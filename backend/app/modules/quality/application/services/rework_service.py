"""
Rework Operation Service - Application Layer
Business logic for rework management
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.quality import ReworkOperation
from app.schemas.quality import (
    ReworkOperationCreate,
    ReworkOperationUpdate,
    ReworkOperationStart,
    ReworkOperationComplete,
)
from app.modules.quality.infra.repositories import ReworkOperationRepository


class ReworkService:
    """Service for managing rework operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rework_repo = ReworkOperationRepository(db)
    
    # ========== Rework Management ==========
    
    def create_rework_operation(
        self,
        data: ReworkOperationCreate
    ) -> ReworkOperation:
        """
        Create a new rework operation
        Business logic:
        - Sets default status to 'pending'
        - Can auto-schedule based on work center capacity
        - Links to NCR
        """
        rework_data = data.model_dump()
        rework_data['status'] = 'pending'
        
        rework = self.rework_repo.create(**rework_data)
        
        # TODO: Auto-schedule based on work center capacity
        # TODO: Notify assigned operator
        
        return rework
    
    def get_rework_operation(self, rework_id: int) -> Optional[ReworkOperation]:
        """Get rework operation by ID"""
        return self.rework_repo.get_by_id(rework_id)
    
    def list_rework_operations(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReworkOperation]:
        """List all rework operations"""
        return self.rework_repo.get_all(skip=skip, limit=limit)
    
    def get_rework_by_ncr(self, ncr_id: int) -> List[ReworkOperation]:
        """Get all rework operations for an NCR"""
        return self.rework_repo.get_by_ncr(ncr_id)
    
    def get_rework_queue(
        self,
        work_center_id: Optional[int] = None,
        status: str = 'pending'
    ) -> List[ReworkOperation]:
        """
        Get rework queue
        Can filter by work center and status
        """
        if work_center_id:
            rework_ops = self.rework_repo.get_by_work_center(work_center_id)
            return [r for r in rework_ops if r.status == status]
        else:
            return self.rework_repo.get_by_status(status)
    
    def get_my_rework_operations(
        self,
        operator_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReworkOperation]:
        """Get rework operations assigned to an operator"""
        return self.rework_repo.get_by_operator(
            operator_id,
            skip=skip,
            limit=limit
        )
    
    def update_rework_operation(
        self,
        rework_id: int,
        data: ReworkOperationUpdate
    ) -> Optional[ReworkOperation]:
        """Update rework operation"""
        update_data = data.model_dump(exclude_unset=True)
        return self.rework_repo.update(rework_id, **update_data)
    
    # ========== Rework Workflow ==========
    
    def start_rework(
        self,
        rework_id: int,
        data: ReworkOperationStart
    ) -> Optional[ReworkOperation]:
        """
        Start a rework operation
        Business logic:
        - Sets status to 'in_progress'
        - Records actual start time
        - Validates operator assignment
        """
        rework = self.rework_repo.get_by_id(rework_id)
        if not rework:
            raise ValueError(f"Rework operation {rework_id} not found")
        
        if rework.status != 'pending':
            raise ValueError(f"Rework must be pending to start. Current status: {rework.status}")
        
        return self.rework_repo.update(
            rework_id,
            status='in_progress',
            actual_start=datetime.utcnow(),
            assigned_operator_id=data.assigned_operator_id
        )
    
    def complete_rework(
        self,
        rework_id: int,
        data: ReworkOperationComplete
    ) -> Optional[ReworkOperation]:
        """
        Complete a rework operation
        Business logic:
        - Sets status to 'completed'
        - Records actual end time and duration
        - Links to re-inspection if provided
        - Calculates costs
        """
        rework = self.rework_repo.get_by_id(rework_id)
        if not rework:
            raise ValueError(f"Rework operation {rework_id} not found")
        
        if rework.status != 'in_progress':
            raise ValueError(f"Rework must be in progress to complete. Current status: {rework.status}")
        
        return self.rework_repo.update(
            rework_id,
            status='completed',
            actual_end=datetime.utcnow(),
            actual_duration_minutes=data.actual_duration_minutes,
            notes=data.notes,
            re_inspection_result_id=data.re_inspection_result_id
        )
    
    def cancel_rework(
        self,
        rework_id: int,
        reason: str
    ) -> Optional[ReworkOperation]:
        """Cancel a rework operation"""
        return self.rework_repo.update(
            rework_id,
            status='cancelled',
            notes=f"Cancelled: {reason}"
        )
    
    # ========== Cost Calculation ==========
    
    def calculate_rework_cost(
        self,
        rework_id: int,
        labor_cost: Optional[Decimal] = None,
        material_cost: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate total rework cost
        Returns: {labor_cost, material_cost, total_cost}
        """
        rework = self.rework_repo.get_by_id(rework_id)
        if not rework:
            return {
                "labor_cost": Decimal('0'),
                "material_cost": Decimal('0'),
                "total_cost": Decimal('0')
            }
        
        labor = labor_cost or rework.labor_cost or Decimal('0')
        material = material_cost or rework.material_cost or Decimal('0')
        total = labor + material
        
        # Update rework with costs
        self.rework_repo.update(
            rework_id,
            labor_cost=labor,
            material_cost=material
        )
        
        return {
            "labor_cost": labor,
            "material_cost": material,
            "total_cost": total
        }
    
    def estimate_labor_cost(
        self,
        rework_id: int,
        hourly_rate: Decimal = Decimal('25.00')
    ) -> Decimal:
        """
        Estimate labor cost based on actual or scheduled duration
        Default hourly rate: $25/hour
        """
        rework = self.rework_repo.get_by_id(rework_id)
        if not rework:
            return Decimal('0')
        
        # Use actual duration if completed, otherwise scheduled
        duration_minutes = rework.actual_duration_minutes or rework.scheduled_duration_minutes
        duration_hours = Decimal(duration_minutes) / Decimal('60')
        
        labor_cost = duration_hours * hourly_rate
        
        return labor_cost.quantize(Decimal('0.01'))
    
    # ========== Analytics ==========
    
    def get_rework_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get rework operation statistics"""
        return self.rework_repo.get_statistics(
            start_date=start_date,
            end_date=end_date
        )
    
    def get_pending_rework_count(self) -> int:
        """Get count of pending rework operations"""
        pending = self.rework_repo.get_pending()
        return len(pending)
    
    def get_in_progress_rework(self) -> List[ReworkOperation]:
        """Get currently in-progress rework operations"""
        return self.rework_repo.get_in_progress()
    
    # ========== Scheduling ==========
    
    def schedule_rework(
        self,
        rework_id: int,
        scheduled_start: datetime,
        scheduled_end: datetime
    ) -> Optional[ReworkOperation]:
        """Schedule a rework operation"""
        # TODO: Validate work center capacity
        # TODO: Check for scheduling conflicts
        
        return self.rework_repo.update(
            rework_id,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end
        )
