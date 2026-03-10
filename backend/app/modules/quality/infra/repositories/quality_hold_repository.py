"""
Quality Hold Repository - Infrastructure Layer
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func

from app.models.quality import QualityHold, HoldStatusEnum, HoldTypeEnum
from app.modules.quality.domain.interfaces import QualityHoldRepositoryProtocol


class QualityHoldRepository(QualityHoldRepositoryProtocol):
    """Repository for QualityHold entity"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> QualityHold:
        """Create a new quality hold"""
        # Generate hold number if not provided
        if 'hold_number' not in kwargs:
            kwargs['hold_number'] = self.generate_hold_number()
        
        # Set placed_date if not provided
        if 'placed_date' not in kwargs:
            kwargs['placed_date'] = datetime.utcnow()
        
        hold = QualityHold(**kwargs)
        self.db.add(hold)
        self.db.commit()
        self.db.refresh(hold)
        return hold
    
    def get_by_id(self, hold_id: int) -> Optional[QualityHold]:
        """Get quality hold by ID with relationships"""
        return self.db.query(QualityHold).options(
            joinedload(QualityHold.ncr),
            joinedload(QualityHold.component),
            joinedload(QualityHold.manufacturing_order),
            joinedload(QualityHold.sales_order),
            joinedload(QualityHold.placed_by),
            joinedload(QualityHold.released_by),
        ).filter(
            QualityHold.id == hold_id
        ).first()
    
    def get_by_number(self, hold_number: str) -> Optional[QualityHold]:
        """Get quality hold by number"""
        return self.db.query(QualityHold).filter(
            QualityHold.hold_number == hold_number
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[QualityHold]:
        """Get all quality holds"""
        return self.db.query(QualityHold).options(
            joinedload(QualityHold.ncr),
            joinedload(QualityHold.placed_by),
        ).order_by(QualityHold.placed_date.desc()).offset(skip).limit(limit).all()
    
    def get_active(self, hold_type: Optional[str] = None) -> List[QualityHold]:
        """Get active quality holds, optionally filtered by type"""
        query = self.db.query(QualityHold).options(
            joinedload(QualityHold.ncr),
            joinedload(QualityHold.component),
            joinedload(QualityHold.manufacturing_order),
            joinedload(QualityHold.sales_order),
            joinedload(QualityHold.placed_by),
        ).filter(
            QualityHold.status == HoldStatusEnum.ACTIVE
        )
        
        if hold_type:
            query = query.filter(QualityHold.hold_type == hold_type)
        
        return query.order_by(QualityHold.placed_date.desc()).all()
    
    def get_by_ncr(self, ncr_id: int) -> List[QualityHold]:
        """Get quality holds by NCR"""
        return self.db.query(QualityHold).options(
            joinedload(QualityHold.component),
            joinedload(QualityHold.manufacturing_order),
            joinedload(QualityHold.sales_order),
        ).filter(
            QualityHold.ncr_id == ncr_id
        ).all()
    
    def check_hold_on_entity(self, entity_type: str, entity_id: int) -> Optional[QualityHold]:
        """
        Check if an entity has an active hold
        entity_type: 'component', 'manufacturing_order', 'sales_order'
        """
        query = self.db.query(QualityHold).filter(
            QualityHold.status == HoldStatusEnum.ACTIVE
        )
        
        if entity_type == 'component':
            query = query.filter(QualityHold.component_id == entity_id)
        elif entity_type == 'manufacturing_order':
            query = query.filter(QualityHold.manufacturing_order_id == entity_id)
        elif entity_type == 'sales_order':
            query = query.filter(QualityHold.sales_order_id == entity_id)
        else:
            return None
        
        return query.first()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[QualityHold]:
        """Get quality holds by status"""
        return self.db.query(QualityHold).options(
            joinedload(QualityHold.ncr),
            joinedload(QualityHold.placed_by),
            joinedload(QualityHold.released_by),
        ).filter(
            QualityHold.status == status
        ).order_by(QualityHold.placed_date.desc()).offset(skip).limit(limit).all()
    
    def get_by_type(self, hold_type: str, skip: int = 0, limit: int = 100) -> List[QualityHold]:
        """Get quality holds by type"""
        return self.db.query(QualityHold).options(
            joinedload(QualityHold.ncr),
            joinedload(QualityHold.placed_by),
        ).filter(
            QualityHold.hold_type == hold_type
        ).order_by(QualityHold.placed_date.desc()).offset(skip).limit(limit).all()
    
    def update(self, hold_id: int, **kwargs) -> Optional[QualityHold]:
        """Update quality hold"""
        hold = self.get_by_id(hold_id)
        if not hold:
            return None
        
        for key, value in kwargs.items():
            if hasattr(hold, key):
                setattr(hold, key, value)
        
        self.db.commit()
        self.db.refresh(hold)
        return hold
    
    def generate_hold_number(self) -> str:
        """Generate unique quality hold number: QH-YYYYMMDD-XXXX"""
        today = datetime.utcnow().strftime("%Y%m%d")
        prefix = f"QH-{today}"
        
        # Get the count of holds created today
        count = self.db.query(func.count(QualityHold.id)).filter(
            QualityHold.hold_number.like(f"{prefix}%")
        ).scalar()
        
        sequence = count + 1
        return f"{prefix}-{sequence:04d}"
    
    def get_hold_duration_report(self) -> List[dict]:
        """Get report of hold durations"""
        all_holds = self.db.query(QualityHold).filter(
            QualityHold.status.in_([HoldStatusEnum.ACTIVE, HoldStatusEnum.RELEASED])
        ).all()
        
        report = []
        for hold in all_holds:
            if hold.status == HoldStatusEnum.ACTIVE:
                duration_days = (datetime.utcnow() - hold.placed_date).days
            else:
                if hold.released_date:
                    duration_days = (hold.released_date - hold.placed_date).days
                else:
                    duration_days = 0
            
            report.append({
                "hold_id": hold.id,
                "hold_number": hold.hold_number,
                "hold_type": hold.hold_type,
                "status": hold.status,
                "duration_days": duration_days,
                "quantity_held": hold.quantity_held,
                "placed_date": hold.placed_date,
                "released_date": hold.released_date
            })
        
        return report
    
    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get quality hold statistics"""
        query = self.db.query(QualityHold)
        
        if start_date:
            query = query.filter(QualityHold.placed_date >= start_date)
        if end_date:
            query = query.filter(QualityHold.placed_date <= end_date)
        
        total = query.count()
        active = query.filter(QualityHold.status == HoldStatusEnum.ACTIVE).count()
        released = query.filter(QualityHold.status == HoldStatusEnum.RELEASED).count()
        cancelled = query.filter(QualityHold.status == HoldStatusEnum.CANCELLED).count()
        
        # By type
        inventory = query.filter(QualityHold.hold_type == HoldTypeEnum.INVENTORY).count()
        mo = query.filter(QualityHold.hold_type == HoldTypeEnum.MANUFACTURING_ORDER).count()
        so = query.filter(QualityHold.hold_type == HoldTypeEnum.SALES_ORDER).count()
        
        # Calculate average hold duration for released holds
        released_holds = query.filter(
            QualityHold.status == HoldStatusEnum.RELEASED,
            QualityHold.released_date.isnot(None)
        ).all()
        
        if released_holds:
            total_days = sum([
                (hold.released_date - hold.placed_date).days 
                for hold in released_holds
            ])
            avg_duration = total_days / len(released_holds)
        else:
            avg_duration = 0
        
        return {
            "total": total,
            "by_status": {
                "active": active,
                "released": released,
                "cancelled": cancelled
            },
            "by_type": {
                "inventory": inventory,
                "manufacturing_order": mo,
                "sales_order": so
            },
            "avg_hold_duration_days": round(avg_duration, 1)
        }
