"""
Rework Operation API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.quality import (
    ReworkOperationCreate,
    ReworkOperationUpdate,
    ReworkOperationStart,
    ReworkOperationComplete,
    ReworkOperationResponse,
)
from app.modules.quality.application.services import ReworkService

router = APIRouter(prefix="/api/quality/rework", tags=["Quality - Rework"])


@router.post("/", response_model=ReworkOperationResponse, status_code=status.HTTP_201_CREATED)
def create_rework_operation(
    data: ReworkOperationCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new rework operation"""
    service = ReworkService(db)
    return service.create_rework_operation(data)


@router.get("/", response_model=List[ReworkOperationResponse])
def list_rework_operations(
    skip: int = 0,
    limit: int = 100,
    work_center_id: Optional[int] = None,
    operator_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List rework operations with optional filters"""
    service = ReworkService(db)
    
    if operator_id:
        return service.get_my_rework_operations(operator_id, skip=skip, limit=limit)
    elif status_filter:
        return [r for r in service.get_rework_queue(work_center_id, status_filter)][:limit]
    
    return service.list_rework_operations(skip=skip, limit=limit)


@router.get("/queue", response_model=List[ReworkOperationResponse])
def get_rework_queue(
    work_center_id: Optional[int] = None,
    status: str = "pending",
    db: Session = Depends(get_db),
):
    """Get rework queue by work center and status"""
    service = ReworkService(db)
    return service.get_rework_queue(work_center_id=work_center_id, status=status)


@router.get("/my-rework", response_model=List[ReworkOperationResponse])
def get_my_rework_operations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get rework operations assigned to current user"""
    service = ReworkService(db)
    return service.get_my_rework_operations(user_id, skip=skip, limit=limit)


@router.get("/{rework_id}", response_model=ReworkOperationResponse)
def get_rework_operation(
    rework_id: int,
    db: Session = Depends(get_db),
):
    """Get rework operation by ID"""
    service = ReworkService(db)
    rework = service.get_rework_operation(rework_id)
    
    if not rework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rework operation {rework_id} not found"
        )
    
    return rework


@router.put("/{rework_id}", response_model=ReworkOperationResponse)
def update_rework_operation(
    rework_id: int,
    data: ReworkOperationUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update rework operation"""
    service = ReworkService(db)
    updated = service.update_rework_operation(rework_id, data)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rework operation {rework_id} not found"
        )
    
    return updated


@router.post("/{rework_id}/start", response_model=ReworkOperationResponse)
def start_rework(
    rework_id: int,
    data: ReworkOperationStart,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Start a rework operation"""
    service = ReworkService(db)
    
    try:
        return service.start_rework(rework_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{rework_id}/complete", response_model=ReworkOperationResponse)
def complete_rework(
    rework_id: int,
    data: ReworkOperationComplete,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Complete a rework operation"""
    service = ReworkService(db)
    
    try:
        return service.complete_rework(rework_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
