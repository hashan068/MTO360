"""
Work Center Service

Business logic for work center management.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from app.models.manufacturing import WorkCenter
from app.modules.manufacturing.domain.interfaces import WorkCenterRepository
from app.modules.manufacturing.infra.repositories.work_center_repo import (
    WorkCenterRepository as WorkCenterRepositoryImpl,
)


class WorkCenterService:
    """Service for work center operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        work_center_repo: Optional[WorkCenterRepository] = None,
    ):
        self.db = db
        self.work_center_repo = work_center_repo or WorkCenterRepositoryImpl(db)
    
    async def get_work_center(self, work_center_id: int) -> Optional[WorkCenter]:
        """Get work center by ID"""
        return await self.work_center_repo.get_by_id(work_center_id)
    
    async def get_work_centers(
        self, skip: int = 0, limit: int = 100, active_only: bool = False
    ) -> List[WorkCenter]:
        """Get all work centers, optionally filtered by active status"""
        return await self.work_center_repo.get_all(skip=skip, limit=limit, active_only=active_only)
    
    async def get_work_center_by_code(self, code: str) -> Optional[WorkCenter]:
        """Get work center by unique code"""
        return await self.work_center_repo.get_by_code(code)
    
    async def create_work_center(
        self,
        name: str,
        code: str,
        capacity_hours_per_day: float,
        description: Optional[str] = None,
        is_active: bool = True,
        location: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> WorkCenter:
        """Create a new work center"""
        # Check if code already exists
        existing = await self.work_center_repo.get_by_code(code)
        if existing:
            raise ValueError(f"Work center with code '{code}' already exists")
        
        work_center = await self.work_center_repo.create(
            name=name,
            code=code,
            capacity_hours_per_day=capacity_hours_per_day,
            description=description,
            is_active=is_active,
            location=location,
            notes=notes,
        )
        await self.db.commit()
        return work_center
    
    async def update_work_center(
        self, work_center_id: int, **updates
    ) -> Optional[WorkCenter]:
        """Update work center"""
        # If code is being updated, check for uniqueness
        if "code" in updates:
            existing = await self.work_center_repo.get_by_code(updates["code"])
            if existing and existing.id != work_center_id:
                raise ValueError(f"Work center with code '{updates['code']}' already exists")
        
        work_center = await self.work_center_repo.update(work_center_id, **updates)
        if work_center:
            await self.db.commit()
        return work_center
    
    async def delete_work_center(self, work_center_id: int) -> bool:
        """Delete work center"""
        success = await self.work_center_repo.delete(work_center_id)
        if success:
            await self.db.commit()
        return success
    
    async def toggle_work_center_status(self, work_center_id: int) -> Optional[WorkCenter]:
        """Toggle work center active status"""
        work_center = await self.work_center_repo.get_by_id(work_center_id)
        if not work_center:
            return None
        
        updated = await self.work_center_repo.update(
            work_center_id, is_active=not work_center.is_active
        )
        if updated:
            await self.db.commit()
        return updated
