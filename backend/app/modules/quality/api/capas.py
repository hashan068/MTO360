"""
CAPA (Corrective Action) API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.quality import (
    CAPACreate,
    CAPAUpdate,
    CAPAVerify,
    CAPAClose,
    CAPAResponse,
    ActionItemSchema,
)
from app.modules.quality.application.services import CAPAService

router = APIRouter(prefix="/api/quality/capas", tags=["Quality - CAPA"])


@router.post("/", response_model=CAPAResponse, status_code=status.HTTP_201_CREATED)
def create_capa(
    data: CAPACreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new CAPA"""
    service = CAPAService(db)
    return service.create_capa(data)


@router.get("/", response_model=List[CAPAResponse])
def list_capas(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    owner_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List all CAPAs with optional filters"""
    service = CAPAService(db)
    
    if status_filter:
        return service.get_capas_by_status(status_filter, skip=skip, limit=limit)
    elif owner_id:
        return service.get_my_capas(owner_id, skip=skip, limit=limit)
    
    return service.list_capas(skip=skip, limit=limit)


@router.get("/overdue", response_model=List[CAPAResponse])
def get_overdue_capas(
    db: Session = Depends(get_db),
):
    """Get CAPAs with overdue actions"""
    service = CAPAService(db)
    return service.get_overdue_capas()


@router.get("/pending-verification", response_model=List[CAPAResponse])
def get_pending_verification(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get CAPAs pending verification"""
    service = CAPAService(db)
    return service.get_pending_verification(skip=skip, limit=limit)


@router.get("/my-capas", response_model=List[CAPAResponse])
def get_my_capas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get CAPAs assigned to current user"""
    service = CAPAService(db)
    return service.get_my_capas(user_id, skip=skip, limit=limit)


@router.get("/{capa_id}", response_model=CAPAResponse)
def get_capa(
    capa_id: int,
    db: Session = Depends(get_db),
):
    """Get CAPA by ID"""
    service = CAPAService(db)
    capa = service.get_capa(capa_id)
    
    if not capa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CAPA {capa_id} not found"
        )
    
    return capa


@router.get("/number/{capa_number}", response_model=CAPAResponse)
def get_capa_by_number(
    capa_number: str,
    db: Session = Depends(get_db),
):
    """Get CAPA by number"""
    service = CAPAService(db)
    capa = service.get_capa_by_number(capa_number)
    
    if not capa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CAPA {capa_number} not found"
        )
    
    return capa


@router.put("/{capa_id}", response_model=CAPAResponse)
def update_capa(
    capa_id: int,
    data: CAPAUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update CAPA"""
    service = CAPAService(db)
    updated = service.update_capa(capa_id, data)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CAPA {capa_id} not found"
        )
    
    return updated


@router.post("/{capa_id}/actions", response_model=CAPAResponse)
def add_action(
    capa_id: int,
    action: ActionItemSchema,
    action_type: str = "corrective",  # or preventive
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Add an action item to CAPA"""
    service = CAPAService(db)
    
    try:
        return service.add_action(capa_id, action, action_type)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{capa_id}/actions/{action_id}/status", response_model=CAPAResponse)
def update_action_status(
    capa_id: int,
    action_id: str,
    status: str,
    completed_date: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update status of an action item"""
    service = CAPAService(db)
    
    try:
        return service.update_action_status(capa_id, action_id, status, completed_date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{capa_id}/start", response_model=CAPAResponse)
def start_capa_work(
    capa_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Start working on CAPA"""
    service = CAPAService(db)
    updated = service.start_work(capa_id)
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CAPA {capa_id} not found"
        )
    
    return updated


@router.post("/{capa_id}/verify", response_model=CAPAResponse)
def verify_capa(
    capa_id: int,
    data: CAPAVerify,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Verify CAPA effectiveness"""
    service = CAPAService(db)
    
    try:
        return service.verify_capa(capa_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{capa_id}/close", response_model=CAPAResponse)
def close_capa(
    capa_id: int,
    data: CAPAClose,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Close a CAPA"""
    service = CAPAService(db)
    
    try:
        return service.close_capa(capa_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{capa_id}/completion-status")
def get_completion_status(
    capa_id: int,
    db: Session = Depends(get_db),
):
    """Get completion status of CAPA actions"""
    service = CAPAService(db)
    return service.get_completion_status(capa_id)
