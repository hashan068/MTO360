"""
Work Centers API Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.work_centers import (
    WorkCenterCreate,
    WorkCenterUpdate,
    TestResponse as WorkCenterResponse,
)
from app.modules.manufacturing.application.services.work_center_service import WorkCenterService
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TestResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    capacity_hours_per_day: float
    is_active: bool
    location: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TestResponse(BaseModel):
    id: int
    name: str
    code: str
    capacity_hours_per_day: float
    is_active: bool
    description: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

router = APIRouter(prefix="/api/manufacturing/work-centers", tags=["Work Centers"])


@router.get("/", response_model=List[WorkCenterResponse])
async def list_work_centers(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get all work centers"""
    service = WorkCenterService(db)
    work_centers = await service.get_work_centers(skip=skip, limit=limit, active_only=active_only)
    return work_centers


@router.get("/{work_center_id}", response_model=WorkCenterResponse)
async def get_work_center(
    work_center_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get work center by ID"""
    service = WorkCenterService(db)
    work_center = await service.get_work_center(work_center_id)
    if not work_center:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Work center {work_center_id} not found"
        )
    return work_center


@router.post("/", response_model=WorkCenterResponse, status_code=http_status.HTTP_201_CREATED)
async def create_work_center(
    data: WorkCenterCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new work center"""
    service = WorkCenterService(db)
    try:
        work_center = await service.create_work_center(
            name=data.name,
            code=data.code,
            capacity_hours_per_day=data.capacity_hours_per_day,
            description=data.description,
            is_active=data.is_active,
            location=data.location,
            notes=data.notes,
        )
        encoded_wc = jsonable_encoder(work_center)
        with open("router_debug.txt", "w") as f:
            import json
            f.write(f"ENCODED: {json.dumps(encoded_wc, default=str)}")
        return encoded_wc
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        with open("router_error.txt", "w") as f:
            import traceback
            traceback.print_exc(file=f)
        raise e


@router.patch("/{work_center_id}", response_model=WorkCenterResponse)
async def update_work_center(
    work_center_id: int,
    data: WorkCenterUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update work center"""
    service = WorkCenterService(db)
    
    # Only include non-None fields
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    
    try:
        work_center = await service.update_work_center(work_center_id, **updates)
        if not work_center:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Work center {work_center_id} not found"
            )
        return work_center
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{work_center_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_work_center(
    work_center_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete work center"""
    service = WorkCenterService(db)
    success = await service.delete_work_center(work_center_id)
    if not success:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Work center {work_center_id} not found"
        )


@router.patch("/{work_center_id}/toggle-status", response_model=WorkCenterResponse)
async def toggle_work_center_status(
    work_center_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Toggle work center active status"""
    service = WorkCenterService(db)
    work_center = await service.toggle_work_center_status(work_center_id)
    if not work_center:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Work center {work_center_id} not found"
        )
    return work_center
