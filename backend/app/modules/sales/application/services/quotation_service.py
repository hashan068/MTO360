"""
Quotation Service

Business logic for quotation management.
"""
from typing import Optional, List
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.sales import (
    Quotation,
    QuotationItem,
    QuotationStatusEnum,
    SalesOrder,
    SalesOrderStatusEnum,
)
from app.modules.sales.domain.interfaces import (
    QuotationRepository,
    QuotationItemRepository,
    SalesOrderRepository,
    SalesOrderItemRepository,
)
from app.modules.sales.infra.repositories.quotation_repo import (
    QuotationRepository as QuotationRepositoryImpl,
)
from app.modules.sales.infra.repositories.quotation_item_repo import (
    QuotationItemRepository as QuotationItemRepositoryImpl,
)
from app.modules.sales.infra.repositories.sales_order_repo import (
    SalesOrderRepository as SalesOrderRepositoryImpl,
)
from app.modules.sales.infra.repositories.sales_order_item_repo import (
    SalesOrderItemRepository as SalesOrderItemRepositoryImpl,
)
from app.modules.sales.infra.repositories.customer_repo import (
    CustomerRepository,
)
from app.modules.sales.domain.exceptions import (
    DocumentNotFoundError,
    InvalidStatusTransitionError,
    DocumentLockedException,
    DuplicateConversionError,
    ValidationError,
)


