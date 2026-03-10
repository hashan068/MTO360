"""
CAPA (Corrective Action) Repository - Infrastructure Layer
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from app.models.quality import CorrectiveAction, CAPAStatusEnum
from app.modules.quality.domain.interfaces import CAPARepositoryProtocol


class CAPARepository(CAPARepositoryProtocol):
    """Repository for CorrectiveAction (CAPA) entity"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, **kwargs) -> CorrectiveAction:
        """Create a new CAPA"""
        # Generate CAPA number if not provided
        if 'capa_number' not in kwargs:
            kwargs['capa_number'] = self.generate_capa_number()
        
        capa = CorrectiveAction(**kwargs)
        self.db.add(capa)
        self.db.commit()
        self.db.refresh(capa)
        return capa
    
    def get_by_id(self, capa_id: int) -> Optional[CorrectiveAction]:
        """Get CAPA by ID with relationships"""
        return self.db.query(CorrectiveAction).options(
            joinedload(CorrectiveAction.ncr),
            joinedload(CorrectiveAction.defect),
            joinedload(CorrectiveAction.owner),
            joinedload(CorrectiveAction.created_by),
            joinedload(CorrectiveAction.verified_by),
            joinedload(CorrectiveAction.closed_by),
        ).filter(
            CorrectiveAction.id == capa_id
        ).first()
    
    def get_by_number(self, capa_number: str) -> Optional[CorrectiveAction]:
        """Get CAPA by number"""
        return self.db.query(CorrectiveAction).filter(
            CorrectiveAction.capa_number == capa_number
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[CorrectiveAction]:
        """Get all CAPAs"""
        return self.db.query(CorrectiveAction).options(
            joinedload(CorrectiveAction.owner),
            joinedload(CorrectiveAction.ncr),
            joinedload(CorrectiveAction.defect),
        ).order_by(CorrectiveAction.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[CorrectiveAction]:
        """Get CAPAs by status"""
        return self.db.query(CorrectiveAction).options(
            joinedload(CorrectiveAction.owner),
            joinedload(CorrectiveAction.ncr),
        ).filter(
            CorrectiveAction.status == status
        ).order_by(CorrectiveAction.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[CorrectiveAction]:
        """Get CAPAs by owner"""
        return self.db.query(CorrectiveAction).options(
            joinedload(CorrectiveAction.ncr),
            joinedload(CorrectiveAction.defect),
        ).filter(
            CorrectiveAction.owner_id == owner_id
        ).order_by(CorrectiveAction.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_action_type(self, action_type: str, skip: int = 0, limit: int = 100) -> List[CorrectiveAction]:
        """Get CAPAs by action type (corrective/preventive)"""
        return self.db.query(CorrectiveAction).options(
            joinedload(CorrectiveAction.owner),
        ).filter(
            CorrectiveAction.action_type == action_type
        ).order_by(CorrectiveAction.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_overdue(self) -> List[CorrectiveAction]:
        """
        Get CAPAs with overdue actions
        Checks if any action items in corrective_actions or preventive_actions have:
        - status not 'completed' AND due_date < today
        """
        all_open_capas = self.db.query(CorrectiveAction).filter(
            CorrectiveAction.status.in_(['open', 'in_progress'])
        ).all()
        
        overdue_capas = []
        today = datetime.utcnow().date()
        
        for capa in all_open_capas:
            has_overdue = False
            
            # Check corrective actions
            if capa.corrective_actions:
                for action in capa.corrective_actions:
                    if (action.get('status') != 'completed' and 
                        action.get('due_date')):
                        try:
                            due_date = datetime.strptime(action['due_date'], '%Y-%m-%d').date()
                            if due_date < today:
                                has_overdue = True
                                break
                        except:
                            pass
            
            # Check preventive actions
            if not has_overdue and capa.preventive_actions:
                for action in capa.preventive_actions:
                    if (action.get('status') != 'completed' and 
                        action.get('due_date')):
                        try:
                            due_date = datetime.strptime(action['due_date'], '%Y-%m-%d').date()
                            if due_date < today:
                                has_overdue = True
                                break
                        except:
                            pass
            
            if has_overdue:
                overdue_capas.append(capa)
        
        return overdue_capas
    
    def get_pending_verification(self, skip: int = 0, limit: int = 100) -> List[CorrectiveAction]:
        """Get CAPAs pending effectiveness verification"""
        return self.db.query(CorrectiveAction).options(
            joinedload(CorrectiveAction.owner),
            joinedload(CorrectiveAction.ncr),
        ).filter(
            CorrectiveAction.status == CAPAStatusEnum.VERIFICATION
        ).order_by(CorrectiveAction.created_at.asc()).offset(skip).limit(limit).all()
    
    def update(self, capa_id: int, **kwargs) -> Optional[CorrectiveAction]:
        """Update CAPA"""
        capa = self.get_by_id(capa_id)
        if not capa:
            return None
        
        for key, value in kwargs.items():
            if hasattr(capa, key):
                setattr(capa, key, value)
        
        self.db.commit()
        self.db.refresh(capa)
        return capa
    
    def generate_capa_number(self) -> str:
        """Generate unique CAPA number: CAPA-YYYYMMDD-XXXX"""
        today = datetime.utcnow().strftime("%Y%m%d")
        prefix = f"CAPA-{today}"
        
        # Get the count of CAPAs created today
        count = self.db.query(func.count(CorrectiveAction.id)).filter(
            CorrectiveAction.capa_number.like(f"{prefix}%")
        ).scalar()
        
        sequence = count + 1
        return f"{prefix}-{sequence:04d}"
    
    def get_action_items(self, capa_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all action items from a CAPA"""
        capa = self.get_by_id(capa_id)
        if not capa:
            return {"corrective_actions": [], "preventive_actions": []}
        
        return {
            "corrective_actions": capa.corrective_actions or [],
            "preventive_actions": capa.preventive_actions or []
        }
    
    def get_completion_status(self, capa_id: int) -> Dict[str, Any]:
        """Get completion status of CAPA action items"""
        capa = self.get_by_id(capa_id)
        if not capa:
            return {}
        
        def calculate_progress(actions):
            if not actions:
                return {"total": 0, "completed": 0, "percentage": 0}
            
            total = len(actions)
            completed = sum(1 for action in actions if action.get('status') == 'completed')
            percentage = (completed / total * 100) if total > 0 else 0
            
            return {
                "total": total,
                "completed": completed,
                "percentage": round(percentage, 1)
            }
        
        corrective_progress = calculate_progress(capa.corrective_actions)
        preventive_progress = calculate_progress(capa.preventive_actions)
        
        total_actions = corrective_progress['total'] + preventive_progress['total']
        total_completed = corrective_progress['completed'] + preventive_progress['completed']
        overall_percentage = (total_completed / total_actions * 100) if total_actions > 0 else 0
        
        return {
            "corrective_actions": corrective_progress,
            "preventive_actions": preventive_progress,
            "overall": {
                "total": total_actions,
                "completed": total_completed,
                "percentage": round(overall_percentage, 1)
            }
        }
    
    def calculate_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate CAPA metrics"""
        query = self.db.query(CorrectiveAction)
        
        if start_date:
            query = query.filter(CorrectiveAction.created_at >= start_date)
        if end_date:
            query = query.filter(CorrectiveAction.created_at <= end_date)
        
        total = query.count()
        open_capas = query.filter(CorrectiveAction.status == 'open').count()
        in_progress = query.filter(CorrectiveAction.status == 'in_progress').count()
        verification = query.filter(CorrectiveAction.status == 'verification').count()
        closed = query.filter(CorrectiveAction.status == 'closed').count()
        
        corrective = query.filter(CorrectiveAction.action_type == 'corrective').count()
        preventive = query.filter(CorrectiveAction.action_type == 'preventive').count()
        
        # Calculate average time to close
        closed_capas = query.filter(
            CorrectiveAction.status == 'closed',
            CorrectiveAction.closed_date.isnot(None)
        ).all()
        
        if closed_capas:
            total_days = sum([
                (capa.closed_date - capa.created_at).days 
                for capa in closed_capas
            ])
            avg_closure_days = total_days / len(closed_capas)
        else:
            avg_closure_days = 0
        
        return {
            "total": total,
            "by_status": {
                "open": open_capas,
                "in_progress": in_progress,
                "verification": verification,
                "closed": closed
            },
            "by_type": {
                "corrective": corrective,
                "preventive": preventive
            },
            "avg_closure_days": round(avg_closure_days, 1)
        }
