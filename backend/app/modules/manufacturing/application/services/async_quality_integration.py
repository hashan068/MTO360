"""
Async Quality Integration Helper for Manufacturing Module
Provides quality validation and blocking logic for manufacturing operations
Compatible with AsyncSession
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.manufacturing import ManufacturingOrder, ManufacturingOrderOperation


class AsyncManufacturingQualityValidator:
    """
    Async quality validation helper for manufacturing operations
    Enforces quality requirements in manufacturing workflow
    Compatible with async/await patterns
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def validate_operation_start(
        self, 
        mo_operation_id: int, 
        manufacturing_order_id: int
    ) -> Dict[str, Any]:
        """
        Validate if operation can start
        Checks for quality holds on MO
        
        Returns:
            {
                "can_start": bool,
                "reason": str (if blocked),
                "hold": QualityHold (if blocked)
            }
        """
        # Import here to avoid circular dependencies
        from app.models.quality import QualityHold, HoldStatusEnum
        
        # Check for active quality holds on manufacturing order
        stmt = select(QualityHold).where(
            QualityHold.manufacturing_order_id == manufacturing_order_id,
            QualityHold.status == HoldStatusEnum.ACTIVE
        )
        result = await self.db.execute(stmt)
        hold = result.scalar_one_or_none()
        
        if hold:
            return {
                "can_start": False,
                "reason": f"Quality hold active: {hold.hold_reason}",
                "hold_id": hold.id,
                "hold_number": hold.hold_number
            }
        
        return {"can_start": True}
    
    async def validate_operation_completion(self, mo_operation_id: int) -> Dict[str, Any]:
        """
        Validate if operation can be completed
        Checks:
        1. Quality hold on operation
        2. Required inspection passed
        
        Returns:
            {
                "can_complete": bool,
                "reason": str (if blocked),
                "inspection_status": str,
                "details": dict
            }
        """
        # Get operation
        stmt = select(ManufacturingOrderOperation).where(
            ManufacturingOrderOperation.id == mo_operation_id
        )
        result = await self.db.execute(stmt)
        operation = result.scalar_one_or_none()
        
        if not operation:
            return {
                "can_complete": False,
                "reason": "Operation not found"
            }
        
        # Check if operation has quality hold
        if operation.quality_hold:
            return {
                "can_complete": False,
                "reason": "Operation has active quality hold",
                "inspection_status": operation.inspection_status or "none"
            }
        
        # Check inspection status from operation field
        # Note: InspectionService already updates this field
        inspection_status = operation.inspection_status or "none"
        
        # If inspection failed, block completion
        if inspection_status == 'fail':
            return {
                "can_complete": False,
                "reason": "Inspection failed - rework or NCR required",
                "inspection_status": inspection_status
            }
        
        # If inspections are pending, allow with warning (business decision)
        if inspection_status == 'pending':
            return {
                "can_complete": True,  
                "warning": "Inspection pending but not yet completed",
                "inspection_status": inspection_status
            }
        
        return {
            "can_complete": True,
            "inspection_status": inspection_status
        }
    
    async def check_final_inspection_required(self, manufacturing_order_id: int) -> Dict[str, Any]:
        """
        Check if MO has completed final inspection
        Used before allowing shipment
        
        Returns:
            {
                "has_final_inspection": bool,
                "passed": bool (if has inspection),
                "quality_status": str
            }
        """
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.id == manufacturing_order_id
        )
        result = await self.db.execute(stmt)
        mo = result.scalar_one_or_none()
        
        if not mo:
            return {"has_final_inspection": False, "error": "MO not found"}
        
        # Check quality_status field (set by InspectionService)
        has_inspection = mo.quality_status is not None
        passed = mo.quality_status == 'pass' if has_inspection else False
        
        return {
            "has_final_inspection": has_inspection,
            "passed": passed,
            "quality_status": mo.quality_status
        }
