"""
Shop Floor API Endpoints - Operation execution and tracking
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.middleware.permission_checker import require_permission
from app.schemas.manufacturing import ManufacturingOrderOperationResponse
from app.modules.manufacturing.application.services.shop_floor_service import (
    ShopFloorService,
)
from app.models.manufacturing import OperationStatusEnum


# Request/Response Schemas
class StartOperationRequest(BaseModel):
    """Request to start an operation"""
    operator_id: Optional[int] = None  # If not provided, use authenticated user


class PauseOperationRequest(BaseModel):
    """Request to pause an operation"""
    reason: str


class BlockOperationRequest(BaseModel):
    """Request to block an operation"""
    blocking_reason: str


class OperationExecutionResponse(BaseModel):
    """Response with operation execution details"""
    operation_id: int
    status: str
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    actual_duration_minutes: Optional[int]
    scheduled_duration_minutes: int
    variance_minutes: Optional[int]

    @classmethod
    def from_operation(cls, operation):
        """Create from ManufacturingOrderOperation"""
        variance = None
        if operation.actual_duration_minutes and operation.scheduled_duration_minutes:
            variance = operation.actual_duration_minutes - operation.scheduled_duration_minutes

        return cls(
            operation_id=operation.id,
            status=operation.status.value,
            actual_start=operation.actual_start,
            actual_end=operation.actual_end,
            actual_duration_minutes=operation.actual_duration_minutes,
            scheduled_duration_minutes=operation.scheduled_duration_minutes,
            variance_minutes=variance,
        )


class DashboardMetrics(BaseModel):
    """Dashboard metrics response"""
    active_operations: int
    pending_operations: int
    blocked_operations: int
    completed_today: int
    avg_utilization_pct: float
    timestamp: datetime


class WorkCenterQueueItem(BaseModel):
    """Work center queue item"""
    operation_id: int
    operation_name: str
    sequence: int
    status: str
    scheduled_start: Optional[datetime]
    scheduled_duration_minutes: int
    mo_id: int
    mo_number: Optional[str]
    product_id: Optional[int]
    quantity: Optional[int]


router = APIRouter(prefix="/shop-floor", tags=["Shop Floor"])


@router.post("/operations/{operation_id}/start", response_model=OperationExecutionResponse)
async def start_operation(
    operation_id: int,
    request: StartOperationRequest = StartOperationRequest(),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_permission("production.operation.start")),
):
    """
    Start an operation - records actual start time.
    
    Validates:
    - Operation is SCHEDULED or PENDING
    - Previous operation in sequence is complete
    """
    service = ShopFloorService(db)
    
    # Use provided operator_id or authenticated user
    operator_id = request.operator_id if request.operator_id else user_id
    
    try:
        operation = await service.start_operation(operation_id, operator_id)
        return OperationExecutionResponse.from_operation(operation)
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/operations/{operation_id}/complete", response_model=OperationExecutionResponse)
async def complete_operation(
    operation_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_permission("production.operation.complete")),
):
    """
    Complete an operation - records actual end time and calculates duration.
    
    Validates:
    - Operation is IN_PROGRESS
    - Actual start time is set
    """
    service = ShopFloorService(db)
    
    try:
        operation = await service.complete_operation(operation_id)
        return OperationExecutionResponse.from_operation(operation)
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/operations/{operation_id}/pause", response_model=ManufacturingOrderOperationResponse)
async def pause_operation(
    operation_id: int,
    request: PauseOperationRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Pause an in-progress operation.
    
    Records pause reason in operation notes.
    """
    service = ShopFloorService(db)
    
    try:
        operation = await service.pause_operation(operation_id, request.reason)
        return operation
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/operations/{operation_id}/block", response_model=ManufacturingOrderOperationResponse)
async def block_operation(
    operation_id: int,
    request: BlockOperationRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_permission("production.operation.block")),
):
    """
    Block an operation due to an issue.
    
    Updates operation status to BLOCKED and MO status to BLOCKED.
    """
    service = ShopFloorService(db)
    
    try:
        operation = await service.block_operation(operation_id, request.blocking_reason)
        return operation
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/operations/{operation_id}/unblock", response_model=ManufacturingOrderOperationResponse)
async def unblock_operation(
    operation_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Unblock a blocked operation.
    
    Returns operation to IN_PROGRESS or SCHEDULED status.
    """
    service = ShopFloorService(db)
    
    try:
        operation = await service.unblock_operation(operation_id)
        return operation
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/work-centers/{work_center_id}/queue", response_model=List[WorkCenterQueueItem])
async def get_work_center_queue(
    work_center_id: int,
    status: Optional[str] = Query(None, description="Filter by status (comma-separated)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the queue of operations for a work center.
    
    Shows pending, scheduled, and in-progress operations by default.
    """
    service = ShopFloorService(db)
    
    # Parse status filter
    status_filter = None
    if status:
        try:
            status_filter = [
                OperationStatusEnum(s.strip()) for s in status.split(",")
            ]
        except ValueError as e:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status value: {e}"
            )
    
    queue_items = await service.get_work_center_queue(work_center_id, status_filter)
    
    return [WorkCenterQueueItem(**item) for item in queue_items]


@router.get("/operations/my-assignments", response_model=List[ManufacturingOrderOperationResponse])
async def get_my_assignments(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get operations assigned to the current user.
    
    Returns scheduled and in-progress operations.
    """
    service = ShopFloorService(db)
    
    operations = await service.get_my_assignments(user_id)
    
    return operations


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_data(
    work_center_id: Optional[int] = Query(None, description="Filter by work center"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get shop floor dashboard metrics.
    
    Shows:
    - Active operations count
    - Pending operations count
    - Blocked operations count
    - Completed today count
    - Average utilization percentage
    """
    service = ShopFloorService(db)
    
    metrics = await service.get_dashboard_data(work_center_id)
    
    return DashboardMetrics(**metrics)
