"""
Quality Integration Helper for Manufacturing Module
Provides quality validation and blocking logic for manufacturing operations
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.manufacturing import ManufacturingOrder, ManufacturingOrderOperation
from app.modules.quality.application.services import InspectionService, QualityHoldService


class ManufacturingQualityValidator:
    """
    Quality validation helper for manufacturing operations
    Enforces quality requirements in manufacturing workflow
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.inspection_service = InspectionService(db)
        self.quality_hold_service = QualityHoldService(db)
    
    def validate_operation_start(self, mo_operation_id: int, manufacturing_order_id: int) -> Dict[str, Any]:
        """
        Validate if operation can start
        Checks for quality holds on MO
        
        Returns:
            {
                "can_start": bool,
                "reason": str (if blocked),
                "hold": QualityHold (if blocked)
            }
        """
        # Check for active quality holds on manufacturing order
        hold_status = self.quality_hold_service.check_hold_status(
            'manufacturing_order',
            manufacturing_order_id
        )
        
        if hold_status['has_hold']:
            return {
                "can_start": False,
                "reason": f"Quality hold active: {hold_status['hold'].hold_reason}",
                "hold_id": hold_status['hold'].id,
                "hold_number": hold_status['hold'].hold_number
            }
        
        return {"can_start": True}
    
    def validate_operation_completion(self, mo_operation_id: int) -> Dict[str, Any]:
        """
        Validate if operation can be completed
        Checks:
        1. Quality hold on operation
        2. Required inspection passed
        
        Returns:
            {
                "can_complete": bool,
                "reason": str (if blocked),
                "inspection_status": str,
                "details": dict
            }
        """
        from app.models.manufacturing import ManufacturingOrderOperation
        
        # Get operation
        operation = self.db.query(ManufacturingOrderOperation).filter(
            ManufacturingOrderOperation.id == mo_operation_id
        ).first()
        
        if not operation:
            return {
                "can_complete": False,
                "reason": "Operation not found"
            }
        
        # Check if operation has quality hold
        if operation.quality_hold:
            return {
                "can_complete": False,
                "reason": "Operation has active quality hold",
                "inspection_status": operation.inspection_status or "none"
            }
        
        # Check inspection status
        inspection_status = self.inspection_service.check_operation_inspection_status(mo_operation_id)
        
        # If there are inspections and any failed, block completion
        if inspection_status == 'fail':
            validation_result = self.inspection_service.validate_inspection_requirements(mo_operation_id)
            
            return {
                "can_complete": False,
                "reason": "Inspection failed - rework required",
                "inspection_status": inspection_status,
                "inspection_details": validation_result
            }
        
        # If inspections are pending, warn but may allow (business decision)
        if inspection_status == 'pending':
            return {
                "can_complete": True,  # Can be made False based on business rules
                "warning": "Inspection pending but not yet completed",
                "inspection_status": inspection_status
            }
        
        return {
            "can_complete": True,
            "inspection_status": inspection_status
        }
    
    def check_final_inspection_required(self, manufacturing_order_id: int) -> Dict[str, Any]:
        """
        Check if MO has completed final inspection
        Used before allowing shipment
        
        Returns:
            {
                "has_final_inspection": bool,
                "passed": bool (if has inspection),
                "result": InspectionResult (if exists)
            }
        """
        mo = self.db.query(ManufacturingOrder).filter(
            ManufacturingOrder.id == manufacturing_order_id
        ).first()
        
        if not mo:
            return {"has_final_inspection": False, "error": "MO not found"}
        
        # Check if final_inspection_result_id is set
        if mo.final_inspection_result_id:
            result = self.inspection_service.get_inspection_result(mo.final_inspection_result_id)
            if result:
                return {
                    "has_final_inspection": True,
                    "passed": result.result.value == 'pass',
                    "result": result
                }
        
        return {"has_final_inspection": False}
    
    def get_mo_quality_summary(self, manufacturing_order_id: int) -> Dict[str, Any]:
        """
        Get comprehensive quality summary for MO
        For display in UI
        
        Returns summary of:
        - Quality status
        - Inspection results
        - Active holds
        - Defects
        - NCRs
        """
        mo = self.db.query(ManufacturingOrder).filter(
            ManufacturingOrder.id == manufacturing_order_id
        ).first()
        
        if not mo:
            return {}
        
        # Get inspection results
        inspections = self.inspection_service.get_inspection_results_by_mo(manufacturing_order_id)
        
        # Get quality holds
        hold_status = self.quality_hold_service.check_hold_status(
            'manufacturing_order',
            manufacturing_order_id
        )
        
        # Count defects (would need defect service)
        # For now, use relationship
        defect_count = len(mo.defects) if hasattr(mo, 'defects') and mo.defects else 0
        
        return {
            "quality_status": mo.quality_status,
            "inspection_count": len(inspections),
            "has_final_inspection": mo.final_inspection_result_id is not None,
            "has_quality_hold": hold_status['has_hold'],
            "defect_count": defect_count,
            "ncr_count": len(mo.ncrs) if hasattr(mo, 'ncrs') and mo.ncrs else 0
        }
