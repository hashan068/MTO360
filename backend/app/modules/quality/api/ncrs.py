"""
NCR (Non-Conformance Report) API endpoints
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.quality import (
    NCRCreate,
    NCRUpdate,
    NCRApprove,
    NCRClose,
    NCRResponse,
)
from app.modules.quality.application.services import NCRService

router = APIRouter(prefix="/api/quality/ncrs", tags=["Quality - NCR"])


@router.post("/", response_model=NCRResponse, status_code=status.HTTP_201_CREATED)
def create_ncr(
    data: NCRCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new Non-Conformance Report"""
    service = NCRService(db)
    return service.create_ncr(data)


@router.get("/", response_model=List[NCRResponse])
def list_ncrs(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    owner_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List all NCRs with optional filters"""
    service = NCRService(db)
    
    if status_filter:
        return service.get_ncrs_by_status(status_filter, skip=skip, limit=limit)
    elif owner_id:
        return service.get_my_ncrs(owner_id, skip=skip, limit=limit)
    
    return service.list_ncrs(skip=skip, limit=limit)


@router.get("/search", response_model=List[NCRResponse])
def search_ncrs(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    owner_id: Optional[int] = None,
    defect_id: Optional[int] = None,
    manufacturing_order_id: Optional[int] = None,
    disposition: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Search NCRs with filters"""
    service = NCRService(db)
    
    filters = {"skip": skip, "limit": limit}
    
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    if owner_id:
        filters["owner_id"] = owner_id
    if defect_id:
        filters["defect_id"] = defect_id
    if manufacturing_order_id:
        filters["manufacturing_order_id"] = manufacturing_order_id
    if disposition:
        filters["disposition"] = disposition
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    
    return service.search_ncrs(**filters)


@router.get("/overdue", response_model=List[NCRResponse])
def get_overdue_ncrs(
    days_threshold: int = 7,
    db: Session = Depends(get_db),
):
    """Get overdue NCRs"""
    service = NCRService(db)
    return service.get_overdue_ncrs(days_threshold=days_threshold)


@router.get("/pending-approval", response_model=List[NCRResponse])
def get_pending_approval_ncrs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get NCRs pending approval"""
    service = NCRService(db)
    return service.get_pending_approval_ncrs(skip=skip, limit=limit)


@router.get("/my-ncrs", response_model=List[NCRResponse])
def get_my_ncrs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get NCRs assigned to current user"""
    service = NCRService(db)
    return service.get_my_ncrs(user_id, skip=skip, limit=limit)


@router.get("/{ncr_id}", response_model=NCRResponse)
def get_ncr(
    ncr_id: int,
    db: Session = Depends(get_db),
):
    """Get NCR by ID"""
    service = NCRService(db)
    ncr = service.get_ncr(ncr_id)
    
    if not ncr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NCR {ncr_id} not found"
        )
    
    return ncr


@router.get("/number/{ncr_number}", response_model=NCRResponse)
def get_ncr_by_number(
    ncr_number: str,
    db: Session = Depends(get_db),
):
    """Get NCR by number"""
    service = NCRService(db)
    ncr = service.get_ncr_by_number(ncr_number)
    
    if not ncr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NCR {ncr_number} not found"
        )
    
    return ncr


@router.put("/{ncr_id}", response_model=NCRResponse)
def update_ncr(
    ncr_id: int,
    data: NCRUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update NCR"""
    service = NCRService(db)
    updated = service.update_ncr(ncr_id, data)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NCR {ncr_id} not found"
        )
    
    return updated


@router.post("/{ncr_id}/start-investigation", response_model=NCRResponse)
def start_investigation(
    ncr_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Start NCR investigation"""
    service = NCRService(db)
    updated = service.start_investigation(ncr_id)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NCR {ncr_id} not found"
        )
    
    return updated


@router.post("/{ncr_id}/approve", response_model=NCRResponse)
def approve_ncr(
    ncr_id: int,
    data: NCRApprove,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Approve an NCR"""
    service = NCRService(db)
    
    try:
        return service.approve_ncr(ncr_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{ncr_id}/close", response_model=NCRResponse)
def close_ncr(
    ncr_id: int,
    data: NCRClose,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Close an NCR"""
    service = NCRService(db)
    
    try:
        return service.close_ncr(ncr_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
