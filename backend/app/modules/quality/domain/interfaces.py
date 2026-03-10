"""
Quality Management Domain Layer - Repository Interfaces (Protocols)
"""
from typing import Protocol, Optional, List
from datetime import datetime, date

from app.models.quality import (
    InspectionPoint,
    InspectionResult,
    Defect,
    NonConformanceReport,
    ReworkOperation,
    CorrectiveAction,
    QualityHold,
)


class InspectionPointRepositoryProtocol(Protocol):
    """Repository interface for InspectionPoint management"""
    
    def create(self, **kwargs) -> InspectionPoint:
        """Create a new inspection point"""
        ...
    
    def get_by_id(self, inspection_point_id: int) -> Optional[InspectionPoint]:
        """Get inspection point by ID"""
        ...
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[InspectionPoint]:
        """Get all inspection points"""
        ...
    
    def get_by_route_operation(self, route_operation_id: int) -> List[InspectionPoint]:
        """Get inspection points by route operation"""
        ...
    
    def update(self, inspection_point_id: int, **kwargs) -> Optional[InspectionPoint]:
        """Update inspection point"""
        ...
    
    def delete(self, inspection_point_id: int) -> bool:
        """Delete inspection point"""
        ...


class InspectionResultRepositoryProtocol(Protocol):
    """Repository interface for InspectionResult management"""
    
    def create(self, **kwargs) -> InspectionResult:
        """Create a new inspection result"""
        ...
    
    def get_by_id(self, inspection_result_id: int) -> Optional[InspectionResult]:
        """Get inspection result by ID"""
        ...
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[InspectionResult]:
        """Get all inspection results"""
        ...
    
    def get_by_inspector(self, inspector_id: int) -> List[InspectionResult]:
        """Get inspection results by inspector"""
        ...
    
    def get_by_mo_operation(self,  mo_operation_id: int) -> List[InspectionResult]:
        """Get inspection results by MO operation"""
        ...
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[InspectionResult]:
        """Get inspection results within date range"""
        ...
    
    def update(self, inspection_result_id: int, **kwargs) -> Optional[InspectionResult]:
        """Update inspection result"""
        ...


class DefectRepositoryProtocol(Protocol):
    """Repository interface for Defect management"""
    
    def create(self, **kwargs) -> Defect:
        """Create a new defect"""
        ...
    
    def get_by_id(self, defect_id: int) -> Optional[Defect]:
        """Get defect by ID"""
        ...
    
    def get_by_number(self, defect_number: str) -> Optional[Defect]:
        """Get defect by number"""
        ...
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Defect]:
        """Get all defects"""
        ...
    
    def search(self, **filters) -> List[Defect]:
        """Search defects with filters"""
        ...
    
    def get_by_mo(self, manufacturing_order_id: int) -> List[Defect]:
        """Get defects by manufacturing order"""
        ...
    
    def update(self, defect_id: int, **kwargs) -> Optional[Defect]:
        """Update defect"""
        ...
    
    def generate_defect_number(self) -> str:
        """Generate unique defect number"""
        ...


class NCRRepositoryProtocol(Protocol):
    """Repository interface for NonConformanceReport management"""
    
    def create(self, **kwargs) -> NonConformanceReport:
        """Create a new NCR"""
        ...
    
    def get_by_id(self, ncr_id: int) -> Optional[NonConformanceReport]:
        """Get NCR by ID"""
        ...
    
    def get_by_number(self, ncr_number: str) -> Optional[NonConformanceReport]:
        """Get NCR by number"""
        ...
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[NonConformanceReport]:
        """Get all NCRs"""
        ...
    
    def get_by_status(self, status: str) -> List[NonConformanceReport]:
        """Get NCRs by status"""
        ...
    
    def get_overdue(self) -> List[NonConformanceReport]:
        """Get overdue NCRs"""
        ...
    
    def update(self, ncr_id: int, **kwargs) -> Optional[NonConformanceReport]:
        """Update NCR"""
        ...
    
    def generate_ncr_number(self) -> str:
        """Generate unique NCR number"""
        ...


class ReworkOperationRepositoryProtocol(Protocol):
    """Repository interface for ReworkOperation management"""
    
    def create(self, **kwargs) -> ReworkOperation:
        """Create a new rework operation"""
        ...
    
    def get_by_id(self, rework_id: int) -> Optional[ReworkOperation]:
        """Get rework operation by ID"""
        ...
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ReworkOperation]:
        """Get all rework operations"""
        ...
    
    def get_by_ncr(self, ncr_id: int) -> List[ReworkOperation]:
        """Get rework operations by NCR"""
        ...
    
    def get_by_work_center(self, work_center_id: int) -> List[ReworkOperation]:
        """Get rework operations by work center"""
        ...
    
    def update(self, rework_id: int, **kwargs) -> Optional[ReworkOperation]:
        """Update rework operation"""
        ...


class CAPARepositoryProtocol(Protocol):
    """Repository interface for CorrectiveAction management"""
    
    def create(self, **kwargs) -> CorrectiveAction:
        """Create a new CAPA"""
        ...
    
    def get_by_id(self, capa_id: int) -> Optional[CorrectiveAction]:
        """Get CAPA by ID"""
        ...
    
    def get_by_number(self, capa_number: str) -> Optional[CorrectiveAction]:
        """Get CAPA by number"""
        ...
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[CorrectiveAction]:
        """Get all CAPAs"""
        ...
    
    def get_by_status(self, status: str) -> List[CorrectiveAction]:
        """Get CAPAs by status"""
        ...
    
    def get_overdue(self) -> List[CorrectiveAction]:
        """Get CAPAs with overdue actions"""
        ...
    
    def update(self, capa_id: int, **kwargs) -> Optional[CorrectiveAction]:
        """Update CAPA"""
        ...
    
    def generate_capa_number(self) -> str:
        """Generate unique CAPA number"""
        ...


class QualityHoldRepositoryProtocol(Protocol):
    """Repository interface for QualityHold management"""
    
    def create(self, **kwargs) -> QualityHold:
        """Create a new quality hold"""
        ...
    
    def get_by_id(self, hold_id: int) -> Optional[QualityHold]:
        """Get quality hold by ID"""
        ...
    
    def get_by_number(self, hold_number: str) -> Optional[QualityHold]:
        """Get quality hold by number"""
        ...
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[QualityHold]:
        """Get all quality holds"""
        ...
    
    def get_active(self, hold_type: Optional[str] = None) -> List[QualityHold]:
        """Get active quality holds"""
        ...
    
    def check_hold_on_entity(self, entity_type: str, entity_id: int) -> Optional[QualityHold]:
        """Check if entity has active hold"""
        ...
    
    def update(self, hold_id: int, **kwargs) -> Optional[QualityHold]:
        """Update quality hold"""
        ...
    
    def generate_hold_number(self) -> str:
        """Generate unique quality hold number"""
        ...
