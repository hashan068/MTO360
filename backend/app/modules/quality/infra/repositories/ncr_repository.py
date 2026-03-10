"""
NCR (Non-Conformance Report) Repository - Infrastructure Layer
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from app.models.quality import NonConformanceReport, NCRStatusEnum
from app.modules.quality.domain.interfaces import NCRRepositoryProtocol


class NCRRepository(NCRRepositoryProtocol):
    """Repository for NonConformanceReport entity"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> NonConformanceReport:
        """Create a new NCR"""
        # Generate NCR number if not provided
        if 'ncr_number' not in kwargs:
            kwargs['ncr_number'] = self.generate_ncr_number()
        
        ncr = NonConformanceReport(**kwargs)
        self.db.add(ncr)
        self.db.commit()
        self.db.refresh(ncr)
        return ncr
    
    def get_by_id(self, ncr_id: int) -> Optional[NonConformanceReport]:
        """Get NCR by ID with relationships"""
        return self.db.query(NonConformanceReport).options(
            joinedload(NonConformanceReport.defect),
            joinedload(NonConformanceReport.manufacturing_order),
            joinedload(NonConformanceReport.owner),
            joinedload(NonConformanceReport.created_by),
            joinedload(NonConformanceReport.approver),
            joinedload(NonConformanceReport.closed_by),
        ).filter(
            NonConformanceReport.id == ncr_id
        ).first()
    
    def get_by_number(self, ncr_number: str) -> Optional[NonConformanceReport]:
        """Get NCR by number"""
        return self.db.query(NonConformanceReport).filter(
            NonConformanceReport.ncr_number == ncr_number
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[NonConformanceReport]:
        """Get all NCRs"""
        return self.db.query(NonConformanceReport).options(
            joinedload(NonConformanceReport.owner),
            joinedload(NonConformanceReport.defect),
        ).order_by(NonConformanceReport.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[NonConformanceReport]:
        """Get NCRs by status"""
        return self.db.query(NonConformanceReport).options(
            joinedload(NonConformanceReport.owner),
            joinedload(NonConformanceReport.manufacturing_order),
        ).filter(
            NonConformanceReport.status == status
        ).order_by(NonConformanceReport.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[NonConformanceReport]:
        """Get NCRs by owner"""
        return self.db.query(NonConformanceReport).options(
            joinedload(NonConformanceReport.defect),
            joinedload(NonConformanceReport.manufacturing_order),
        ).filter(
            NonConformanceReport.owner_id == owner_id
        ).order_by(NonConformanceReport.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_priority(self, priority: str, skip: int = 0, limit: int = 100) -> List[NonConformanceReport]:
        """Get NCRs by priority"""
        return self.db.query(NonConformanceReport).options(
            joinedload(NonConformanceReport.owner),
        ).filter(
            NonConformanceReport.priority == priority
        ).order_by(NonConformanceReport.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_overdue(self, days_threshold: int = 7) -> List[NonConformanceReport]:
        """
        Get overdue NCRs
        NCR is considered overdue if:
        - Status is 'open' or 'investigating' for more than days_threshold days
        - Status is 'pending_approval' for more than 3 days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
        approval_cutoff = datetime.utcnow() - timedelta(days=3)
        
        return self.db.query(NonConformanceReport).options(
            joinedload(NonConformanceReport.owner),
            joinedload(NonConformanceReport.manufacturing_order),
        ).filter(
            or_(
                and_(
                    NonConformanceReport.status.in_(['open', 'investigating']),
                    NonConformanceReport.created_at < cutoff_date
                ),
                and_(
                    NonConformanceReport.status == 'pending_approval',
                    NonConformanceReport.created_at < approval_cutoff
                )
            )
        ).all()
    
    def get_pending_approval(self, skip: int = 0, limit: int = 100) -> List[NonConformanceReport]:
        """Get NCRs pending approval"""
        return self.db.query(NonConformanceReport).options(
            joinedload(NonConformanceReport.owner),
            joinedload(NonConformanceReport.manufacturing_order),
        ).filter(
            NonConformanceReport.status == NCRStatusEnum.PENDING_APPROVAL
        ).order_by(NonConformanceReport.created_at.asc()).offset(skip).limit(limit).all()
    
    def search(self, **filters) -> List[NonConformanceReport]:
        """
        Search NCRs with filters
        Supported filters:
        - status: str
        - priority: str
        - owner_id: int
        - defect_id: int
        - manufacturing_order_id: int
        - date_from: datetime
        - date_to: datetime
        - disposition: str
        """
        query = self.db.query(NonConformanceReport).options(
            joinedload(NonConformanceReport.owner),
            joinedload(NonConformanceReport.defect),
            joinedload(NonConformanceReport.manufacturing_order),
        )
        
        if 'status' in filters:
            query = query.filter(NonConformanceReport.status == filters['status'])
        
        if 'priority' in filters:
            query = query.filter(NonConformanceReport.priority == filters['priority'])
        
        if 'owner_id' in filters:
            query = query.filter(NonConformanceReport.owner_id == filters['owner_id'])
        
        if 'defect_id' in filters:
            query = query.filter(NonConformanceReport.defect_id == filters['defect_id'])
        
        if 'manufacturing_order_id' in filters:
            query = query.filter(NonConformanceReport.manufacturing_order_id == filters['manufacturing_order_id'])
        
        if 'disposition' in filters:
            query = query.filter(NonConformanceReport.disposition == filters['disposition'])
        
        if 'date_from' in filters:
            query = query.filter(NonConformanceReport.created_at >= filters['date_from'])
        
        if 'date_to' in filters:
            query = query.filter(NonConformanceReport.created_at <= filters['date_to'])
        
        skip = filters.get('skip', 0)
        limit = filters.get('limit', 100)
        
        return query.order_by(NonConformanceReport.created_at.desc()).offset(skip).limit(limit).all()
    
    def update(self, ncr_id: int, **kwargs) -> Optional[NonConformanceReport]:
        """Update NCR"""
        ncr = self.get_by_id(ncr_id)
        if not ncr:
            return None
        
        for key, value in kwargs.items():
            if hasattr(ncr, key):
                setattr(ncr, key, value)
        
        self.db.commit()
        self.db.refresh(ncr)
        return ncr
    
    def generate_ncr_number(self) -> str:
        """Generate unique NCR number: NCR-YYYYMMDD-XXXX"""
        today = datetime.utcnow().strftime("%Y%m%d")
        prefix = f"NCR-{today}"
        
        # Get the count of NCRs created today
        count = self.db.query(func.count(NonConformanceReport.id)).filter(
            NonConformanceReport.ncr_number.like(f"{prefix}%")
        ).scalar()
        
        sequence = count + 1
        return f"{prefix}-{sequence:04d}"
    
    def calculate_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate NCR metrics"""
        query = self.db.query(NonConformanceReport)
        
        if start_date:
            query = query.filter(NonConformanceReport.created_at >= start_date)
        if end_date:
            query = query.filter(NonConformanceReport.created_at <= end_date)
        
        total = query.count()
        open_ncrs = query.filter(NonConformanceReport.status == 'open').count()
        investigating = query.filter(NonConformanceReport.status == 'investigating').count()
        pending_approval = query.filter(NonConformanceReport.status == 'pending_approval').count()
        approved = query.filter(NonConformanceReport.status == 'approved').count()
        closed = query.filter(NonConformanceReport.status == 'closed').count()
        
        # Calculate average closure time for closed NCRs
        closed_ncrs = query.filter(
            NonConformanceReport.status == 'closed',
            NonConformanceReport.closed_date.isnot(None)
        ).all()
        
        if closed_ncrs:
            total_days = sum([
                (ncr.closed_date - ncr.created_at).days 
                for ncr in closed_ncrs
            ])
            avg_closure_days = total_days / len(closed_ncrs)
        else:
            avg_closure_days = 0
        
        # Cost metrics
        total_cost = self.db.query(
            func.sum(NonConformanceReport.total_cost)
        ).filter(
            NonConformanceReport.total_cost.isnot(None)
        ).scalar() or 0
        
        rework_cost = self.db.query(
            func.sum(NonConformanceReport.rework_cost)
        ).filter(
            NonConformanceReport.rework_cost.isnot(None)
        ).scalar() or 0
        
        scrap_cost = self.db.query(
            func.sum(NonConformanceReport.scrap_cost)
        ).filter(
            NonConformanceReport.scrap_cost.isnot(None)
        ).scalar() or 0
        
        return {
            "total": total,
            "by_status": {
                "open": open_ncrs,
                "investigating": investigating,
                "pending_approval": pending_approval,
                "approved": approved,
                "closed": closed
            },
            "avg_closure_days": round(avg_closure_days, 1),
            "costs": {
                "total": float(total_cost),
                "rework": float(rework_cost),
                "scrap": float(scrap_cost)
            }
        }
    
    def get_aging_report(self) -> List[Dict[str, Any]]:
        """Get NCR aging report"""
        open_ncrs = self.db.query(NonConformanceReport).filter(
            NonConformanceReport.status.in_(['open', 'investigating', 'pending_approval'])
        ).all()
        
        aging_data = []
        for ncr in open_ncrs:
            days_open = (datetime.utcnow() - ncr.created_at).days
            aging_data.append({
                "ncr_id": ncr.id,
                "ncr_number": ncr.ncr_number,
                "status": ncr.status,
                "priority": ncr.priority,
                "days_open": days_open,
                "owner_id": ncr.owner_id,
                "created_at": ncr.created_at
            })
        
        # Sort by days_open descending
        aging_data.sort(key=lambda x: x['days_open'], reverse=True)
        
        return aging_data
