"""
Work Center Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.manufacturing import WorkCenter
from app.modules.manufacturing.domain.interfaces import WorkCenterRepository as WorkCenterRepositoryProtocol


class WorkCenterRepository:
    """Repository implementation for WorkCenter"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, work_center_id: int) -> Optional[WorkCenter]:
        """Get work center by ID"""
        result = await self.db.execute(
            select(WorkCenter).where(WorkCenter.id == work_center_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[WorkCenter]:
        """Get all work centers with pagination"""
        query = select(WorkCenter)
        
        if active_only:
            query = query.where(WorkCenter.is_active == True)
        
        query = query.offset(skip).limit(limit).order_by(WorkCenter.code)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_code(self, code: str) -> Optional[WorkCenter]:
        """Get work center by unique code"""
        result = await self.db.execute(
            select(WorkCenter).where(WorkCenter.code == code)
        )
        return result.scalar_one_or_none()
    
    async def create(self, *, name: str, code: str, capacity_hours_per_day: float,
                     description: Optional[str] = None, is_active: bool = True,
                     location: Optional[str] = None, notes: Optional[str] = None) -> WorkCenter:
        """Create a new work center"""
        work_center = WorkCenter(
            name=name,
            code=code,
            capacity_hours_per_day=capacity_hours_per_day,
            description=description,
            is_active=is_active,
            location=location,
            notes=notes,
        )
        self.db.add(work_center)
        await self.db.flush()
        await self.db.refresh(work_center)
        with open("repo_debug.txt", "w") as f:
            f.write(f"REPO DEBUG: Created WC id={work_center.id}, name={work_center.name}, code={work_center.code}, type(code)={type(work_center.code)}")
        return work_center
    
    async def update(self, work_center_id: int, **kwargs) -> Optional[WorkCenter]:
        """Update work center"""
        work_center = await self.get_by_id(work_center_id)
        if not work_center:
            return None
        
        for key, value in kwargs.items():
            if hasattr(work_center, key):
                setattr(work_center, key, value)
        
        await self.db.flush()
        await self.db.refresh(work_center)
        return work_center
    
    async def delete(self, work_center_id: int) -> bool:
        """Delete work center"""
        work_center = await self.get_by_id(work_center_id)
        if not work_center:
            return False
        
        await self.db.delete(work_center)
        await self.db.flush()
        return True