class QuotationService:
    """Service for quotation operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        quotation_repo: Optional[QuotationRepository] = None,
        quotation_item_repo: Optional[QuotationItemRepository] = None,
        sales_order_repo: Optional[SalesOrderRepository] = None,
        sales_order_item_repo: Optional[SalesOrderItemRepository] = None,
        customer_repo: Optional[CustomerRepository] = None,
    ):
        self.db = db
        self.quotation_repo = quotation_repo or QuotationRepositoryImpl(db)
        self.quotation_item_repo = quotation_item_repo or QuotationItemRepositoryImpl(db)
        self.sales_order_repo = sales_order_repo or SalesOrderRepositoryImpl(db)
        self.sales_order_item_repo = sales_order_item_repo or SalesOrderItemRepositoryImpl(db)
        self.customer_repo = customer_repo or CustomerRepository(db)
    
    async def get_quotation(self, quotation_id: int) -> Optional[Quotation]:
        """Get quotation by ID"""
        return await self.quotation_repo.get_by_id(quotation_id)
    
    async def get_quotations(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[QuotationStatusEnum] = None,
        search: Optional[str] = None,
    ) -> List[Quotation]:
        """Get all quotations with filtering and search"""
        return await self.quotation_repo.get_all(
            skip=skip,
            limit=limit,
            status_filter=status_filter,
            search=search,
        )
    
    async def create_quotation(
        self,
        customer_id: int,
        date: date,
        expiration_date: date,
        invoicing_and_shipping_address: str,
        quotation_items: List[dict],
        created_by_id: int,
        status: QuotationStatusEnum = QuotationStatusEnum.QUOTATION,
    ) -> Quotation:
        """Create a new quotation with items"""
        # Validate customer exists and is active
        customer = await self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise ValidationError(f"Customer with id {customer_id} not found")
        if not customer.is_active:
            raise ValidationError(f"Customer {customer.name} is not active")
        
        # Validate dates
        if expiration_date <= date:
            raise ValidationError("Expiration date must be after quotation date")
        
        # Validate items
        if not quotation_items or len(quotation_items) == 0:
            raise ValidationError("At least one quotation item is required")
        
        # Calculate total amount
        total_amount = sum(
            Decimal(str(item['unit_price'])) * item['quantity']
            for item in quotation_items
        )
        
        # Create quotation
        quotation = await self.quotation_repo.create(
            customer_id=customer_id,
            date=date,
            expiration_date=expiration_date,
            invoicing_and_shipping_address=invoicing_and_shipping_address,
            total_amount=float(total_amount),
            status=status,
            created_by_id=created_by_id,
        )
        
        # Create quotation items
        for item_data in quotation_items:
            await self.quotation_item_repo.create(
                quotation_id=quotation.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
            )
        
        await self.db.commit()
        await self.db.refresh(quotation)
        return quotation
    
    async def update_quotation(self, quotation_id: int, **kwargs) -> Optional[Quotation]:
        """Update quotation with edit permission check"""
        quotation = await self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            return None
        
        # Check if quotation can be edited
        if not self.can_edit(quotation):
            raise DocumentLockedException(
                f"Cannot edit quotation in {quotation.status.value} status"
            )
        
        quotation = await self.quotation_repo.update(quotation_id, **kwargs)
        if quotation:
            await self.db.commit()
        return quotation
    
    async def delete_quotation(self, quotation_id: int) -> bool:
        """Delete quotation"""
        result = await self.quotation_repo.delete(quotation_id)
        if result:
            await self.db.commit()
        return result
    
    async def delete_quotation_item(self, item_id: int) -> bool:
        """Delete quotation item"""
        result = await self.quotation_item_repo.delete(item_id)
        if result:
            await self.db.commit()
        return result
    
    async def update_quotation_status(
        self,
        quotation_id: int,
        new_status: QuotationStatusEnum,
        user_id: int,
    ) -> Optional[Quotation]:
        """Update quotation status with validation"""
        quotation = await self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise DocumentNotFoundError(f"Quotation with id {quotation_id} not found")
        
        # Validate status transition
        self._validate_quotation_status_transition(quotation.status, new_status)
        
        # Update status
        quotation = await self.quotation_repo.update(quotation_id, status=new_status)
        await self.db.commit()
        return quotation
    
    def _validate_quotation_status_transition(
        self,
        current_status: QuotationStatusEnum,
        new_status: QuotationStatusEnum,
    ) -> None:
        """Validate quotation status transitions"""
        # Define valid transitions
        valid_transitions = {
            QuotationStatusEnum.QUOTATION: [
                QuotationStatusEnum.QUOTATION_SENT,
                QuotationStatusEnum.CANCELLED,
                QuotationStatusEnum.EXPIRED,
            ],
            QuotationStatusEnum.QUOTATION_SENT: [
                QuotationStatusEnum.ACCEPTED,
                QuotationStatusEnum.REJECTED,
                QuotationStatusEnum.CANCELLED,
                QuotationStatusEnum.EXPIRED,
            ],
            QuotationStatusEnum.ACCEPTED: [],  # Terminal state
            QuotationStatusEnum.REJECTED: [],  # Terminal state
            QuotationStatusEnum.CANCELLED: [],  # Terminal state
            QuotationStatusEnum.EXPIRED: [],  # Terminal state
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise InvalidStatusTransitionError(
                f"Cannot transition quotation from {current_status.value} to {new_status.value}"
            )
    
    def check_expiration(self, quotation: Quotation) -> bool:
        """Check if quotation is expired"""
        today = date.today()
        return (
            quotation.expiration_date < today
            and quotation.status in [
                QuotationStatusEnum.QUOTATION,
                QuotationStatusEnum.QUOTATION_SENT,
            ]
        )
    
    def can_edit(self, quotation: Quotation) -> bool:
        """Check if quotation can be edited based on status"""
        # Cannot edit after accepted, rejected, cancelled, or expired
        locked_statuses = [
            QuotationStatusEnum.ACCEPTED,
            QuotationStatusEnum.REJECTED,
            QuotationStatusEnum.CANCELLED,
            QuotationStatusEnum.EXPIRED,
        ]
        return quotation.status not in locked_statuses
    
    async def convert_to_sales_order(
        self,
        quotation_id: int,
        user_id: int,
    ) -> SalesOrder:
        """Convert quotation to sales order"""
        # Get quotation with items
        quotation = await self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise DocumentNotFoundError(f"Quotation with id {quotation_id} not found")
        
        # Validate quotation status
        if quotation.status != QuotationStatusEnum.ACCEPTED:
            raise InvalidStatusTransitionError(
                f"Can only convert quotation with status 'accepted', current status is '{quotation.status.value}'"
            )
        
        # Check for duplicate conversion
        if quotation.sales_orders:
            raise DuplicateConversionError(
                f"Quotation {quotation_id} has already been converted to a sales order"
            )
        
        # Validate quotation has items
        if not quotation.quotation_items:
            raise ValidationError("Quotation must have at least one item to convert to sales order")
        
        # Calculate total amount
        total_amount = sum(
            Decimal(str(item.unit_price)) * item.quantity
            for item in quotation.quotation_items
        )
        
        # Create sales order
        sales_order = await self.sales_order_repo.create(
            customer_id=quotation.customer_id,
            total_amount=float(total_amount),
            status=SalesOrderStatusEnum.PENDING,
        )
        
        # Update sales order with quotation_id
        await self.sales_order_repo.update(sales_order.id, quotation_id=quotation_id)
        
        # Create sales order items from quotation items
        for quotation_item in quotation.quotation_items:
            await self.sales_order_item_repo.create(
                order_id=sales_order.id,
                product_id=quotation_item.product_id,
                quantity=quotation_item.quantity,
                price=float(quotation_item.unit_price),
            )
        
        await self.db.commit()
        await self.db.refresh(sales_order)
        return sales_order
    
    async def send_email(
        self,
        quotation_id: int,
        user_id: int,
    ) -> Quotation:
        """Send quotation email and track sending history"""
        from sqlalchemy import select
        from app.models.user import User
        
        # Get quotation
        quotation = await self.quotation_repo.get_by_id(quotation_id)
        if not quotation:
            raise DocumentNotFoundError(f"Quotation with id {quotation_id} not found")
        
        # Validate customer has email
        customer = await self.customer_repo.get_by_id(quotation.customer_id)
        if not customer or not customer.email:
            raise ValidationError("Customer email is required to send quotation")
        
        # Get user who is sending the email
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        username = user.username if user else f"User {user_id}"
        
        # TODO: Implement actual email sending logic here
        # For now, we'll just track the email as sent
        
        # Update email tracking
        now = datetime.now()
        email_sent_count = (quotation.email_sent_count or 0) + 1
        
        # Build email history
        history = quotation.email_history if quotation.email_history else []
        if not isinstance(history, list):
            history = []
        
        history.append({
            "sent_at": now.isoformat(),
            "sent_by_user_id": user_id,
            "sent_by_username": username,
            "recipient": customer.email,
            "count": email_sent_count,
        })
        
        # Update quotation
        quotation = await self.quotation_repo.update(
            quotation_id,
            email_sent_at=now,
            email_sent_count=email_sent_count,
            email_history=history,
            status=QuotationStatusEnum.QUOTATION_SENT if quotation.status == QuotationStatusEnum.QUOTATION else quotation.status,
        )
        
        await self.db.commit()
        await self.db.refresh(quotation)
        return quotation

