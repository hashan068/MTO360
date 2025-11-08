"""
Purchase Requisition Repository Implementation
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.inventory import PurchaseRequisition, StatusEnum, PriorityEnum
from app.modules.inventory.domain.interfaces import PurchaseRequisitionRepository as PurchaseRequisitionRepositoryProtocol


class PurchaseRequisitionRepository:
    """Repository implementation for PurchaseRequisition"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, requisition_id: int) -> Optional[PurchaseRequisition]:
        """Get purchase requisition by ID"""
        result = await self.db.execute(
            select(PurchaseRequisition)
            .options(selectinload(PurchaseRequisition.component))
            .where(PurchaseRequisition.id == requisition_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[PurchaseRequisition]:
        """Get all purchase requisitions with pagination"""
        result = await self.db.execute(
            select(PurchaseRequisition)
            .options(selectinload(PurchaseRequisition.component))
            .offset(skip)
            .limit(limit)
            .order_by(PurchaseRequisition.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def create(self, *, user_id: Optional[int], component_id: int, quantity: int,
                     status: StatusEnum = StatusEnum.PENDING, notes: Optional[str] = None,
                     expected_delivery_date: Optional[datetime] = None,
                     priority: PriorityEnum = PriorityEnum.HIGH) -> PurchaseRequisition:
        """Create a new purchase requisition"""
        requisition = PurchaseRequisition(
            user_id=user_id,
            component_id=component_id,
            quantity=quantity,
            status=status,
            notes=notes,
            expected_delivery_date=expected_delivery_date,
            priority=priority,
        )
        self.db.add(requisition)
        await self.db.flush()
        await self.db.refresh(requisition)
        return requisition
    
    async def update(self, requisition_id: int, **kwargs) -> Optional[PurchaseRequisition]:
        """Update purchase requisition"""
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
        """Delete purchase requisition"""
        requisition = await self.get_by_id(requisition_id)
        if not requisition:
            return False
        
        await self.db.delete(requisition)
        await self.db.flush()
        return True

