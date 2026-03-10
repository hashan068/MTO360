"""
Rework Operation Repository - Infrastructure Layer
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func

from app.models.quality import ReworkOperation
from app.modules.quality.domain.interfaces import ReworkOperationRepositoryProtocol


class ReworkOperationRepository(ReworkOperationRepositoryProtocol):
    """Repository for ReworkOperation entity"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> ReworkOperation:
        """Create a new rework operation"""
        rework = ReworkOperation(**kwargs)
        self.db.add(rework)
        self.db.commit()
        self.db.refresh(rework)
        return rework
    
    def get_by_id(self, rework_id: int) -> Optional[ReworkOperation]:
        """Get rework operation by ID with relationships"""
        return self.db.query(ReworkOperation).options(
            joinedload(ReworkOperation.ncr),
            joinedload(ReworkOperation.manufacturing_order),
            joinedload(ReworkOperation.work_center),
            joinedload(ReworkOperation.assigned_operator),
            joinedload(ReworkOperation.re_inspection_result),
        ).filter(
            ReworkOperation.id == rework_id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ReworkOperation]:
        """Get all rework operations"""
        return self.db.query(ReworkOperation).options(
            joinedload(ReworkOperation.ncr),
            joinedload(ReworkOperation.work_center),
            joinedload(ReworkOperation.assigned_operator),
        ).order_by(ReworkOperation.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_ncr(self, ncr_id: int) -> List[ReworkOperation]:
        """Get rework operations by NCR"""
        return self.db.query(ReworkOperation).options(
            joinedload(ReworkOperation.work_center),
            joinedload(ReworkOperation.assigned_operator),
        ).filter(
            ReworkOperation.ncr_id == ncr_id
        ).all()
    
    def get_by_work_center(
        self, 
        work_center_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReworkOperation]:
        """Get rework operations by work center"""
        return self.db.query(ReworkOperation).options(
            joinedload(ReworkOperation.ncr),
            joinedload(ReworkOperation.manufacturing_order),
            joinedload(ReworkOperation.assigned_operator),
        ).filter(
            ReworkOperation.work_center_id == work_center_id
        ).order_by(ReworkOperation.scheduled_start).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[ReworkOperation]:
        """Get rework operations by status"""
        return self.db.query(ReworkOperation).options(
            joinedload(ReworkOperation.ncr),
            joinedload(ReworkOperation.work_center),
            joinedload(ReworkOperation.assigned_operator),
        ).filter(
            ReworkOperation.status == status
        ).order_by(ReworkOperation.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_operator(
        self,
        operator_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReworkOperation]:
        """Get rework operations by operator"""
        return self.db.query(ReworkOperation).options(
            joinedload(ReworkOperation.ncr),
            joinedload(ReworkOperation.work_center),
            joinedload(ReworkOperation.manufacturing_order),
        ).filter(
            ReworkOperation.assigned_operator_id == operator_id
        ).order_by(ReworkOperation.scheduled_start).offset(skip).limit(limit).all()
    
    def get_pending(self, skip: int = 0, limit: int = 100) -> List[ReworkOperation]:
        """Get pending rework operations"""
        return self.db.query(ReworkOperation).options(
            joinedload(ReworkOperation.ncr),
            joinedload(ReworkOperation.work_center),
        ).filter(
            ReworkOperation.status == 'pending'
        ).order_by(ReworkOperation.created_at.asc()).offset(skip).limit(limit).all()
    
    def get_in_progress(self, skip: int = 0, limit: int = 100) -> List[ReworkOperation]:
        """Get in-progress rework operations"""
        return self.db.query(ReworkOperation).options(
            joinedload(ReworkOperation.ncr),
            joinedload(ReworkOperation.work_center),
            joinedload(ReworkOperation.assigned_operator),
        ).filter(
            ReworkOperation.status == 'in_progress'
        ).order_by(ReworkOperation.actual_start).offset(skip).limit(limit).all()
    
    def update(self, rework_id: int, **kwargs) -> Optional[ReworkOperation]:
        """Update rework operation"""
        rework = self.get_by_id(rework_id)
        if not rework:
            return None
        
        for key, value in kwargs.items():
            if hasattr(rework, key):
                setattr(rework, key, value)
        
        self.db.commit()
        self.db.refresh(rework)
        return rework
    
    def calculate_total_cost(self, rework_id: int) -> float:
        """Calculate total cost for a rework operation"""
        rework = self.get_by_id(rework_id)
        if not rework:
            return 0.0
        
        labor_cost = float(rework.labor_cost or 0)
        material_cost = float(rework.material_cost or 0)
        
        return labor_cost + material_cost
    
    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get rework operation statistics"""
        query = self.db.query(ReworkOperation)
        
        if start_date:
            query = query.filter(ReworkOperation.created_at >= start_date)
        if end_date:
            query = query.filter(ReworkOperation.created_at <= end_date)
        
        total = query.count()
        pending = query.filter(ReworkOperation.status == 'pending').count()
        in_progress = query.filter(ReworkOperation.status == 'in_progress').count()
        completed = query.filter(ReworkOperation.status == 'completed').count()
        
        # Calculate average duration for completed rework
        completed_rework = query.filter(
            ReworkOperation.status == 'completed',
            ReworkOperation.actual_duration_minutes.isnot(None)
        ).all()
        
        if completed_rework:
            avg_duration = sum([r.actual_duration_minutes for r in completed_rework]) / len(completed_rework)
        else:
            avg_duration = 0
        
        # Calculate total costs
        total_labor_cost = self.db.query(
            func.sum(ReworkOperation.labor_cost)
        ).filter(
            ReworkOperation.labor_cost.isnot(None)
        ).scalar() or 0
        
        total_material_cost = self.db.query(
            func.sum(ReworkOperation.material_cost)
        ).filter(
            ReworkOperation.material_cost.isnot(None)
        ).scalar() or 0
        
        return {
            "total": total,
            "by_status": {
                "pending": pending,
                "in_progress": in_progress,
                "completed": completed
            },
            "avg_duration_minutes": round(avg_duration, 1),
            "total_labor_cost": float(total_labor_cost),
            "total_material_cost": float(total_material_cost),
            "total_cost": float(total_labor_cost + total_material_cost)
        }
