"""
Defect API endpoints
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.quality import DefectCreate, DefectUpdate, DefectResponse
from app.modules.quality.application.services import DefectService

router = APIRouter(prefix="/api/quality/defects", tags=["Quality - Defects"])


@router.post("/", response_model=DefectResponse, status_code=status.HTTP_201_CREATED)
def create_defect(
    data: DefectCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new defect record"""
    service = DefectService(db)
    return service.create_defect(data)


@router.get("/", response_model=List[DefectResponse])
def list_defects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all defects"""
    service = DefectService(db)
    return service.list_defects(skip=skip, limit=limit)


@router.get("/search", response_model=List[DefectResponse])
def search_defects(
    defect_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    responsible_party: Optional[str] = None,
    manufacturing_order_id: Optional[int] = None,
    operator_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    defect_category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Search defects with filters
    Supports multiple filter criteria
    """
    service = DefectService(db)
    
    filters = {
        "skip": skip,
        "limit": limit
    }
    
    if defect_type:
        filters["defect_type"] = defect_type
    if severity:
        filters["severity"] = severity
    if status:
        filters["status"] = status
    if responsible_party:
        filters["responsible_party"] = responsible_party
    if manufacturing_order_id:
        filters["manufacturing_order_id"] = manufacturing_order_id
    if operator_id:
        filters["operator_id"] = operator_id
    if supplier_id:
        filters["supplier_id"] = supplier_id
    if defect_category:
        filters["defect_category"] = defect_category
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    
    return service.search_defects(**filters)


@router.get("/{defect_id}", response_model=DefectResponse)
def get_defect(
    defect_id: int,
    db: Session = Depends(get_db),
):
    """Get defect by ID"""
    service = DefectService(db)
    defect = service.get_defect(defect_id)
    
    if not defect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Defect {defect_id} not found"
        )
    
    return defect


@router.get("/number/{defect_number}", response_model=DefectResponse)
def get_defect_by_number(
    defect_number: str,
    db: Session = Depends(get_db),
):
    """Get defect by defect number"""
    service = DefectService(db)
    defect = service.get_defect_by_number(defect_number)
    
    if not defect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Defect {defect_number} not found"
        )
    
    return defect


@router.put("/{defect_id}", response_model=DefectResponse)
def update_defect(
    defect_id: int,
    data: DefectUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update defect"""
    service = DefectService(db)
    updated = service.update_defect(defect_id, data)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Defect {defect_id} not found"
        )
    
    return updated


@router.post("/{defect_id}/close", response_model=DefectResponse)
def close_defect(
    defect_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Close a defect"""
    service = DefectService(db)
    closed = service.close_defect(defect_id)
    
    if not closed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Defect {defect_id} not found"
        )
    
    return closed


# TODO: Add photo upload endpoint
# @router.post("/{defect_id}/upload-photo")
# def upload_defect_photo(...):
#     pass
