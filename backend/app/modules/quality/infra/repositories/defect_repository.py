"""
Defect Repository - Infrastructure Layer
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from app.models.quality import Defect
from app.modules.quality.domain.interfaces import DefectRepositoryProtocol


class DefectRepository(DefectRepositoryProtocol):
    """Repository for Defect entity"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> Defect:
        """Create a new defect"""
        # Generate defect number if not provided
        if 'defect_number' not in kwargs:
            kwargs['defect_number'] = self.generate_defect_number()
        
        defect = Defect(**kwargs)
        self.db.add(defect)
        self.db.commit()
        self.db.refresh(defect)
        return defect
    
    def get_by_id(self, defect_id: int) -> Optional[Defect]:
        """Get defect by ID with relationships"""
        return self.db.query(Defect).options(
            joinedload(Defect.manufacturing_order),
            joinedload(Defect.mo_operation),
            joinedload(Defect.inspection_result),
            joinedload(Defect.reported_by),
            joinedload(Defect.operator),
            joinedload(Defect.supplier),
        ).filter(
            Defect.id == defect_id
        ).first()
    
    def get_by_number(self, defect_number: str) -> Optional[Defect]:
        """Get defect by number"""
        return self.db.query(Defect).filter(
            Defect.defect_number == defect_number
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Defect]:
        """Get all defects"""
        return self.db.query(Defect).options(
            joinedload(Defect.reported_by),
            joinedload(Defect.manufacturing_order),
        ).order_by(Defect.created_at.desc()).offset(skip).limit(limit).all()
    
    def search(self, **filters) -> List[Defect]:
        """
        Search defects with filters
        Supported filters:
        - defect_type: str
        - severity: str
        - status: str
        - responsible_party: str
        - manufacturing_order_id: int
        - operator_id: int
        - supplier_id: int
        - date_from: datetime
        - date_to: datetime
        - defect_category: str
        """
        query = self.db.query(Defect).options(
            joinedload(Defect.reported_by),
            joinedload(Defect.manufacturing_order),
            joinedload(Defect.operator),
            joinedload(Defect.supplier),
        )
        
        if 'defect_type' in filters:
            query = query.filter(Defect.defect_type == filters['defect_type'])
        
        if 'severity' in filters:
            query = query.filter(Defect.severity == filters['severity'])
        
        if 'status' in filters:
            query = query.filter(Defect.status == filters['status'])
        
        if 'responsible_party' in filters:
            query = query.filter(Defect.responsible_party == filters['responsible_party'])
        
        if 'manufacturing_order_id' in filters:
            query = query.filter(Defect.manufacturing_order_id == filters['manufacturing_order_id'])
        
        if 'operator_id' in filters:
            query = query.filter(Defect.operator_id == filters['operator_id'])
        
        if 'supplier_id' in filters:
            query = query.filter(Defect.supplier_id == filters['supplier_id'])
        
        if 'defect_category' in filters:
            query = query.filter(Defect.defect_category.ilike(f"%{filters['defect_category']}%"))
        
        if 'date_from' in filters:
            query = query.filter(Defect.created_at >= filters['date_from'])
        
        if 'date_to' in filters:
            query = query.filter(Defect.created_at <= filters['date_to'])
        
        # Pagination
        skip = filters.get('skip', 0)
        limit = filters.get('limit', 100)
        
        return query.order_by(Defect.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_mo(self, manufacturing_order_id: int) -> List[Defect]:
        """Get defects by manufacturing order"""
        return self.db.query(Defect).options(
            joinedload(Defect.reported_by),
            joinedload(Defect.mo_operation),
        ).filter(
            Defect.manufacturing_order_id == manufacturing_order_id
        ).all()
    
    def get_by_operator(self, operator_id: int, skip: int = 0, limit: int = 100) -> List[Defect]:
        """Get defects by operator"""
        return self.db.query(Defect).options(
            joinedload(Defect.manufacturing_order),
            joinedload(Defect.mo_operation),
        ).filter(
            Defect.operator_id == operator_id
        ).order_by(Defect.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_supplier(self, supplier_id: int, skip: int = 0, limit: int = 100) -> List[Defect]:
        """Get defects by supplier"""
        return self.db.query(Defect).options(
            joinedload(Defect.manufacturing_order),
            joinedload(Defect.component),
        ).filter(
            Defect.supplier_id == supplier_id
        ).order_by(Defect.created_at.desc()).offset(skip).limit(limit).all()
    
    def update(self, defect_id: int, **kwargs) -> Optional[Defect]:
        """Update defect"""
        defect = self.get_by_id(defect_id)
        if not defect:
            return None
        
        for key, value in kwargs.items():
            if hasattr(defect, key):
                setattr(defect, key, value)
        
        self.db.commit()
        self.db.refresh(defect)
        return defect
    
    def generate_defect_number(self) -> str:
        """Generate unique defect number: DEF-YYYYMMDD-XXXX"""
        today = datetime.utcnow().strftime("%Y%m%d")
        prefix = f"DEF-{today}"
        
        # Get the count of defects created today
        count = self.db.query(func.count(Defect.id)).filter(
            Defect.defect_number.like(f"{prefix}%")
        ).scalar()
        
        sequence = count + 1
        return f"{prefix}-{sequence:04d}"
    
    def get_defect_trends(
        self,
        group_by: str,  # 'type', 'severity', 'category', 'operator'
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get defect trends grouped by specified field"""
        query = self.db.query(Defect)
        
        if start_date:
            query = query.filter(Defect.created_at >= start_date)
        if end_date:
            query = query.filter(Defect.created_at <= end_date)
        
        if group_by == 'type':
            results = query.group_by(Defect.defect_type).with_entities(
                Defect.defect_type,
                func.count(Defect.id).label('count')
            ).all()
            return [{"category": r[0], "count": r[1]} for r in results]
        
        elif group_by == 'severity':
            results = query.group_by(Defect.severity).with_entities(
                Defect.severity,
                func.count(Defect.id).label('count')
            ).all()
            return [{"category": r[0], "count": r[1]} for r in results]
        
        elif group_by == 'category':
            results = query.group_by(Defect.defect_category).with_entities(
                Defect.defect_category,
                func.count(Defect.id).label('count')
            ).order_by(func.count(Defect.id).desc()).all()
            return [{"category": r[0], "count": r[1]} for r in results]
        
        elif group_by == 'operator':
            results = query.filter(Defect.operator_id.isnot(None)).group_by(Defect.operator_id).with_entities(
                Defect.operator_id,
                func.count(Defect.id).label('count')
            ).order_by(func.count(Defect.id).desc()).all()
            return [{"operator_id": r[0], "count": r[1]} for r in results]
        
        return []
    
    def get_pareto_analysis(
        self,
        metric: str = 'defects',  # 'defects' or 'cost'
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get Pareto analysis (80/20 rule) for defects"""
        query = self.db.query(Defect)
        
        if start_date:
            query = query.filter(Defect.created_at >= start_date)
        if end_date:
            query = query.filter(Defect.created_at <= end_date)
        
        # Group by defect category and count/sum
        results = query.group_by(Defect.defect_category).with_entities(
            Defect.defect_category,
            func.count(Defect.id).label('count'),
            func.sum(Defect.quantity_affected).label('total_quantity')
        ).order_by(func.count(Defect.id).desc()).limit(limit).all()
        
        total_defects = sum([r[1] for r in results])
        
        pareto_data = []
        cumulative = 0
        for category, count, quantity in results:
            cumulative += count
            percentage = (count / total_defects * 100) if total_defects > 0 else 0
            cumulative_percentage = (cumulative / total_defects * 100) if total_defects > 0 else 0
            
            pareto_data.append({
                "category": category,
                "count": count,
                "quantity": quantity or 0,
                "percentage": round(percentage, 2),
                "cumulative_percentage": round(cumulative_percentage, 2)
            })
        
        return pareto_data
    
    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get defect statistics"""
        query = self.db.query(Defect)
        
        if start_date:
            query = query.filter(Defect.created_at >= start_date)
        if end_date:
            query = query.filter(Defect.created_at <= end_date)
        
        total = query.count()
        open_defects = query.filter(Defect.status == 'open').count()
        resolved = query.filter(Defect.status == 'resolved').count()
        closed = query.filter(Defect.status == 'closed').count()
        
        critical = query.filter(Defect.severity == 'critical').count()
        major = query.filter(Defect.severity == 'major').count()
        minor = query.filter(Defect.severity == 'minor').count()
        cosmetic = query.filter(Defect.severity == 'cosmetic').count()
        
        return {
            "total": total,
            "open": open_defects,
            "resolved": resolved,
            "closed": closed,
            "by_severity": {
                "critical": critical,
                "major": major,
                "minor": minor,
                "cosmetic": cosmetic
            }
        }
