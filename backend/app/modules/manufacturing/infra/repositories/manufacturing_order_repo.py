"""
Manufacturing Order Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.manufacturing import ManufacturingOrder, ManufacturingOrderStatusEnum
from app.modules.manufacturing.domain.interfaces import ManufacturingOrderRepository as ManufacturingOrderRepositoryProtocol


class ManufacturingOrderRepository:
    """Repository implementation for ManufacturingOrder"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, order_id: int) -> Optional[ManufacturingOrder]:
        """Get manufacturing order by ID"""
        result = await self.db.execute(
            select(ManufacturingOrder)
            .options(
                selectinload(ManufacturingOrder.product),
                selectinload(ManufacturingOrder.bom),
                selectinload(ManufacturingOrder.sales_order_item)
            )
            .where(ManufacturingOrder.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ManufacturingOrder]:
        """Get all manufacturing orders with pagination"""
        result = await self.db.execute(
            select(ManufacturingOrder)
            .options(selectinload(ManufacturingOrder.product))
            .offset(skip)
            .limit(limit)
            .order_by(ManufacturingOrder.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, sales_order_item_id: Optional[int] = None,
                     product_id: Optional[int] = None, quantity: int = 1,
                     bom_id: Optional[int] = None,
                     status: ManufacturingOrderStatusEnum = ManufacturingOrderStatusEnum.PENDING,
                     creator_id: Optional[int] = None) -> ManufacturingOrder:
        """Create a new manufacturing order"""
        order = ManufacturingOrder(
            sales_order_item_id=sales_order_item_id,
            product_id=product_id,
            quantity=quantity,
            bom_id=bom_id,
            status=status,
            creator_id=creator_id,
        )
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order
    
    async def update(self, order_id: int, **kwargs) -> Optional[ManufacturingOrder]:
        """Update manufacturing order"""
        order = await self.get_by_id(order_id)
        if not order:
            return None
        
        for key, value in kwargs.items():
            if hasattr(order, key):
                setattr(order, key, value)
        
        await self.db.flush()
        await self.db.refresh(order)
        return order
    
    async def delete(self, order_id: int) -> bool:
        """Delete manufacturing order"""
        order = await self.get_by_id(order_id)
        if not order:
            return False
        
        await self.db.delete(order)
        await self.db.flush()
        return True

