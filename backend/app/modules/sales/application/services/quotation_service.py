"""
Quotation Service

Business logic for quotation management.
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.sales import Quotation, QuotationItem, QuotationStatusEnum
from app.modules.sales.domain.interfaces import (
    QuotationRepository,
    QuotationItemRepository,
)
from app.modules.sales.infra.repositories.quotation_repo import (
    QuotationRepository as QuotationRepositoryImpl,
)
from app.modules.sales.infra.repositories.quotation_item_repo import (
    QuotationItemRepository as QuotationItemRepositoryImpl,
)


class QuotationService:
    """Service for quotation operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        quotation_repo: Optional[QuotationRepository] = None,
        quotation_item_repo: Optional[QuotationItemRepository] = None,
    ):
        self.db = db
        self.quotation_repo = quotation_repo or QuotationRepositoryImpl(db)
        self.quotation_item_repo = quotation_item_repo or QuotationItemRepositoryImpl(db)
    
    async def get_quotation(self, quotation_id: int) -> Optional[Quotation]:
        """Get quotation by ID"""
        return await self.quotation_repo.get_by_id(quotation_id)
    
    async def get_quotations(self, skip: int = 0, limit: int = 100) -> List[Quotation]:
        """Get all quotations"""
        return await self.quotation_repo.get_all(skip=skip, limit=limit)
    
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
        """Update quotation"""
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

