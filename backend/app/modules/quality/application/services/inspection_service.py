"""
Inspection Service - Application Layer
Business logic for inspection management
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.quality import InspectionPoint, InspectionResult, InspectionResultEnum
from app.schemas.quality import (
    InspectionPointCreate,
    InspectionPointUpdate,
    InspectionResultCreate,
    InspectionResultUpdate,
)
from app.modules.quality.infra.repositories import (
    InspectionPointRepository,
    InspectionResultRepository,
)


class InspectionService:
    """Service for managing inspections and inspection points"""
    
    def __init__(self, db: Session):
        self.db = db
        self.inspection_point_repo = InspectionPointRepository(db)
        self.inspection_result_repo = InspectionResultRepository(db)
    
    # ========== Inspection Point Management ==========
    
    def create_inspection_point(self, data: InspectionPointCreate) -> InspectionPoint:
        """Create a new inspection point"""
        inspection_point = self.inspection_point_repo.create(
            **data.model_dump()
        )
        return inspection_point
    
    def get_inspection_point(self, inspection_point_id: int) -> Optional[InspectionPoint]:
        """Get inspection point by ID"""
        return self.inspection_point_repo.get_by_id(inspection_point_id)
    
    def list_inspection_points(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[InspectionPoint]:
        """List all inspection points"""
        return self.inspection_point_repo.get_all(skip=skip, limit=limit)
    
    def update_inspection_point(
        self,
        inspection_point_id: int,
        data: InspectionPointUpdate
    ) -> Optional[InspectionPoint]:
        """Update inspection point"""
        update_data = data.model_dump(exclude_unset=True)
        return self.inspection_point_repo.update(inspection_point_id, **update_data)
    
    def delete_inspection_point(self, inspection_point_id: int) -> bool:
        """Delete inspection point"""
        return self.inspection_point_repo.delete(inspection_point_id)
    
    def get_inspection_points_for_route_operation(
        self,
        route_operation_id: int
    ) -> List[InspectionPoint]:
        """Get all inspection points for a route operation"""
        return self.inspection_point_repo.get_by_route_operation(route_operation_id)
    
    # ========== Inspection Result Management ==========
    
    def record_inspection(self, data: InspectionResultCreate) -> InspectionResult:
        """
        Record an inspection result
        Business logic:
        - Validates inspection point exists
        - Auto-sets inspection date if not provided
        - Updates MO operation inspection_status if linked
        - Emits event if inspection fails
        """
        # Validate inspection point exists
        inspection_point = self.inspection_point_repo.get_by_id(data.inspection_point_id)
        if not inspection_point:
            raise ValueError(f"Inspection point {data.inspection_point_id} not found")
        
        # Create inspection result
        result_data = data.model_dump()
        inspection_result = self.inspection_result_repo.create(**result_data)
        
        # Update MO operation inspection status if applicable
        if data.mo_operation_id:
            self._update_operation_inspection_status(
                data.mo_operation_id,
                data.result
            )
        
        # Update MO quality status if final inspection
        if data.manufacturing_order_id and inspection_point.inspection_type == 'final':
            self._update_mo_quality_status(
                data.manufacturing_order_id,
                data.result
            )
        
        # Emit event if inspection failed
        if data.result == InspectionResultEnum.FAIL:
            self._emit_inspection_failed_event(inspection_result)
        
        return inspection_result
    
    def get_inspection_result(self, inspection_result_id: int) -> Optional[InspectionResult]:
        """Get inspection result by ID"""
        return self.inspection_result_repo.get_by_id(inspection_result_id)
    
    def list_inspection_results(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[InspectionResult]:
        """List all inspection results"""
        return self.inspection_result_repo.get_all(skip=skip, limit=limit)
    
    def get_my_inspections(
        self,
        inspector_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[InspectionResult]:
        """Get inspections for a specific inspector"""
        return self.inspection_result_repo.get_by_inspector(
            inspector_id,
            skip=skip,
            limit=limit
        )
    
    def get_pending_inspections(
        self,
        work_center_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get pending inspections for operations
        Returns inspections that need to be performed
        """
        # This would require checking against MO operations
        # For now, return empty list - full implementation needs MO integration
        return []
    
    def update_inspection_result(
        self,
        inspection_result_id: int,
        data: InspectionResultUpdate
    ) -> Optional[InspectionResult]:
        """Update inspection result"""
        update_data = data.model_dump(exclude_unset=True)
        return self.inspection_result_repo.update(inspection_result_id, **update_data)
    
    # ========== Analytics ==========
    
    def calculate_pass_rate(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        inspector_id: Optional[int] = None,
        mo_operation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Calculate inspection pass rate with filters"""
        return self.inspection_result_repo.calculate_pass_rate(
            start_date=start_date,
            end_date=end_date,
            inspector_id=inspector_id,
            mo_operation_id=mo_operation_id
        )
    
    def get_inspection_results_by_mo(
        self,
        manufacturing_order_id: int
    ) -> List[InspectionResult]:
        """Get all inspection results for a manufacturing order"""
        return self.inspection_result_repo.get_by_manufacturing_order(
            manufacturing_order_id
        )
    
    def get_inspection_results_by_operation(
        self,
        mo_operation_id: int
    ) -> List[InspectionResult]:
        """Get all inspection results for a MO operation"""
        return self.inspection_result_repo.get_by_mo_operation(mo_operation_id)
    
    # ========== Validation & Business Logic ==========
    
    def validate_inspection_requirements(
        self,
        mo_operation_id: int
    ) -> Dict[str, Any]:
        """
        Validate if all required inspections have been completed for an operation
        Returns: {
            "all_passed": bool,
            "required_inspections": int,
            "completed_inspections": int,
            "failed_inspections": int,
            "can_complete_operation": bool
        }
        """
        # Get all inspections for this operation
        inspections = self.inspection_result_repo.get_by_mo_operation(mo_operation_id)
        
        # Get required inspection points for this operation
        # (This would need route operation → inspection points mapping)
        # For now, simple validation
        
        total = len(inspections)
        passed = sum(1 for i in inspections if i.result == InspectionResultEnum.PASS)
        failed = sum(1 for i in inspections if i.result == InspectionResultEnum.FAIL)
        conditional = sum(1 for i in inspections if i.result == InspectionResultEnum.CONDITIONAL)
        
        # Operation can complete if no failed inspections
        can_complete = failed == 0
        
        return {
            "all_passed": passed == total and total > 0,
            "required_inspections": total,
            "completed_inspections": total,
            "passed_inspections": passed,
            "failed_inspections": failed,
            "conditional_inspections": conditional,
            "can_complete_operation": can_complete
        }
    
    def check_operation_inspection_status(
        self,
        mo_operation_id: int
    ) -> str:
        """
        Check overall inspection status for an operation
        Returns: 'pass', 'fail', 'pending', or 'none'
        """
        inspections = self.inspection_result_repo.get_by_mo_operation(mo_operation_id)
        
        if not inspections:
            return 'none'
        
        # If any failed, overall is fail
        if any(i.result == InspectionResultEnum.FAIL for i in inspections):
            return 'fail'
        
        # If all passed (or conditional), overall is pass
        if all(i.result in [InspectionResultEnum.PASS, InspectionResultEnum.CONDITIONAL] 
               for i in inspections):
            return 'pass'
        
        return 'pending'
    
    # ========== Private Helper Methods ==========
    
    def _update_operation_inspection_status(
        self,
        mo_operation_id: int,
        result: InspectionResultEnum
    ) -> None:
        """Update MO operation's inspection_status field"""
        from app.models.manufacturing import ManufacturingOrderOperation
        
        operation = self.db.query(ManufacturingOrderOperation).filter(
            ManufacturingOrderOperation.id == mo_operation_id
        ).first()
        
        if operation:
            operation.inspection_status = result.value
            self.db.commit()
    
    def _update_mo_quality_status(
        self,
        manufacturing_order_id: int,
        result: InspectionResultEnum
    ) -> None:
        """Update MO's quality_status field"""
        from app.models.manufacturing import ManufacturingOrder
        
        mo = self.db.query(ManufacturingOrder).filter(
            ManufacturingOrder.id == manufacturing_order_id
        ).first()
        
        if mo:
            mo.quality_status = result.value
            self.db.commit()
    
    def _emit_inspection_failed_event(self, inspection_result: InspectionResult) -> None:
        """Emit event when inspection fails"""
        try:
            from app.modules.quality.application.events.quality_events import QualityEventEmitter
            emitter = QualityEventEmitter(self.db)
            emitter.emit_inspection_failed(
                inspection_id=inspection_result.id,
                mo_operation_id=inspection_result.mo_operation_id,
                inspector_id=inspection_result.inspector_id
            )
        except ImportError:
            # Event system not available, just log
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Inspection {inspection_result.id} failed but event system unavailable")
