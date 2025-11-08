"""
BOM Item Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.manufacturing import BOMItem
from app.modules.manufacturing.domain.interfaces import BOMItemRepository as BOMItemRepositoryProtocol


class BOMItemRepository:
    """Repository implementation for BOMItem"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, item_id: int) -> Optional[BOMItem]:
        """Get BOM item by ID"""
        result = await self.db.execute(
            select(BOMItem)
            .options(selectinload(BOMItem.component))
            .where(BOMItem.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_bom_id(self, bom_id: int) -> List[BOMItem]:
        """Get all BOM items for a BOM"""
        result = await self.db.execute(
            select(BOMItem)
            .options(selectinload(BOMItem.component))
            .where(BOMItem.bill_of_material_id == bom_id)
        )
        return list(result.scalars().all())
    
    async def create(self, *, bill_of_material_id: int, component_id: Optional[int] = None,
                     quantity: int) -> BOMItem:
        """Create a new BOM item"""
        item = BOMItem(
            bill_of_material_id=bill_of_material_id,
            component_id=component_id,
            quantity=quantity,
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item
    
    async def delete(self, item_id: int) -> bool:
        """Delete BOM item"""
        item = await self.get_by_id(item_id)
        if not item:
            return False
        
        await self.db.delete(item)
        await self.db.flush()
        return True

