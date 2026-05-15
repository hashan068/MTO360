"""
Inspection API endpoints
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.config.database import get_sync_db as get_db
from app.middleware.auth import get_current_user_id
from app.schemas.quality import (
    InspectionPointCreate,
    InspectionPointUpdate,
    InspectionPointResponse,
    InspectionResultCreate,
    InspectionResultUpdate,
    InspectionResultResponse,
)
from app.modules.quality.application.services import InspectionService

router = APIRouter(prefix="/api/quality/inspections", tags=["Quality - Inspections"])


# ========== Inspection Points ==========

@router.post("/points", response_model=InspectionPointResponse, status_code=status.HTTP_201_CREATED)
def create_inspection_point(
    data: InspectionPointCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new inspection point"""
    service = InspectionService(db)
    return service.create_inspection_point(data)


@router.get("/points", response_model=List[InspectionPointResponse])
def list_inspection_points(
    skip: int = 0,
    limit: int = 100,
    route_operation_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List all inspection points, optionally filtered by route operation"""
    service = InspectionService(db)
    
    if route_operation_id:
        return service.get_inspection_points_for_route_operation(route_operation_id)
    
    return service.list_inspection_points(skip=skip, limit=limit)


@router.get("/points/{inspection_point_id}", response_model=InspectionPointResponse)
def get_inspection_point(
    inspection_point_id: int,
    db: Session = Depends(get_db),
):
    """Get inspection point by ID"""
    service = InspectionService(db)
    inspection_point = service.get_inspection_point(inspection_point_id)
    
    if not inspection_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection point {inspection_point_id} not found"
        )
    
    return inspection_point


@router.put("/points/{inspection_point_id}", response_model=InspectionPointResponse)
def update_inspection_point(
    inspection_point_id: int,
    data: InspectionPointUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update inspection point"""
    service = InspectionService(db)
    updated = service.update_inspection_point(inspection_point_id, data)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection point {inspection_point_id} not found"
        )
    
    return updated


@router.delete("/points/{inspection_point_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inspection_point(
    inspection_point_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete inspection point"""
    service = InspectionService(db)
    success = service.delete_inspection_point(inspection_point_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection point {inspection_point_id} not found"
        )
    
    return None


# ========== Inspection Results ==========

@router.post("/results", response_model=InspectionResultResponse, status_code=status.HTTP_201_CREATED)
def record_inspection(
    data: InspectionResultCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Record an inspection result
    Auto-updates MO operation inspection status
    """
    service = InspectionService(db)
    
    try:
        return service.record_inspection(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/results", response_model=List[InspectionResultResponse])
def list_inspection_results(
    skip: int = 0,
    limit: int = 100,
    inspector_id: Optional[int] = None,
    mo_operation_id: Optional[int] = None,
    manufacturing_order_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List inspection results with optional filters"""
    service = InspectionService(db)
    
    if inspector_id:
        return service.get_my_inspections(inspector_id, skip=skip, limit=limit)
    elif mo_operation_id:
        return service.get_inspection_results_by_operation(mo_operation_id)
    elif manufacturing_order_id:
        return service.get_inspection_results_by_mo(manufacturing_order_id)
    
    return service.list_inspection_results(skip=skip, limit=limit)


@router.get("/results/{inspection_result_id}", response_model=InspectionResultResponse)
def get_inspection_result(
    inspection_result_id: int,
    db: Session = Depends(get_db),
):
    """Get inspection result by ID"""
    service = InspectionService(db)
    result = service.get_inspection_result(inspection_result_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection result {inspection_result_id} not found"
        )
    
    return result


@router.put("/results/{inspection_result_id}", response_model=InspectionResultResponse)
def update_inspection_result(
    inspection_result_id: int,
    data: InspectionResultUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update inspection result"""
    service = InspectionService(db)
    updated = service.update_inspection_result(inspection_result_id, data)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inspection result {inspection_result_id} not found"
        )
    
    return updated


@router.get("/my-assignments", response_model=List[InspectionResultResponse])
def get_my_inspection_assignments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get inspections assigned to current user"""
    service = InspectionService(db)
    return service.get_my_inspections(user_id, skip=skip, limit=limit)


@router.get("/operations/{mo_operation_id}/status")
def check_operation_inspection_status(
    mo_operation_id: int,
    db: Session = Depends(get_db),
):
    """
    Check inspection status for an MO operation
    Returns: {status: 'pass'|'fail'|'pending'|'none'}
    """
    service = InspectionService(db)
    inspection_status = service.check_operation_inspection_status(mo_operation_id)
    
    return {
        "mo_operation_id": mo_operation_id,
        "inspection_status": inspection_status
    }


@router.get("/operations/{mo_operation_id}/validate")
def validate_inspection_requirements(
    mo_operation_id: int,
    db: Session = Depends(get_db),
):
    """
    Validate if all required inspections completed for operation
    Returns validation details
    """
    service = InspectionService(db)
    validation = service.validate_inspection_requirements(mo_operation_id)
    
    return {
        "mo_operation_id": mo_operation_id,
        **validation
    }


# TODO: Add photo upload endpoint
# @router.post("/results/{inspection_result_id}/upload-photo")
# def upload_inspection_photo(...):
#     pass
