"""
Quotation Item Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.models.sales import QuotationItem
from app.modules.sales.domain.interfaces import QuotationItemRepository as QuotationItemRepositoryProtocol


class QuotationItemRepository:
    """Repository implementation for QuotationItem"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, item_id: int) -> Optional[QuotationItem]:
        """Get quotation item by ID"""
        result = await self.db.execute(
            select(QuotationItem)
            .options(selectinload(QuotationItem.product))
            .where(QuotationItem.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_quotation_id(self, quotation_id: int) -> List[QuotationItem]:
        """Get all quotation items for a quotation"""
        result = await self.db.execute(
            select(QuotationItem)
            .options(selectinload(QuotationItem.product))
            .where(QuotationItem.quotation_id == quotation_id)
        )
        return list(result.scalars().all())
    
    async def create(self, *, quotation_id: int, product_id: int, quantity: int, unit_price: float) -> QuotationItem:
        """Create a new quotation item"""
        item = QuotationItem(
            quotation_id=quotation_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=Decimal(str(unit_price)),
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item
    
    async def delete(self, item_id: int) -> bool:
        """Delete quotation item"""
        item = await self.get_by_id(item_id)
        if not item:
            return False
        
        await self.db.delete(item)
        await self.db.flush()
        return True

