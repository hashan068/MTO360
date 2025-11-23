"""
Material Availability Service - Check component availability for production
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.inventory import Component
from app.models.manufacturing import BillOfMaterial, BOMItem


class MaterialAvailabilityService:
    """Service for checking material availability for manufacturing"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_bom_availability(
        self, 
        bom_id: int, 
        quantity: int
    ) -> Dict[str, any]:
        """
        Check availability of all components in a BOM for a given quantity.
        
        Args:
            bom_id: Bill of Material ID
            quantity: Quantity to produce
        
        Returns:
            Dict with:
                - all_available: bool - True if all materials available
                - components: List of component availability details
                - missing_components: List of components with insufficient stock
        """
        # Get BOM
        result = await self.db.execute(
            select(BillOfMaterial).where(BillOfMaterial.id == bom_id)
        )
        bom = result.scalar_one_or_none()
        
        if not bom:
            raise ValueError(f"BOM {bom_id} not found")
        
        # Get BOM items
        result = await self.db.execute(
            select(BOMItem).where(BOMItem.bill_of_material_id == bom_id)
        )
        bom_items = result.scalars().all()
        
        if not bom_items:
            return {
                "all_available": True,
                "components": [],
                "missing_components": []
            }
        
        # Check each component
        component_details = []
        missing_components = []
        
        for bom_item in bom_items:
            # Get component details
            result = await self.db.execute(
                select(Component).where(Component.id == bom_item.component_id)
            )
            component = result.scalar_one_or_none()
            
            if not component:
                continue
            
            # Calculate required quantity
            required_qty = bom_item.quantity * quantity
            available_qty = component.quantity_on_hand
            
            is_available = available_qty >= required_qty
            shortage = max(0, required_qty - available_qty)
            
            component_info = {
                "component_id": component.id,
                "component_name": component.name,
                "component_code": component.code,
                "required_quantity": required_qty,
                "available_quantity": available_qty,
                "unit": component.unit,
                "is_available": is_available,
                "shortage": shortage
            }
            
            component_details.append(component_info)
            
            if not is_available:
                missing_components.append(component_info)
        
        return {
            "all_available": len(missing_components) == 0,
            "components": component_details,
            "missing_components": missing_components
        }
    
    async def get_availability_indicators(
        self, 
        component_ids: List[int]
    ) -> Dict[int, Dict[str, any]]:
        """
        Get availability indicators for multiple components.
        
        Args:
            component_ids: List of component IDs
        
        Returns:
            Dict mapping component_id to availability info:
                - quantity_on_hand: Current stock
                - reorder_point: Reorder threshold
                - status: "available", "low", "out_of_stock"
        """
        if not component_ids:
            return {}
        
        # Get components
        result = await self.db.execute(
            select(Component).where(Component.id.in_(component_ids))
        )
        components = result.scalars().all()
        
        indicators = {}
        for component in components:
            # Determine status
            if component.quantity_on_hand <= 0:
                status = "out_of_stock"
            elif component.quantity_on_hand <= component.reorder_point:
                status = "low"
            else:
                status = "available"
            
            indicators[component.id] = {
                "component_id": component.id,
                "component_name": component.name,
                "component_code": component.code,
                "quantity_on_hand": component.quantity_on_hand,
                "reorder_point": component.reorder_point,
                "unit": component.unit,
                "status": status
            }
        
        return indicators
    
    async def calculate_material_ready_date(
        self, 
        bom_id: int, 
        quantity: int
    ) -> Optional[datetime]:
        """
        Estimate when materials will be available based on pending orders.
        
        This is a simplified version - in production, would check:
        - Pending purchase orders
        - Lead times from suppliers
        - Production schedules for sub-assemblies
        
        Args:
            bom_id: Bill of Material ID
            quantity: Quantity to produce
        
        Returns:
            Estimated date when all materials will be available, or None if unknown
        """
        # Check current availability
        availability = await self.check_bom_availability(bom_id, quantity)
        
        if availability["all_available"]:
            # Materials already available
            return datetime.utcnow()
        
        # For missing components, estimate based on standard lead times
        # This is simplified - real implementation would check purchase orders
        max_lead_time_days = 0
        
        for missing in availability["missing_components"]:
            # Get component
            result = await self.db.execute(
                select(Component).where(Component.id == missing["component_id"])
            )
            component = result.scalar_one_or_none()
            
            if component and component.lead_time_days:
                max_lead_time_days = max(max_lead_time_days, component.lead_time_days)
        
        if max_lead_time_days > 0:
            return datetime.utcnow() + timedelta(days=max_lead_time_days)
        
        # Unknown - return None
        return None
    
    async def validate_materials_for_mo(
        self, 
        mo_id: int
    ) -> Dict[str, any]:
        """
        Validate material availability for a manufacturing order.
        
        Args:
            mo_id: Manufacturing Order ID
        
        Returns:
            Dict with:
                - can_schedule: bool - Whether MO can be scheduled
                - availability: Material availability details
                - estimated_ready_date: When materials will be available
                - blocking_reason: Reason if cannot schedule
        """
        from app.models.manufacturing import ManufacturingOrder
        
        # Get MO
        result = await self.db.execute(
            select(ManufacturingOrder).where(ManufacturingOrder.id == mo_id)
        )
        mo = result.scalar_one_or_none()
        
        if not mo:
            raise ValueError(f"Manufacturing Order {mo_id} not found")
        
        if not mo.bom_id:
            # No BOM, assume materials not required or checked elsewhere
            return {
                "can_schedule": True,
                "availability": None,
                "estimated_ready_date": None,
                "blocking_reason": None
            }
        
        # Check BOM availability
        availability = await self.check_bom_availability(mo.bom_id, mo.quantity)
        
        if availability["all_available"]:
            return {
                "can_schedule": True,
                "availability": availability,
                "estimated_ready_date": datetime.utcnow(),
                "blocking_reason": None
            }
        else:
            # Materials not available
            estimated_ready = await self.calculate_material_ready_date(
                mo.bom_id, mo.quantity
            )
            
            missing_items = [
                f"{comp['component_name']} (shortage: {comp['shortage']} {comp['unit']})"
                for comp in availability["missing_components"]
            ]
            
            blocking_reason = f"Missing materials: {', '.join(missing_items)}"
            
            return {
                "can_schedule": False,
                "availability": availability,
                "estimated_ready_date": estimated_ready,
                "blocking_reason": blocking_reason
            }
    
    async def get_material_shortages(
        self, 
        mo_id: int
    ) -> List[Dict[str, any]]:
        """
        Get list of material shortages for a manufacturing order.
        
        Args:
            mo_id: Manufacturing Order ID
        
        Returns:
            List of shortage details for each missing component
        """
        validation = await self.validate_materials_for_mo(mo_id)
        
        if not validation["availability"]:
            return []
        
        return validation["availability"]["missing_components"]
