"""
RFQ Item Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.models.sales import RFQItem
from app.modules.sales.domain.interfaces import RFQItemRepository as RFQItemRepositoryProtocol


class RFQItemRepository:
    """Repository implementation for RFQItem"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, item_id: int) -> Optional[RFQItem]:
        """Get RFQ item by ID"""
        result = await self.db.execute(
            select(RFQItem)
            .options(selectinload(RFQItem.product))
            .where(RFQItem.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_rfq_id(self, rfq_id: int) -> List[RFQItem]:
        """Get all RFQ items for an RFQ"""
        result = await self.db.execute(
            select(RFQItem)
            .options(selectinload(RFQItem.product))
            .where(RFQItem.rfq_id == rfq_id)
        )
        return list(result.scalars().all())
    
    async def create(self, *, rfq_id: int, product_id: int, quantity: int, unit_price: float) -> RFQItem:
        """Create a new RFQ item"""
        item = RFQItem(
            rfq_id=rfq_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=Decimal(str(unit_price)),
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item
    
    async def delete(self, item_id: int) -> bool:
        """Delete RFQ item"""
        item = await self.get_by_id(item_id)
        if not item:
            return False
        
        await self.db.delete(item)
        await self.db.flush()
        return True

