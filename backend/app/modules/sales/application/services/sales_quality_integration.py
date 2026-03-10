"""
Sales Quality Integration Helper
Provides quality validation for sales/shipment operations
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.manufacturing import ManufacturingOrder


class AsyncSalesQualityValidator:
    """
    Async quality validation helper for sales/shipment operations
    Ensures quality requirements met before shipment
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def validate_shipment_allowed(
        self, 
        manufacturing_order_id: int
    ) -> Dict[str, Any]:
        """
        Validate if shipment is allowed for a manufacturing order
        Checks:
        1. Final inspection completed and passed
        2. No active quality holds on MO
        
        Returns:
            {
                "can_ship": bool,
                "reason": str (if blocked),
                "quality_status": str,
                "has_hold": bool
            }
        """
        # Get MO
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.id == manufacturing_order_id
        )
        result = await self.db.execute(stmt)
        mo = result.scalar_one_or_none()
        
        if not mo:
            return {
                "can_ship": False,
                "reason": "Manufacturing order not found"
            }
        
        # Check final inspection
        quality_status = mo.quality_status
        
        if not quality_status:
            return {
                "can_ship": False,
                "reason": "Final inspection not completed",
                "quality_status": None,
                "has_hold": False
            }
        
        if quality_status != 'pass':
            return {
                "can_ship": False,
                "reason": f"Final inspection failed (status: {quality_status})",
                "quality_status": quality_status,
                "has_hold": False
            }
        
        # Check for quality holds
        from app.models.quality import QualityHold, HoldStatusEnum
        
        hold_stmt = select(QualityHold).where(
            QualityHold.manufacturing_order_id == manufacturing_order_id,
            QualityHold.status == HoldStatusEnum.ACTIVE
        )
        hold_result = await self.db.execute(hold_stmt)
        hold = hold_result.scalar_one_or_none()
        
        if hold:
            return {
                "can_ship": False,
                "reason": f"Quality hold active: {hold.hold_reason}",
                "quality_status": quality_status,
                "has_hold": True,
                "hold_number": hold.hold_number
            }
        
        return {
            "can_ship": True,
            "quality_status": quality_status,
            "has_hold": False
        }
    
    async def validate_sales_order_shipment(
        self,
        sales_order_id: int
    ) -> Dict[str, Any]:
        """
        Validate if sales order can be shipped
        Checks all linked manufacturing orders
        
        Returns:
            {
                "can_ship": bool,
                "reason": str (if blocked),
                "mo_validations": list of validation results
            }
        """
        # Get all MOs linked to this sales order
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.sales_order_id == sales_order_id
        )
        result = await self.db.execute(stmt)
        mos = result.scalars().all()
        
        if not mos:
            return {
                "can_ship": True,
                "reason": "No manufacturing orders linked (direct sale)"
            }
        
        # Validate each MO
        mo_validations = []
        all_can_ship = True
        block_reasons = []
        
        for mo in mos:
            validation = await self.validate_shipment_allowed(mo.id)
            mo_validations.append({
                "mo_id": mo.id,
                **validation
            })
            
            if not validation["can_ship"]:
                all_can_ship = False
                block_reasons.append(f"MO #{mo.id}: {validation['reason']}")
        
        if not all_can_ship:
            return {
                "can_ship": False,
                "reason": "; ".join(block_reasons),
                "mo_validations": mo_validations
            }
        
        return {
            "can_ship": True,
            "mo_validations": mo_validations
        }
