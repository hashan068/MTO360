"""
Sales Order Item Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.models.sales import SalesOrderItem
from app.modules.sales.domain.interfaces import SalesOrderItemRepository as SalesOrderItemRepositoryProtocol


class SalesOrderItemRepository:
    """Repository implementation for SalesOrderItem"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, item_id: int) -> Optional[SalesOrderItem]:
        """Get sales order item by ID"""
        result = await self.db.execute(
            select(SalesOrderItem)
            .options(selectinload(SalesOrderItem.product))
            .where(SalesOrderItem.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_order_id(self, order_id: int) -> List[SalesOrderItem]:
        """Get all sales order items for an order"""
        result = await self.db.execute(
            select(SalesOrderItem)
            .options(selectinload(SalesOrderItem.product))
            .where(SalesOrderItem.order_id == order_id)
        )
        return list(result.scalars().all())
    
    async def create(self, *, order_id: int, product_id: int, quantity: int, price: float) -> SalesOrderItem:
        """Create a new sales order item"""
        item = SalesOrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=Decimal(str(price)),
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item
    
    async def delete(self, item_id: int) -> bool:
        """Delete sales order item"""
        item = await self.get_by_id(item_id)
        if not item:
            return False
        
        await self.db.delete(item)
        await self.db.flush()
        return True

