"""
Quality Hold API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_sync_db as get_db
from app.middleware.auth import get_current_user_id
from app.schemas.quality import QualityHoldCreate, QualityHoldRelease, QualityHoldResponse
from app.modules.quality.application.services import QualityHoldService

router = APIRouter(prefix="/api/quality/holds", tags=["Quality - Holds"])


@router.post("/", response_model=QualityHoldResponse, status_code=status.HTTP_201_CREATED)
def place_hold(
    data: QualityHoldCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Place a quality hold on inventory, MO, or sales order
    This will block operations/shipments based on hold type
    """
    service = QualityHoldService(db)
    
    try:
        return service.place_hold(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[QualityHoldResponse])
def list_holds(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    hold_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List quality holds with optional filters"""
    service = QualityHoldService(db)
    
    if status_filter == "active":
        return service.get_active_holds(hold_type=hold_type)
    
    # Add more filters as needed
    return service.list_holds(skip=skip, limit=limit)


@router.get("/active", response_model=List[QualityHoldResponse])
def get_active_holds(
    hold_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all active quality holds"""
    service = QualityHoldService(db)
    return service.get_active_holds(hold_type=hold_type)


@router.get("/check/{entity_type}/{entity_id}")
def check_hold_status(
    entity_type: str,  # component, manufacturing_order, sales_order
    entity_id: int,
    db: Session = Depends(get_db),
):
    """
    Check if an entity has an active quality hold
    Returns: {has_hold: bool, hold: QualityHold or None}
    """
    service = QualityHoldService(db)
    
    # Validate entity type
    valid_types = ["component", "manufacturing_order", "sales_order"]
    if entity_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid entity_type. Must be one of: {', '.join(valid_types)}"
        )
    
    return service.check_hold_status(entity_type, entity_id)


@router.get("/{hold_id}", response_model=QualityHoldResponse)
def get_hold(
    hold_id: int,
    db: Session = Depends(get_db),
):
    """Get quality hold by ID"""
    service = QualityHoldService(db)
    hold = service.get_hold(hold_id)
    
    if not hold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality hold {hold_id} not found"
        )
    
    return hold


@router.get("/number/{hold_number}", response_model=QualityHoldResponse)
def get_hold_by_number(
    hold_number: str,
    db: Session = Depends(get_db),
):
    """Get quality hold by number"""
    service = QualityHoldService(db)
    hold = service.get_hold_by_number(hold_number)
    
    if not hold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quality hold {hold_number} not found"
        )
    
    return hold


@router.post("/{hold_id}/release", response_model=QualityHoldResponse)
def release_hold(
    hold_id: int,
    data: QualityHoldRelease,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Release a quality hold
    This will unblock the entity and allow operations to proceed
    """
    service = QualityHoldService(db)
    
    try:
        return service.release_hold(hold_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{hold_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_hold(
    hold_id: int,
    reason: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Cancel a quality hold"""
    service = QualityHoldService(db)
    
    try:
        service.cancel_hold(hold_id, user_id, reason)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
