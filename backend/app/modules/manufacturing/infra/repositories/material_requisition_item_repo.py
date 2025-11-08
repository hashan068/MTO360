"""
Material Requisition Item Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.manufacturing import MaterialRequisitionItem, MaterialRequisitionItemStatusEnum
from app.modules.manufacturing.domain.interfaces import MaterialRequisitionItemRepository as MaterialRequisitionItemRepositoryProtocol


class MaterialRequisitionItemRepository:
    """Repository implementation for MaterialRequisitionItem"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, item_id: int) -> Optional[MaterialRequisitionItem]:
        """Get material requisition item by ID"""
        result = await self.db.execute(
            select(MaterialRequisitionItem)
            .options(selectinload(MaterialRequisitionItem.component))
            .where(MaterialRequisitionItem.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_requisition_id(self, requisition_id: int) -> List[MaterialRequisitionItem]:
        """Get all material requisition items for a requisition"""
        result = await self.db.execute(
            select(MaterialRequisitionItem)
            .options(selectinload(MaterialRequisitionItem.component))
            .where(MaterialRequisitionItem.material_requisition_id == requisition_id)
        )
        return list(result.scalars().all())
    
    async def create(self, *, material_requisition_id: int, component_id: int,
                     quantity: int, status: MaterialRequisitionItemStatusEnum = MaterialRequisitionItemStatusEnum.PENDING) -> MaterialRequisitionItem:
        """Create a new material requisition item"""
        item = MaterialRequisitionItem(
            material_requisition_id=material_requisition_id,
            component_id=component_id,
            quantity=quantity,
            status=status,
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item
    
    async def update(self, item_id: int, **kwargs) -> Optional[MaterialRequisitionItem]:
        """Update material requisition item"""
        item = await self.get_by_id(item_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        await self.db.flush()
        await self.db.refresh(item)
        return item
    
    async def delete(self, item_id: int) -> bool:
        """Delete material requisition item"""
        item = await self.get_by_id(item_id)
        if not item:
            return False
        
        await self.db.delete(item)
        await self.db.flush()
        return True

