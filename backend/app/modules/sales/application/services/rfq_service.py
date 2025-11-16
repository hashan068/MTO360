"""
RFQ Service

Business logic for RFQ management.
"""
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.sales import (
    RFQ,
    RFQItem,
    RFQStatusEnum,
    Quotation,
    QuotationStatusEnum,
)
from app.modules.sales.domain.interfaces import (
    RFQRepository,
    RFQItemRepository,
    QuotationRepository,
    QuotationItemRepository,
)
from app.modules.sales.infra.repositories.rfq_repo import (
    RFQRepository as RFQRepositoryImpl,
)
from app.modules.sales.infra.repositories.rfq_item_repo import (
    RFQItemRepository as RFQItemRepositoryImpl,
)
from app.modules.sales.infra.repositories.quotation_repo import (
    QuotationRepository as QuotationRepositoryImpl,
)
from app.modules.sales.infra.repositories.quotation_item_repo import (
    QuotationItemRepository as QuotationItemRepositoryImpl,
)
from app.modules.sales.infra.repositories.customer_repo import (
    CustomerRepository,
)
from app.modules.sales.domain.exceptions import (
    DocumentNotFoundError,
    InvalidStatusTransitionError,
    ValidationError,
)


class RFQService:
    """Service for RFQ operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        rfq_repo: Optional[RFQRepository] = None,
        rfq_item_repo: Optional[RFQItemRepository] = None,
        quotation_repo: Optional[QuotationRepository] = None,
        quotation_item_repo: Optional[QuotationItemRepository] = None,
        customer_repo: Optional[CustomerRepository] = None,
    ):
        self.db = db
        self.rfq_repo = rfq_repo or RFQRepositoryImpl(db)
        self.rfq_item_repo = rfq_item_repo or RFQItemRepositoryImpl(db)
        self.quotation_repo = quotation_repo or QuotationRepositoryImpl(db)
        self.quotation_item_repo = quotation_item_repo or QuotationItemRepositoryImpl(db)
        self.customer_repo = customer_repo or CustomerRepository(db)
    
    async def get_rfq(self, rfq_id: int) -> Optional[RFQ]:
        """Get RFQ by ID"""
        return await self.rfq_repo.get_by_id(rfq_id)
    
    async def get_rfqs(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[RFQStatusEnum] = None,
        search: Optional[str] = None,
    ) -> List[RFQ]:
        """Get all RFQs with filtering and search"""
        return await self.rfq_repo.get_all(
            skip=skip,
            limit=limit,
            status_filter=status_filter,
            search=search,
        )
    
    async def create_rfq(
        self,
        creator_id: int,
        status: RFQStatusEnum = RFQStatusEnum.DRAFT,
        due_date: Optional[datetime] = None,
        description: Optional[str] = None,
        items: Optional[List[dict]] = None,
    ) -> RFQ:
        """Create a new RFQ with optional items"""
        rfq = await self.rfq_repo.create(
            creator_id=creator_id,
            status=status,
            due_date=due_date,
            description=description,
        )
        
        # Create RFQ items if provided
        if items:
            for item_data in items:
                await self.rfq_item_repo.create(
                    rfq_id=rfq.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                )
        
        await self.db.commit()
        await self.db.refresh(rfq)
        return rfq
    
    async def update_rfq(self, rfq_id: int, **kwargs) -> Optional[RFQ]:
        """Update RFQ with status validation"""
        rfq = await self.rfq_repo.get_by_id(rfq_id)
        if not rfq:
            return None
        
        # Validate status transitions if status is being updated
        if 'status' in kwargs:
            new_status = kwargs['status']
            self._validate_rfq_status_transition(rfq.status, new_status)
        
        # Prevent editing if RFQ is completed or cancelled
        if rfq.status in [RFQStatusEnum.COMPLETED, RFQStatusEnum.CANCELLED]:
            if any(key not in ['status'] for key in kwargs.keys()):
                raise InvalidStatusTransitionError(
                    f"Cannot edit RFQ in {rfq.status.value} status"
                )
        
        rfq = await self.rfq_repo.update(rfq_id, **kwargs)
        if rfq:
            await self.db.commit()
        return rfq
    
    def _validate_rfq_status_transition(
        self,
        current_status: RFQStatusEnum,
        new_status: RFQStatusEnum,
    ) -> None:
        """Validate RFQ status transitions"""
        # Define valid transitions
        valid_transitions = {
            RFQStatusEnum.DRAFT: [RFQStatusEnum.SENT, RFQStatusEnum.CANCELLED],
            RFQStatusEnum.SENT: [RFQStatusEnum.COMPLETED, RFQStatusEnum.CANCELLED],
            RFQStatusEnum.CANCELLED: [],  # Terminal state
            RFQStatusEnum.COMPLETED: [],  # Terminal state
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise InvalidStatusTransitionError(
                f"Cannot transition RFQ from {current_status.value} to {new_status.value}"
            )
    
    async def delete_rfq(self, rfq_id: int) -> bool:
        """Delete RFQ"""
        result = await self.rfq_repo.delete(rfq_id)
        if result:
            await self.db.commit()
        return result
    
    async def convert_to_quotation(
        self,
        rfq_id: int,
        customer_id: int,
        user_id: int,
        quotation_date: date,
        expiration_date: date,
        invoicing_and_shipping_address: str,
    ) -> Quotation:
        """Convert RFQ to Quotation"""
        # Get RFQ with items
        rfq = await self.rfq_repo.get_by_id(rfq_id)
        if not rfq:
            raise DocumentNotFoundError(f"RFQ with id {rfq_id} not found")
        
        # Validate RFQ status
        if rfq.status != RFQStatusEnum.SENT:
            raise InvalidStatusTransitionError(
                f"Can only convert RFQ with status 'sent', current status is '{rfq.status.value}'"
            )
        
        # Validate RFQ has items
        if not rfq.items:
            raise ValidationError("RFQ must have at least one item to convert to quotation")
        
        # Validate customer exists and is active
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise ValidationError(f"Customer with id {customer_id} not found")
        if not customer.is_active:
            raise ValidationError(f"Customer {customer.name} is not active")
        
        # Validate dates
        if expiration_date <= quotation_date:
            raise ValidationError("Expiration date must be after quotation date")
        
        # Calculate total amount
        total_amount = sum(
            Decimal(str(item.unit_price)) * item.quantity
            for item in rfq.items
        )
        
        # Create quotation
        quotation = await self.quotation_repo.create(
            customer_id=customer_id,
            date=quotation_date,
            expiration_date=expiration_date,
            invoicing_and_shipping_address=invoicing_and_shipping_address,
            total_amount=float(total_amount),
            status=QuotationStatusEnum.QUOTATION,
            created_by_id=user_id,
        )
        
        # Update quotation with rfq_id
        await self.quotation_repo.update(quotation.id, rfq_id=rfq_id)
        
        # Create quotation items from RFQ items
        for rfq_item in rfq.items:
            await self.quotation_item_repo.create(
                quotation_id=quotation.id,
                product_id=rfq_item.product_id,
                quantity=rfq_item.quantity,
                unit_price=float(rfq_item.unit_price),
            )
        
        # Update RFQ status to completed
        await self.rfq_repo.update(rfq_id, status=RFQStatusEnum.COMPLETED)
        
        await self.db.commit()
        await self.db.refresh(quotation)
        return quotation
    
    async def get_rfq_quotations(self, rfq_id: int) -> List[Quotation]:
        """Get all quotations created from this RFQ"""
        rfq = await self.rfq_repo.get_by_id(rfq_id)
        if not rfq:
            raise DocumentNotFoundError(f"RFQ with id {rfq_id} not found")
        
        return rfq.quotations

