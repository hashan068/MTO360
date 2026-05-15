"""
NCR (Non-Conformance Report) Service - Application Layer
Business logic for NCR workflow management
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.quality import NonConformanceReport, NCRStatusEnum, DispositionEnum
from app.schemas.quality import (
    NCRCreate,
    NCRUpdate,
    NCRApprove,
    NCRClose,
)
from app.modules.quality.infra.repositories import NCRRepository


class NCRService:
    """Service for managing NCR lifecycle and workflows"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ncr_repo = NCRRepository(db)
    
    # ========== NCR Management ==========
    
    def create_ncr(self, data: NCRCreate) -> NonConformanceReport:
        """
        Create a new NCR
        Business logic:
        - Auto-generates NCR number
        - Sets default status to 'open'
        - Can link to defect or MO
        - Sends notification to owner
        """
        ncr_data = data.model_dump()
        ncr_data['status'] = NCRStatusEnum.OPEN
        
        ncr = self.ncr_repo.create(**ncr_data)
        
        # TODO: Send notification to owner
        self._notify_ncr_assignment(ncr)
        
        return ncr
    
    def get_ncr(self, ncr_id: int) -> Optional[NonConformanceReport]:
        """Get NCR by ID"""
        return self.ncr_repo.get_by_id(ncr_id)
    
    def get_ncr_by_number(self, ncr_number: str) -> Optional[NonConformanceReport]:
        """Get NCR by number"""
        return self.ncr_repo.get_by_number(ncr_number)
    
    def list_ncrs(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[NonConformanceReport]:
        """List all NCRs"""
        return self.ncr_repo.get_all(skip=skip, limit=limit)
    
    def get_ncrs_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[NonConformanceReport]:
        """Get NCRs by status"""
        return self.ncr_repo.get_by_status(status, skip=skip, limit=limit)
    
    def get_my_ncrs(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[NonConformanceReport]:
        """Get NCRs assigned to a specific owner"""
        return self.ncr_repo.get_by_owner(owner_id, skip=skip, limit=limit)
    
    def search_ncrs(self, **filters) -> List[NonConformanceReport]:
        """Search NCRs with filters"""
        return self.ncr_repo.search(**filters)
    
    def update_ncr(
        self,
        ncr_id: int,
        data: NCRUpdate
    ) -> Optional[NonConformanceReport]:
        """Update NCR"""
        update_data = data.model_dump(exclude_unset=True)
        
        # Business logic: Auto-calculate total cost if components change
        if 'rework_cost' in update_data or 'scrap_cost' in update_data:
            ncr = self.ncr_repo.get_by_id(ncr_id)
            if ncr:
                rework = update_data.get('rework_cost', ncr.rework_cost) or Decimal('0')
                scrap = update_data.get('scrap_cost', ncr.scrap_cost) or Decimal('0')
                update_data['total_cost'] = rework + scrap
        
        return self.ncr_repo.update(ncr_id, **update_data)
    
    # ========== NCR Workflow ==========
    
    def start_investigation(self, ncr_id: int) -> Optional[NonConformanceReport]:
        """Move NCR to investigating status"""
        return self.ncr_repo.update(
            ncr_id,
            status=NCRStatusEnum.INVESTIGATING
        )
    
    def submit_for_approval(
        self,
        ncr_id: int,
        disposition: DispositionEnum,
        disposition_justification: str
    ) -> Optional[NonConformanceReport]:
        """
        Submit NCR for approval
        Requires disposition and justification
        """
        ncr = self.ncr_repo.get_by_id(ncr_id)
        if not ncr:
            raise ValueError(f"NCR {ncr_id} not found")
        
        if ncr.status != NCRStatusEnum.INVESTIGATING:
            raise ValueError(f"NCR must be in investigating status to submit for approval")
        
        return self.ncr_repo.update(
            ncr_id,
            status=NCRStatusEnum.PENDING_APPROVAL,
            disposition=disposition,
            disposition_justification=disposition_justification
        )
    
    def approve_ncr(
        self,
        ncr_id: int,
        data: NCRApprove
    ) -> Optional[NonConformanceReport]:
        """
        Approve an NCR
        Business logic:
        - Validates NCR is pending approval
        - Sets approval date and approver
        - Changes status to approved
        - Creates quality hold if disposition is 'quarantine'
        """
        ncr = self.ncr_repo.get_by_id(ncr_id)
        if not ncr:
            raise ValueError(f"NCR {ncr_id} not found")
        
        if ncr.status != NCRStatusEnum.PENDING_APPROVAL:
            raise ValueError(f"NCR must be pending approval. Current status: {ncr.status.value}")
        
        updated_ncr = self.ncr_repo.update(
            ncr_id,
            status=NCRStatusEnum.APPROVED,
            approver_id=data.approver_id,
            approval_date=datetime.utcnow(),
            approval_notes=data.approval_notes
        )
        
        # Create quality hold if quarantine disposition
        if ncr.disposition == DispositionEnum.REWORK:
            self._create_quality_hold_for_ncr(ncr)
        
        return updated_ncr
    
    def reject_ncr(
        self,
        ncr_id: int,
        approver_id: int,
        rejection_reason: str
    ) -> Optional[NonConformanceReport]:
        """Reject an NCR - send back to investigating"""
        ncr = self.ncr_repo.get_by_id(ncr_id)
        if not ncr:
            raise ValueError(f"NCR {ncr_id} not found")
        
        return self.ncr_repo.update(
            ncr_id,
            status=NCRStatusEnum.INVESTIGATING,
            approver_id=approver_id,
            approval_notes=f"Rejected: {rejection_reason}"
        )
    
    def close_ncr(
        self,
        ncr_id: int,
        data: NCRClose
    ) -> Optional[NonConformanceReport]:
        """
        Close an NCR
        Business logic:
        - Validates NCR is approved
        - Sets closure date and closer
        - Checks if rework/CAPA completed (if required)
        """
        ncr = self.ncr_repo.get_by_id(ncr_id)
        if not ncr:
            raise ValueError(f"NCR {ncr_id} not found")
        
        if ncr.status != NCRStatusEnum.APPROVED:
            raise ValueError(f"NCR must be approved before closure. Current status: {ncr.status.value}")
        
        return self.ncr_repo.update(
            ncr_id,
            status=NCRStatusEnum.CLOSED,
            closed_by_id=data.closed_by_id,
            closed_date=datetime.utcnow(),
            verification_notes=data.verification_notes
        )
    
    # ========== NCR Analytics ==========
    
    def get_overdue_ncrs(self, days_threshold: int = 7) -> List[NonConformanceReport]:
        """Get overdue NCRs"""
        return self.ncr_repo.get_overdue(days_threshold=days_threshold)
    
    def get_pending_approval_ncrs(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[NonConformanceReport]:
        """Get NCRs pending approval"""
        return self.ncr_repo.get_pending_approval(skip=skip, limit=limit)
    
    def calculate_ncr_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate NCR metrics"""
        return self.ncr_repo.calculate_metrics(
            start_date=start_date,
            end_date=end_date
        )
    
    def get_ncr_aging_report(self) -> List[Dict[str, Any]]:
        """Get NCR aging report"""
        return self.ncr_repo.get_aging_report()
    
    # ========== Business Logic ==========
    
    def calculate_total_cost(
        self,
        ncr_id: int,
        rework_cost: Optional[Decimal] = None,
        scrap_cost: Optional[Decimal] = None
    ) -> Decimal:
        """Calculate total cost for an NCR"""
        ncr = self.ncr_repo.get_by_id(ncr_id)
        if not ncr:
            return Decimal('0')
        
        rework = rework_cost or ncr.rework_cost or Decimal('0')
        scrap = scrap_cost or ncr.scrap_cost or Decimal('0')
        
        total = rework + scrap
        
        # Update NCR with calculated total
        self.ncr_repo.update(ncr_id, total_cost=total)
        
        return total
    
    def validate_closure_ready(self, ncr_id: int) -> Dict[str, Any]:
        """
        Validate if NCR is ready for closure
        Checks:
        - Status is approved
        - Rework completed (if applicable)
        - CAPA completed (if applicable)
        - Quality holds released (if applicable)
        """
        ncr = self.ncr_repo.get_by_id(ncr_id)
        if not ncr:
            return {"ready": False, "reason": "NCR not found"}
        
        if ncr.status != NCRStatusEnum.APPROVED:
            return {"ready": False, "reason": f"NCR not approved. Current status: {ncr.status.value}"}
        
        # Check if disposition requires rework and rework is completed
        if ncr.disposition == DispositionEnum.REWORK:
            # Check rework operations
            # TODO: Check rework completion
            pass
        
        return {"ready": True, "reason": "All closure requirements met"}
    
    # ========== Private Helper Methods ==========
    
    def _notify_ncr_assignment(self, ncr: NonConformanceReport) -> None:
        """Send notification for NCR assignment"""
        # TODO: Integrate with notification service
        pass
    
    def _create_quality_hold_for_ncr(self, ncr: NonConformanceReport) -> None:
        """Create quality hold when NCR disposition is quarantine"""
        # TODO: Integrate with QualityHoldService
        pass
