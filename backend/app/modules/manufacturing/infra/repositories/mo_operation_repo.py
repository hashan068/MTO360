"""
Manufacturing Order Operation Repository Implementation
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.manufacturing import ManufacturingOrderOperation, OperationStatusEnum
from app.modules.manufacturing.domain.interfaces import ManufacturingOrderOperationRepository as ManufacturingOrderOperationRepositoryProtocol


class ManufacturingOrderOperationRepository:
    """Repository implementation for ManufacturingOrderOperation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, operation_id: int) -> Optional[ManufacturingOrderOperation]:
        """Get MO operation by ID"""
        result = await self.db.execute(
            select(ManufacturingOrderOperation)
            .options(
                selectinload(ManufacturingOrderOperation.work_center),
                selectinload(ManufacturingOrderOperation.manufacturing_order)
            )
            .where(ManufacturingOrderOperation.id == operation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_mo_id(self, mo_id: int) -> List[ManufacturingOrderOperation]:
        """Get all operations for a manufacturing order, ordered by sequence"""
        result = await self.db.execute(
            select(ManufacturingOrderOperation)
            .options(selectinload(ManufacturingOrderOperation.work_center))
            .where(ManufacturingOrderOperation.manufacturing_order_id == mo_id)
            .order_by(ManufacturingOrderOperation.sequence)
        )
        return list(result.scalars().all())
    
    async def get_by_work_center_id(self, work_center_id: int, 
                                     status: Optional[OperationStatusEnum] = None) -> List[ManufacturingOrderOperation]:
        """Get operations by work center, optionally filtered by status"""
        query = select(ManufacturingOrderOperation).where(
            ManufacturingOrderOperation.work_center_id == work_center_id
        )
        
        if status:
            query = query.where(ManufacturingOrderOperation.status == status)
        
        query = query.order_by(ManufacturingOrderOperation.scheduled_start)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_operator_id(self, operator_id: int,
                                  status: Optional[OperationStatusEnum] = None) -> List[ManufacturingOrderOperation]:
        """Get operations assigned to an operator"""
        query = select(ManufacturingOrderOperation).where(
            ManufacturingOrderOperation.assigned_operator_id == operator_id
        )
        
        if status:
            query = query.where(ManufacturingOrderOperation.status == status)
        
        query = query.order_by(ManufacturingOrderOperation.scheduled_start)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_scheduled_between(self, work_center_id: int, start_date: datetime,
                                     end_date: datetime) -> List[ManufacturingOrderOperation]:
        """Get operations scheduled within a date range for a work center"""
        result = await self.db.execute(
            select(ManufacturingOrderOperation)
            .where(ManufacturingOrderOperation.work_center_id == work_center_id)
            .where(ManufacturingOrderOperation.scheduled_start >= start_date)
            .where(ManufacturingOrderOperation.scheduled_start <= end_date)
            .order_by(ManufacturingOrderOperation.scheduled_start)
        )
        return list(result.scalars().all())
    
    async def create(self, *, manufacturing_order_id: int, sequence: int, name: str,
                     work_center_id: int, scheduled_duration_minutes: int,
                     route_operation_id: Optional[int] = None,
                     scheduled_start: Optional[datetime] = None,
                     scheduled_end: Optional[datetime] = None,
                     status: OperationStatusEnum = OperationStatusEnum.PENDING) -> ManufacturingOrderOperation:
        """Create a new MO operation"""
        operation = ManufacturingOrderOperation(
            manufacturing_order_id=manufacturing_order_id,
            route_operation_id=route_operation_id,
            sequence=sequence,
            name=name,
            work_center_id=work_center_id,
            scheduled_duration_minutes=scheduled_duration_minutes,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            status=status,
        )
        self.db.add(operation)
        await self.db.flush()
        await self.db.refresh(operation)
        return operation
    
    async def update(self, operation_id: int, **kwargs) -> Optional[ManufacturingOrderOperation]:
        """Update MO operation"""
        operation = await self.get_by_id(operation_id)
        if not operation:
            return None
        
        for key, value in kwargs.items():
            if hasattr(operation, key):
                setattr(operation, key, value)
        
        await self.db.flush()
        await self.db.refresh(operation)
        return operation
    
    async def delete(self, operation_id: int) -> bool:
        """Delete MO operation"""
        operation = await self.get_by_id(operation_id)
        if not operation:
            return False
        
        await self.db.delete(operation)
        await self.db.flush()
        return True
