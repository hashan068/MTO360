"""
Scheduling API Endpoints
"""
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.middleware.permission_checker import require_permission
from app.schemas.manufacturing import ManufacturingOrderOperationResponse
from app.modules.manufacturing.application.services.scheduling_service import (
    SchedulingService,
)


# Request/Response Schemas
class AutoScheduleRequest(BaseModel):
    """Request to auto-schedule a manufacturing order"""
    mo_id: int


class RescheduleRequest(BaseModel):
    """Request to reschedule an operation"""
    operation_id: int
    new_start_datetime: datetime


class CapacityResponse(BaseModel):
    """Work center capacity information"""
    work_center_id: int
    date: date
    capacity_minutes: float
    scheduled_minutes: float
    available_minutes: float
    utilization_pct: float


class ConflictResponse(BaseModel):
    """Scheduling conflict information"""
    operation_id: int
    operation_name: str
    mo_id: int
    scheduled_start: datetime
    scheduled_end: datetime


router = APIRouter(prefix="/api/manufacturing/schedule", tags=["Scheduling"])


@router.post("/generate-operations/{mo_id}", response_model=List[ManufacturingOrderOperationResponse])
async def generate_operations(
    mo_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_permission("production.schedule.create")),
):
    """
    Generate operations for a manufacturing order from its route template.
    
    This creates ManufacturingOrderOperation records based on the OperationRoute
    associated with the MO's product or BOM.
    """
    service = SchedulingService(db)
    try:
        operations = await service.generate_operations_for_mo(mo_id)
        return operations
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/auto-schedule", status_code=http_status.HTTP_200_OK)
async def auto_schedule_mo(
    request: AutoScheduleRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_permission("production.schedule.create")),
):
    """
    Automatically schedule all operations for a manufacturing order.
    
    Uses forward scheduling algorithm to find available slots for each operation
    in sequence order.
    """
    service = SchedulingService(db)
    try:
        mo = await service.auto_schedule_mo(request.mo_id)
        return {
            "mo_id": mo.id,
            "scheduled_start": mo.scheduled_start,
            "scheduled_end": mo.scheduled_end,
            "total_duration_minutes": mo.total_scheduled_duration_minutes,
            "message": f"Successfully scheduled {len(await service.mo_operation_repo.get_by_mo_id(mo.id))} operations",
        }
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reschedule", response_model=ManufacturingOrderOperationResponse)
async def reschedule_operation(
    request: RescheduleRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_permission("production.schedule.update")),
):
    """
    Reschedule an operation to a new start time.
    
    Validates that no conflicts exist and updates the operation's schedule.
    Does not cascade to dependent operations.
    """
    service = SchedulingService(db)
    try:
        operation = await service.reschedule_operation(
            request.operation_id, request.new_start_datetime
        )
        return operation
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/capacity", response_model=List[CapacityResponse])
async def get_capacity(
    work_center_id: Optional[int] = Query(None, description="Filter by work center"),
    start_date: date = Query(..., description="Start date for capacity query"),
    end_date: date = Query(..., description="End date for capacity query"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get capacity information for work centers over a date range.
    
    Returns capacity, scheduled, available minutes and utilization percentage
    for each day in the range.
    """
    service = SchedulingService(db)
    
    # Validate date range
    if end_date < start_date:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="end_date must be after start_date"
        )
    
    # Limit to reasonable range
    days_diff = (end_date - start_date).days
    if days_diff > 90:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 90 days"
        )
    
    results = []
    
    # Get work centers to query
    if work_center_id:
        work_center_ids = [work_center_id]
    else:
        # Get all active work centers
        work_centers = await service.work_center_repo.get_active_work_centers()
        work_center_ids = [wc.id for wc in work_centers]
    
    # Calculate capacity for each work center and date
    current_date = start_date
    while current_date <= end_date:
        for wc_id in work_center_ids:
            try:
                capacity_info = await service.calculate_work_center_capacity(
                    wc_id, current_date
                )
                results.append(
                    CapacityResponse(
                        work_center_id=wc_id,
                        date=current_date,
                        **capacity_info
                    )
                )
            except ValueError:
                # Skip if work center not found
                continue
        
        current_date += timedelta(days=1)
    
    return results


@router.get("/conflicts", response_model=List[ConflictResponse])
async def detect_conflicts(
    work_center_id: int = Query(..., description="Work center to check"),
    start_datetime: datetime = Query(..., description="Start of time range"),
    end_datetime: datetime = Query(..., description="End of time range"),
    db: AsyncSession = Depends(get_db),
):
    """
    Detect scheduling conflicts in a work center for a given time range.
    
    Returns list of operations that would conflict with the specified time window.
    """
    service = SchedulingService(db)
    
    try:
        conflicts = await service.detect_scheduling_conflicts(
            work_center_id, start_datetime, end_datetime
        )
        
        return [
            ConflictResponse(
                operation_id=op.id,
                operation_name=op.name,
                mo_id=op.manufacturing_order_id,
                scheduled_start=op.scheduled_start,
                scheduled_end=op.scheduled_end,
            )
            for op in conflicts
        ]
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))


# Import timedelta for capacity endpoint
from datetime import timedelta
from sqlalchemy import select, and_
from app.models.manufacturing import ManufacturingOrderOperation, OperationStatusEnum


@router.get("/operations", response_model=List[ManufacturingOrderOperationResponse])
async def get_all_operations(
    start_date: Optional[datetime] = Query(None, description="Filter operations starting after this datetime"),
    end_date: Optional[datetime] = Query(None, description="Filter operations ending before this datetime"),
    work_center_id: Optional[int] = Query(None, description="Filter by work center"),
    status: Optional[str] = Query(None, description="Filter by status (comma-separated)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all manufacturing order operations with optional filters.
    
    Used by the scheduler to display operations in the timeline.
    Returns operations that overlap with the specified date range.
    """
    # Build query
    query = select(ManufacturingOrderOperation)
    filters = []
    
    # Date range filtering
    if start_date:
        # Include operations that end after the start date
        filters.append(ManufacturingOrderOperation.scheduled_end >= start_date)
    
    if end_date:
        # Include operations that start before the end date
        filters.append(ManufacturingOrderOperation.scheduled_start <= end_date)
    
    # Work center filtering
    if work_center_id:
        filters.append(ManufacturingOrderOperation.work_center_id == work_center_id)
    
    # Status filtering
    if status:
        status_list = [s.strip() for s in status.split(',')]
        try:
            status_enums = [OperationStatusEnum(s) for s in status_list]
            filters.append(ManufacturingOrderOperation.status.in_(status_enums))
        except ValueError as e:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status value: {e}"
            )
    
    # Only include operations with schedule times set
    filters.append(ManufacturingOrderOperation.scheduled_start.isnot(None))
    filters.append(ManufacturingOrderOperation.scheduled_end.isnot(None))
    
    if filters:
        query = query.where(and_(*filters))
    
    # Order by start time
    query = query.order_by(ManufacturingOrderOperation.scheduled_start)
    
    # Execute query
    result = await db.execute(query)
    operations = result.scalars().all()
    
    return operations
