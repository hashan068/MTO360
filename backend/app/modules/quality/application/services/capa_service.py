"""
CAPA (Corrective Action) Service - Application Layer
Business logic for CAPA management
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.quality import CorrectiveAction, CAPAStatusEnum, ActionTypeEnum
from app.schemas.quality import (
    CAPACreate,
    CAPAUpdate,
    CAPAVerify,
    CAPAClose,
    ActionItemSchema,
)
from app.modules.quality.infra.repositories import CAPARepository


class CAPAService:
    """Service for managing CAPA lifecycle"""
    
    def __init__(self, db: Session):
        self.db = db
        self.capa_repo = CAPARepository(db)
    
    # ========== CAPA Management ==========
    
    def create_capa(self, data: CAPACreate) -> CorrectiveAction:
        """
        Create a new CAPA
        Business logic:
        - Auto-generates CAPA number
        - Sets default status to 'open'
        - Can link to NCR or defect
        - Notifies owner
        """
        capa_data = data.model_dump()
        capa_data['status'] = CAPAStatusEnum.OPEN
        
        # Convert ActionItemSchema to dict for JSON storage
        if capa_data.get('corrective_actions'):
            capa_data['corrective_actions'] = [
                action.model_dump() if isinstance(action, ActionItemSchema) else action
                for action in capa_data['corrective_actions']
            ]
        
        if capa_data.get('preventive_actions'):
            capa_data['preventive_actions'] = [
                action.model_dump() if isinstance(action, ActionItemSchema) else action
                for action in capa_data['preventive_actions']
            ]
        
        capa = self.capa_repo.create(**capa_data)
        
        # TODO: Notify owner
        self._notify_capa_assignment(capa)
        
        return capa
    
    def get_capa(self, capa_id: int) -> Optional[CorrectiveAction]:
        """Get CAPA by ID"""
        return self.capa_repo.get_by_id(capa_id)
    
    def get_capa_by_number(self, capa_number: str) -> Optional[CorrectiveAction]:
        """Get CAPA by number"""
        return self.capa_repo.get_by_number(capa_number)
    
    def list_capas(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[CorrectiveAction]:
        """List all CAPAs"""
        return self.capa_repo.get_all(skip=skip, limit=limit)
    
    def get_capas_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CorrectiveAction]:
        """Get CAPAs by status"""
        return self.capa_repo.get_by_status(status, skip=skip, limit=limit)
    
    def get_my_capas(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[CorrectiveAction]:
        """Get CAPAs assigned to an owner"""
        return self.capa_repo.get_by_owner(owner_id, skip=skip, limit=limit)
    
    def update_capa(
        self,
        capa_id: int,
        data: CAPAUpdate
    ) -> Optional[CorrectiveAction]:
        """Update CAPA"""
        update_data = data.model_dump(exclude_unset=True)
        
        # Convert ActionItemSchema to dict
        if 'corrective_actions' in update_data and update_data['corrective_actions']:
            update_data['corrective_actions'] = [
                action.model_dump() if isinstance(action, ActionItemSchema) else action
                for action in update_data['corrective_actions']
            ]
        
        if 'preventive_actions' in update_data and update_data['preventive_actions']:
            update_data['preventive_actions'] = [
                action.model_dump() if isinstance(action, ActionItemSchema) else action
                for action in update_data['preventive_actions']
            ]
        
        return self.capa_repo.update(capa_id, **update_data)
    
    # ========== CAPA Workflow ==========
    
    def start_work(self, capa_id: int) -> Optional[CorrectiveAction]:
        """Start working on CAPA"""
        return self.capa_repo.update(
            capa_id,
            status=CAPAStatusEnum.IN_PROGRESS
        )
    
    def submit_for_verification(self, capa_id: int) -> Optional[CorrectiveAction]:
        """Submit CAPA for effectiveness verification"""
        capa = self.capa_repo.get_by_id(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        # Check if all actions are completed
        completion = self.capa_repo.get_completion_status(capa_id)
        if completion['overall']['percentage'] < 100:
            raise ValueError(
                f"Cannot submit for verification. Only {completion['overall']['percentage']}% of actions completed"
            )
        
        return self.capa_repo.update(
            capa_id,
            status=CAPAStatusEnum.VERIFICATION
        )
    
    def verify_capa(
        self,
        capa_id: int,
        data: CAPAVerify
    ) -> Optional[CorrectiveAction]:
        """
        Verify CAPA effectiveness
        Business logic:
        - Validates all actions completed
        - Records verification details
        - Changes status to verified
        """
        capa = self.capa_repo.get_by_id(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        if capa.status != CAPAStatusEnum.VERIFICATION:
            raise ValueError(f"CAPA must be in verification status. Current: {capa.status.value}")
        
        return self.capa_repo.update(
            capa_id,
            status=CAPAStatusEnum.VERIFIED,
            effectiveness_verification=data.effectiveness_verification,
            verification_date=datetime.utcnow(),
            verified_by_id=data.verified_by_id
        )
    
    def close_capa(
        self,
        capa_id: int,
        data: CAPAClose
    ) -> Optional[CorrectiveAction]:
        """Close a verified CAPA"""
        capa = self.capa_repo.get_by_id(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        if capa.status != CAPAStatusEnum.VERIFIED:
            raise ValueError(f"CAPA must be verified before closure. Current: {capa.status.value}")
        
        return self.capa_repo.update(
            capa_id,
            status=CAPAStatusEnum.CLOSED,
            closed_date=datetime.utcnow(),
            closed_by_id=data.closed_by_id
        )
    
    # ========== Action Item Management ==========
    
    def add_action(
        self,
        capa_id: int,
        action: ActionItemSchema,
        action_type: str = 'corrective'  # 'corrective' or 'preventive'
    ) -> Optional[CorrectiveAction]:
        """Add an action item to CAPA"""
        capa = self.capa_repo.get_by_id(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        action_dict = action.model_dump()
        
        if action_type == 'corrective':
            actions = capa.corrective_actions or []
            actions.append(action_dict)
            return self.capa_repo.update(capa_id, corrective_actions=actions)
        else:
            actions = capa.preventive_actions or []
            actions.append(action_dict)
            return self.capa_repo.update(capa_id, preventive_actions=actions)
    
    def update_action_status(
        self,
        capa_id: int,
        action_id: str,
        status: str,
        completed_date: Optional[str] = None
    ) -> Optional[CorrectiveAction]:
        """Update status of an action item"""
        capa = self.capa_repo.get_by_id(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        # Update in corrective actions
        if capa.corrective_actions:
            for action in capa.corrective_actions:
                if action.get('id') == action_id:
                    action['status'] = status
                    if status == 'completed' and completed_date:
                        action['completed_date'] = completed_date
                    return self.capa_repo.update(
                        capa_id,
                        corrective_actions=capa.corrective_actions
                    )
        
        # Update in preventive actions
        if capa.preventive_actions:
            for action in capa.preventive_actions:
                if action.get('id') == action_id:
                    action['status'] = status
                    if status == 'completed' and completed_date:
                        action['completed_date'] = completed_date
                    return self.capa_repo.update(
                        capa_id,
                        preventive_actions=capa.preventive_actions
                    )
        
        raise ValueError(f"Action {action_id} not found in CAPA {capa_id}")
    
    # ========== Analytics ==========
    
    def get_overdue_capas(self) -> List[CorrectiveAction]:
        """Get CAPAs with overdue actions"""
        return self.capa_repo.get_overdue()
    
    def get_pending_verification(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[CorrectiveAction]:
        """Get CAPAs pending verification"""
        return self.capa_repo.get_pending_verification(skip=skip, limit=limit)
    
    def calculate_capa_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate CAPA metrics"""
        return self.capa_repo.calculate_metrics(
            start_date=start_date,
            end_date=end_date
        )
    
    def get_completion_status(self, capa_id: int) -> Dict[str, Any]:
        """Get completion status of CAPA actions"""
        return self.capa_repo.get_completion_status(capa_id)
    
    def get_action_items(self, capa_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Get all action items for a CAPA"""
        return self.capa_repo.get_action_items(capa_id)
    
    # ========== Private Helper Methods ==========
    
    def _notify_capa_assignment(self, capa: CorrectiveAction) -> None:
        """Send notification for CAPA assignment"""
        # TODO: Integrate with notification service
        pass
