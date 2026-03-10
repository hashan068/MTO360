"""
Quality Hold Service - Application Layer
Business logic for quality hold management
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.quality import QualityHold, HoldStatusEnum, HoldTypeEnum
from app.schemas.quality import QualityHoldCreate, QualityHoldRelease
from app.modules.quality.infra.repositories import QualityHoldRepository


class QualityHoldService:
    """Service for managing quality holds"""
    
    def __init__(self, db: Session):
        self.db = db
        self.quality_hold_repo = QualityHoldRepository(db)
    
    # ========== Quality Hold Management ==========
    
    def place_hold(self, data: QualityHoldCreate) -> QualityHold:
        """
        Place a quality hold
        Business logic:
        - Auto-generates hold number
        - Sets placed date
        - Validates entity exists
        - Blocks operations/shipments based on hold type
        - Sends notifications
        """
        # Validate entity exists based on hold type
        self._validate_hold_entity(data.hold_type, data)
        
        hold_data = data.model_dump()
        hold_data['status'] = HoldStatusEnum.ACTIVE
        
        hold = self.quality_hold_repo.create(**hold_data)
        
        # Update affected entity status
        self._apply_hold_to_entity(hold)
        
        # TODO: Send notification
        self._notify_hold_placed(hold)
        
        return hold
    
    def get_hold(self, hold_id: int) -> Optional[QualityHold]:
        """Get quality hold by ID"""
        return self.quality_hold_repo.get_by_id(hold_id)
    
    def get_hold_by_number(self, hold_number: str) -> Optional[QualityHold]:
        """Get quality hold by number"""
        return self.quality_hold_repo.get_by_number(hold_number)
    
    def list_holds(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[QualityHold]:
        """List all quality holds"""
        return self.quality_hold_repo.get_all(skip=skip, limit=limit)
    
    def get_active_holds(
        self,
        hold_type: Optional[str] = None
    ) -> List[QualityHold]:
        """Get active quality holds, optionally filtered by type"""
        return self.quality_hold_repo.get_active(hold_type=hold_type)
    
    def get_holds_by_ncr(self, ncr_id: int) -> List[QualityHold]:
        """Get all holds for an NCR"""
        return self.quality_hold_repo.get_by_ncr(ncr_id)
    
    # ========== Hold Release ==========
    
    def release_hold(
        self,
        hold_id: int,
        data: QualityHoldRelease
    ) -> Optional[QualityHold]:
        """
        Release a quality hold
        Business logic:
        - Validates hold is active
        - Sets released date and releaser
        - Updates entity status
        - Sends notifications
        """
        hold = self.quality_hold_repo.get_by_id(hold_id)
        if not hold:
            raise ValueError(f"Quality hold {hold_id} not found")
        
        if hold.status != HoldStatusEnum.ACTIVE:
            raise ValueError(f"Hold must be active to release. Current status: {hold.status.value}")
        
        released_hold = self.quality_hold_repo.update(
            hold_id,
            status=HoldStatusEnum.RELEASED,
            released_by_id=data.released_by_id,
            released_date=datetime.utcnow(),
            release_reason=data.release_reason
        )
        
        # Update affected entity status
        if released_hold:
            self._remove_hold_from_entity(released_hold)
            # TODO: Send notification
            self._notify_hold_released(released_hold)
        
        return released_hold
    
    def cancel_hold(
        self,
        hold_id: int,
        cancelled_by_id: int,
        reason: str
    ) -> Optional[QualityHold]:
        """Cancel a quality hold"""
        hold = self.quality_hold_repo.get_by_id(hold_id)
        if not hold:
            raise ValueError(f"Quality hold {hold_id} not found")
        
        cancelled_hold = self.quality_hold_repo.update(
            hold_id,
            status=HoldStatusEnum.CANCELLED,
            released_by_id=cancelled_by_id,
            released_date=datetime.utcnow(),
            release_reason=f"Cancelled: {reason}"
        )
        
        if cancelled_hold:
            self._remove_hold_from_entity(cancelled_hold)
        
        return cancelled_hold
    
    # ========== Hold Checking ==========
    
    def check_hold_status(
        self,
        entity_type: str,
        entity_id: int
    ) -> dict:
        """
        Check if an entity has an active hold
        Returns: {has_hold: bool, hold: QualityHold or None}
        """
        hold = self.quality_hold_repo.check_hold_on_entity(entity_type, entity_id)
        return {
            "has_hold": hold is not None,
            "hold": hold
        }
    
    def is_entity_blocked(
        self,
        entity_type: str,
        entity_id: int
    ) -> bool:
        """Check if entity is blocked by quality hold"""
        result = self.check_hold_status(entity_type, entity_id)
        return result["has_hold"]
    
    def validate_no_hold(
        self,
        entity_type: str,
        entity_id: int,
        operation: str = ""
    ) -> None:
        """
        Validate entity doesn't have active hold
        Raises ValueError if hold exists
        """
        if self.is_entity_blocked(entity_type, entity_id):
            raise ValueError(
                f"Cannot {operation}: {entity_type} {entity_id} has active quality hold"
            )
    
    # ========== Analytics ==========
    
    def get_hold_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get quality hold statistics"""
        return self.quality_hold_repo.get_statistics(
            start_date=start_date,
            end_date=end_date
        )
    
    def get_hold_duration_report(self) -> List[dict]:
        """Get report of hold durations"""
        return self.quality_hold_repo.get_hold_duration_report()
    
    # ========== Private Helper Methods ==========
    
    def _validate_hold_entity(
        self,
        hold_type: HoldTypeEnum,
        data: QualityHoldCreate
    ) -> None:
        """Validate that the referenced entity exists"""
        # TODO: Add validation logic
        # Check if component/MO/SO exists based on hold_type
        pass
    
    def _apply_hold_to_entity(self, hold: QualityHold) -> None:
        """Apply hold status to the affected entity"""
        from app.models.manufacturing import ManufacturingOrder, ManufacturingOrderOperation
        
        if hold.hold_type == HoldTypeEnum.MANUFACTURING_ORDER and hold.manufacturing_order_id:
            # Set quality hold on MO
            mo = self.db.query(ManufacturingOrder).filter(
                ManufacturingOrder.id == hold.manufacturing_order_id
            ).first()
            if mo:
                # Mark all operations as having quality hold
                for op in mo.operations:
                    op.quality_hold = True
                self.db.commit()
        
        # TODO: Handle inventory and sales order holds
    
    def _remove_hold_from_entity(self, hold: QualityHold) -> None:
        """Remove hold status from the affected entity"""
        from app.models.manufacturing import ManufacturingOrder
        
        if hold.hold_type == HoldTypeEnum.MANUFACTURING_ORDER and hold.manufacturing_order_id:
            # Check if there are other active holds on this MO
            other_holds = self.quality_hold_repo.check_hold_on_entity(
                'manufacturing_order',
                hold.manufacturing_order_id
            )
            
            if not other_holds:
                # No other holds, remove quality hold flag
                mo = self.db.query(ManufacturingOrder).filter(
                    ManufacturingOrder.id == hold.manufacturing_order_id
                ).first()
                if mo:
                    for op in mo.operations:
                        op.quality_hold = False
                    self.db.commit()
    
    def _notify_hold_placed(self, hold: QualityHold) -> None:
        """Send notification when hold is placed"""
        # TODO: Integrate with notification service
        pass
    
    def _notify_hold_released(self, hold: QualityHold) -> None:
        """Send notification when hold is released"""
        # TODO: Integrate with notification service
        pass
