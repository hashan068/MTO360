"""
Material Requisition Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.manufacturing import MaterialRequisition, MaterialRequisitionStatusEnum
from app.modules.manufacturing.domain.interfaces import MaterialRequisitionRepository as MaterialRequisitionRepositoryProtocol


class MaterialRequisitionRepository:
    """Repository implementation for MaterialRequisition"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, requisition_id: int) -> Optional[MaterialRequisition]:
        """Get material requisition by ID"""
        from app.models.manufacturing import MaterialRequisitionItem
        
        result = await self.db.execute(
            select(MaterialRequisition)
            .options(
                selectinload(MaterialRequisition.manufacturing_order),
                selectinload(MaterialRequisition.items).selectinload(MaterialRequisitionItem.component)
            )
            .where(MaterialRequisition.id == requisition_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[MaterialRequisition]:
        """Get all material requisitions with pagination"""
        from app.models.manufacturing import MaterialRequisitionItem
        
        result = await self.db.execute(
            select(MaterialRequisition)
            .options(
                selectinload(MaterialRequisition.manufacturing_order),
                selectinload(MaterialRequisition.items).selectinload(MaterialRequisitionItem.component)
            )
            .offset(skip)
            .limit(limit)
            .order_by(MaterialRequisition.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, manufacturing_order_id: int, bom_id: Optional[int] = None,
                     status: MaterialRequisitionStatusEnum = MaterialRequisitionStatusEnum.PENDING) -> MaterialRequisition:
        """Create a new material requisition"""
        requisition = MaterialRequisition(
            manufacturing_order_id=manufacturing_order_id,
            bom_id=bom_id,
            status=status,
        )
        self.db.add(requisition)
        await self.db.flush()
        await self.db.refresh(requisition)
        return requisition
    
    async def update(self, requisition_id: int, **kwargs) -> Optional[MaterialRequisition]:
        """Update material requisition"""
        requisition = await self.get_by_id(requisition_id)
        if not requisition:
            return None
        
        for key, value in kwargs.items():
            if hasattr(requisition, key):
                setattr(requisition, key, value)
        
        await self.db.flush()
        await self.db.refresh(requisition)
        return requisition
    
    async def delete(self, requisition_id: int) -> bool:
        """Delete material requisition"""
        requisition = await self.get_by_id(requisition_id)
        if not requisition:
            return False
        
        await self.db.delete(requisition)
        await self.db.flush()
        return True

