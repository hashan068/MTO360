"""
Shop Floor Quality API - Quick quality actions from shop floor
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.quality import DefectCreate, DefectResponse
from app.modules.quality.application.services import DefectService

router = APIRouter(prefix="/api/shop-floor/quality", tags=["Shop Floor - Quality"])


@router.post("/defects", response_model=DefectResponse, status_code=status.HTTP_201_CREATED)
def report_defect_from_shop_floor(
    mo_operation_id: int,
    defect_type: str,
    severity: str,
    quantity_affected: int,
    description: str,
    create_ncr: bool = False,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Quick defect reporting from shop floor
    
    Simplified interface for operators to report defects during production
    Auto-links to current operation and operator
    """
    # Get operation to derive MO ID
    from app.models.manufacturing import ManufacturingOrderOperation
    
    operation = db.query(ManufacturingOrderOperation).filter(
        ManufacturingOrderOperation.id == mo_operation_id
    ).first()
    
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operation {mo_operation_id} not found"
        )
    
    # Create defect
    defect_data = DefectCreate(
        defect_type=defect_type,
        severity=severity,
        quantity_affected=quantity_affected,
        description=description,
        mo_operation_id=mo_operation_id,
        manufacturing_order_id=operation.manufacturing_order_id,
        operator_id=user_id,
        responsible_party='internal'
    )
    
    service = DefectService(db)
    defect = service.create_defect(defect_data)
    
    # Optionally create NCR
    if create_ncr:
        try:
            from app.modules.quality.application.services import NCRService
            from app.schemas.quality import NCRCreate
            
            ncr_data = NCRCreate(
                defect_id=defect.id,
                manufacturing_order_id=operation.manufacturing_order_id,
                owner_id=user_id,
                priority='medium' if severity != 'critical' else 'high',
                description=f"Auto-created from shop floor defect: {description}"
            )
            
            ncr_service = NCRService(db)
            ncr = ncr_service.create_ncr(ncr_data)
            
            # Add NCR info to response
            defect.ncr_created = True
            defect.ncr_id = ncr.id
        except Exception as e:
            # Log but don't fail defect creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to auto-create NCR: {e}")
    
    return defect


@router.get("/operations/{operation_id}/quality-summary")
def get_operation_quality_summary(
    operation_id: int,
    db: Session = Depends(get_db),
):
    """
    Get quality summary for an operation
    Shows inspection status, defects, holds for shop floor UI
    """
    from app.models.manufacturing import ManufacturingOrderOperation
    from app.modules.quality.application.services import InspectionService, DefectService
    
    # Get operation
    operation = db.query(ManufacturingOrderOperation).filter(
        ManufacturingOrderOperation.id == operation_id
    ).first()
    
    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operation {operation_id} not found"
        )
    
    # Get inspection results
    inspection_service = InspectionService(db)
    inspections = inspection_service.get_inspection_results_by_operation(operation_id)
    
    # Get defects
    defect_service = DefectService(db)
    defects = defect_service.search_defects(mo_operation_id=operation_id)
    
    return {
        "operation_id": operation_id,
        "inspection_status": operation.inspection_status or "none",
        "quality_hold": operation.quality_hold or False,
        "inspection_count": len(inspections),
        "defect_count": len(defects),
        "inspections": [
            {
                "id": i.id,
                "result": i.result.value,
                "inspection_date": i.inspection_date.isoformat() if i.inspection_date else None
            }
            for i in inspections[:5]  # Last 5
        ],
        "defects": [
            {
                "id": d.id,
                "defect_number": d.defect_number,
                "severity": d.severity.value,
                "description": d.description
            }
            for d in defects[:5]  # Last 5
        ]
    }


@router.get("/manufacturing-orders/{mo_id}/quality-summary")
def get_mo_quality_summary(
    mo_id: int,
    db: Session = Depends(get_db),
):
    """
    Get comprehensive quality summary for MO
    For display in shop floor and shipment views
    """
    from app.models.manufacturing import ManufacturingOrder
    from app.modules.quality.application.services import QualityHoldService
    
    # Get MO
    mo = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.id == mo_id
    ).first()
    
    if not mo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manufacturing order {mo_id} not found"
        )
    
    # Check for quality holds
    hold_service = QualityHoldService(db)
    hold_status = hold_service.check_hold_status('manufacturing_order', mo_id)
    
    # Count defects and NCRs via relationships
    defect_count = len(mo.defects) if hasattr(mo, 'defects') and mo.defects else 0
    ncr_count = len(mo.ncrs) if hasattr(mo, 'ncrs') and mo.ncrs else 0
    
    return {
        "mo_id": mo_id,
        "quality_status": mo.quality_status,
        "has_quality_hold": hold_status['has_hold'],
        "hold_info": {
            "hold_number": hold_status['hold'].hold_number if hold_status['has_hold'] else None,
            "hold_reason": hold_status['hold'].hold_reason if hold_status['has_hold'] else None
        } if hold_status['has_hold'] else None,
        "defect_count": defect_count,
        "ncr_count": ncr_count,
        "can_ship": mo.quality_status == 'pass' and not hold_status['has_hold']
    }
