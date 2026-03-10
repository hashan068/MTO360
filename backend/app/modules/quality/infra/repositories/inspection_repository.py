"""
Inspection Repositories - Infrastructure Layer
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.quality import InspectionPoint, InspectionResult
from app.modules.quality.domain.interfaces import (
    InspectionPointRepositoryProtocol,
    InspectionResultRepositoryProtocol,
)


class InspectionPointRepository(InspectionPointRepositoryProtocol):
    """Repository for InspectionPoint entity"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> InspectionPoint:
        """Create a new inspection point"""
        inspection_point = InspectionPoint(**kwargs)
        self.db.add(inspection_point)
        self.db.commit()
        self.db.refresh(inspection_point)
        return inspection_point
    
    def get_by_id(self, inspection_point_id: int) -> Optional[InspectionPoint]:
        """Get inspection point by ID"""
        return self.db.query(InspectionPoint).filter(
            InspectionPoint.id == inspection_point_id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[InspectionPoint]:
        """Get all inspection points"""
        return self.db.query(InspectionPoint).offset(skip).limit(limit).all()
    
    def get_by_route_operation(self, route_operation_id: int) -> List[InspectionPoint]:
        """Get inspection points by route operation"""
        return self.db.query(InspectionPoint).filter(
            InspectionPoint.route_operation_id == route_operation_id
        ).all()
    
    def get_by_type(self, inspection_type: str) -> List[InspectionPoint]:
        """Get inspection points by type"""
        return self.db.query(InspectionPoint).filter(
            InspectionPoint.inspection_type == inspection_type
        ).all()
    
    def update(self, inspection_point_id: int, **kwargs) -> Optional[InspectionPoint]:
        """Update inspection point"""
        inspection_point = self.get_by_id(inspection_point_id)
        if not inspection_point:
            return None
        
        for key, value in kwargs.items():
            if hasattr(inspection_point, key):
                setattr(inspection_point, key, value)
        
        self.db.commit()
        self.db.refresh(inspection_point)
        return inspection_point
    
    def delete(self, inspection_point_id: int) -> bool:
        """Delete inspection point"""
        inspection_point = self.get_by_id(inspection_point_id)
        if not inspection_point:
            return False
        
        self.db.delete(inspection_point)
        self.db.commit()
        return True


class InspectionResultRepository(InspectionResultRepositoryProtocol):
    """Repository for InspectionResult entity"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> InspectionResult:
        """Create a new inspection result"""
        if 'inspection_date' not in kwargs:
            kwargs['inspection_date'] = datetime.utcnow()
        
        inspection_result = InspectionResult(**kwargs)
        self.db.add(inspection_result)
        self.db.commit()
        self.db.refresh(inspection_result)
        return inspection_result
    
    def get_by_id(self, inspection_result_id: int) -> Optional[InspectionResult]:
        """Get inspection result by ID with relationships"""
        return self.db.query(InspectionResult).options(
            joinedload(InspectionResult.inspection_point),
            joinedload(InspectionResult.inspector),
            joinedload(InspectionResult.mo_operation),
            joinedload(InspectionResult.manufacturing_order),
        ).filter(
            InspectionResult.id == inspection_result_id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[InspectionResult]:
        """Get all inspection results"""
        return self.db.query(InspectionResult).options(
            joinedload(InspectionResult.inspection_point),
            joinedload(InspectionResult.inspector),
        ).offset(skip).limit(limit).all()
    
    def get_by_inspector(self, inspector_id: int, skip: int = 0, limit: int = 100) -> List[InspectionResult]:
        """Get inspection results by inspector"""
        return self.db.query(InspectionResult).options(
            joinedload(InspectionResult.inspection_point),
            joinedload(InspectionResult.mo_operation),
        ).filter(
            InspectionResult.inspector_id == inspector_id
        ).order_by(InspectionResult.inspection_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_mo_operation(self, mo_operation_id: int) -> List[InspectionResult]:
        """Get inspection results by MO operation"""
        return self.db.query(InspectionResult).options(
            joinedload(InspectionResult.inspection_point),
            joinedload(InspectionResult.inspector),
        ).filter(
            InspectionResult.mo_operation_id == mo_operation_id
        ).all()
    
    def get_by_manufacturing_order(self, manufacturing_order_id: int) -> List[InspectionResult]:
        """Get inspection results by manufacturing order"""
        return self.db.query(InspectionResult).options(
            joinedload(InspectionResult.inspection_point),
            joinedload(InspectionResult.inspector),
        ).filter(
            InspectionResult.manufacturing_order_id == manufacturing_order_id
        ).all()
    
    def get_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[InspectionResult]:
        """Get inspection results within date range"""
        return self.db.query(InspectionResult).options(
            joinedload(InspectionResult.inspection_point),
            joinedload(InspectionResult.inspector),
        ).filter(
            and_(
                InspectionResult.inspection_date >= start_date,
                InspectionResult.inspection_date <= end_date
            )
        ).order_by(InspectionResult.inspection_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_result(self, result: str, skip: int = 0, limit: int = 100) -> List[InspectionResult]:
        """Get inspection results by result (pass/fail/conditional)"""
        return self.db.query(InspectionResult).options(
            joinedload(InspectionResult.inspection_point),
            joinedload(InspectionResult.inspector),
        ).filter(
            InspectionResult.result == result
        ).order_by(InspectionResult.inspection_date.desc()).offset(skip).limit(limit).all()
    
    def get_pending_for_mo_operation(self, mo_operation_id: int) -> List[InspectionResult]:
        """Get pending inspections for a specific MO operation"""
        # This would require inspection points to be defined first
        # Returns inspections that haven't been completed yet
        return self.db.query(InspectionResult).options(
            joinedload(InspectionResult.inspection_point),
        ).filter(
            InspectionResult.mo_operation_id == mo_operation_id,
            InspectionResult.result.is_(None)
        ).all()
    
    def update(self, inspection_result_id: int, **kwargs) -> Optional[InspectionResult]:
        """Update inspection result"""
        inspection_result = self.get_by_id(inspection_result_id)
        if not inspection_result:
            return None
        
        for key, value in kwargs.items():
            if hasattr(inspection_result, key):
                setattr(inspection_result, key, value)
        
        self.db.commit()
        self.db.refresh(inspection_result)
        return inspection_result
    
    def calculate_pass_rate(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        inspector_id: Optional[int] = None,
        mo_operation_id: Optional[int] = None
    ) -> dict:
        """Calculate inspection pass rate with filters"""
        query = self.db.query(InspectionResult)
        
        if start_date:
            query = query.filter(InspectionResult.inspection_date >= start_date)
        if end_date:
            query = query.filter(InspectionResult.inspection_date <= end_date)
        if inspector_id:
            query = query.filter(InspectionResult.inspector_id == inspector_id)
        if mo_operation_id:
            query = query.filter(InspectionResult.mo_operation_id == mo_operation_id)
        
        total = query.count()
        passed = query.filter(InspectionResult.result == 'pass').count()
        failed = query.filter(InspectionResult.result == 'fail').count()
        conditional = query.filter(InspectionResult.result == 'conditional').count()
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "conditional": conditional,
            "pass_rate": round(pass_rate, 2)
        }
