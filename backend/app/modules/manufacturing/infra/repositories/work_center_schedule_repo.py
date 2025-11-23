"""
Work Center Schedule Repository Implementation
"""
from typing import Optional, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.manufacturing import WorkCenterSchedule
from app.modules.manufacturing.domain.interfaces import WorkCenterScheduleRepository as WorkCenterScheduleRepositoryProtocol


class WorkCenterScheduleRepository:
    """Repository implementation for WorkCenterSchedule"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, schedule_id: int) -> Optional[WorkCenterSchedule]:
        """Get work center schedule by ID"""
        result = await self.db.execute(
            select(WorkCenterSchedule)
            .options(selectinload(WorkCenterSchedule.work_center))
           .where(WorkCenterSchedule.id == schedule_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_work_center_and_date(self, work_center_id: int, 
                                          schedule_date: date) -> Optional[WorkCenterSchedule]:
        """Get schedule for a work center on a specific date"""
        result = await self.db.execute(
            select(WorkCenterSchedule)
            .where(WorkCenterSchedule.work_center_id == work_center_id)
            .where(WorkCenterSchedule.date == schedule_date)
        )
        return result.scalar_one_or_none()
    
    async def get_by_work_center_date_range(self, work_center_id: int,
                                            start_date: date, end_date: date) -> List[WorkCenterSchedule]:
        """Get schedules for a work center within a date range"""
        result = await self.db.execute(
            select(WorkCenterSchedule)
            .where(WorkCenterSchedule.work_center_id == work_center_id)
            .where(WorkCenterSchedule.date >= start_date)
            .where(WorkCenterSchedule.date <= end_date)
            .order_by(WorkCenterSchedule.date)
        )
        return list(result.scalars().all())
    
    async def create(self, *, work_center_id: int, date: date,
                     available_capacity_minutes: int,
                     scheduled_capacity_minutes: int = 0) -> WorkCenterSchedule:
        """Create a new work center schedule"""
        schedule = WorkCenterSchedule(
            work_center_id=work_center_id,
            date=date,
            available_capacity_minutes=available_capacity_minutes,
            scheduled_capacity_minutes=scheduled_capacity_minutes,
        )
        self.db.add(schedule)
        await self.db.flush()
        await self.db.refresh(schedule)
        return schedule
    
    async def update(self, schedule_id: int, **kwargs) -> Optional[WorkCenterSchedule]:
        """Update work center schedule"""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return None
        
        for key, value in kwargs.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        await self.db.flush()
        await self.db.refresh(schedule)
        return schedule
    
    async def delete(self, schedule_id: int) -> bool:
        """Delete work center schedule"""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return False
        
        await self.db.delete(schedule)
        await self.db.flush()
        return True
