"""
Production Integration Service for Sales Orders
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.sales import SalesOrder
from app.models.manufacturing import ManufacturingOrder, ManufacturingOrderStatusEnum


class ProductionIntegrationService:
    """Service for integrating production scheduling with sales orders"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_delivery_date(
        self, 
        sales_order_id: int,
        buffer_days: int = 3
    ) -> Optional[datetime]:
        """
        Calculate estimated delivery date based on production schedule.
        
        Args:
            sales_order_id: Sales Order ID
            buffer_days: Buffer days to add after production completion (default: 3)
        
        Returns:
            Estimated delivery date or None if not scheduled
        """
        # Get sales order
        result = await self.db.execute(
            select(SalesOrder).where(SalesOrder.id == sales_order_id)
        )
        sales_order = result.scalar_one_or_none()
        
        if not sales_order:
            raise ValueError(f"Sales Order {sales_order_id} not found")
        
        # Get associated manufacturing orders
        result = await self.db.execute(
            select(ManufacturingOrder).where(
                ManufacturingOrder.sales_order_id == sales_order_id
            )
        )
        manufacturing_orders = result.scalars().all()
        
        if not manufacturing_orders:
            # No production orders yet
            return None
        
        # Find the latest scheduled end date across all MOs
        latest_completion = None
        
        for mo in manufacturing_orders:
            if mo.scheduled_end:
                if latest_completion is None or mo.scheduled_end > latest_completion:
                    latest_completion = mo.scheduled_end
        
        if not latest_completion:
            # No MOs are scheduled yet
            return None
        
        # Add buffer days for shipping/packaging
        delivery_date = latest_completion + timedelta(days=buffer_days)
        
        return delivery_date
    
    async def get_production_schedule_for_so(
        self, 
        sales_order_id: int
    ) -> Dict[str, any]:
        """
        Get production schedule information for a sales order.
        
        Args:
            sales_order_id: Sales Order ID
        
        Returns:
            Dict with production schedule details, MO information, and progress
        """
        # Get sales order
        result = await self.db.execute(
            select(SalesOrder).where(SalesOrder.id == sales_order_id)
        )
        sales_order = result.scalar_one_or_none()
        
        if not sales_order:
            raise ValueError(f"Sales Order {sales_order_id} not found")
        
        # Get manufacturing orders
        result = await self.db.execute(
            select(ManufacturingOrder).where(
                ManufacturingOrder.sales_order_id == sales_order_id
            )
        )
        mos = result.scalars().all()
        
        if not mos:
            return {
                "sales_order_id": sales_order_id,
                "has_production": False,
                "manufacturing_orders": [],
                "overall_status": "not_started",
                "estimated_delivery_date": None
            }
        
        # Calculate overall status
        statuses = [mo.status for mo in mos]
        if all(s == ManufacturingOrderStatusEnum.COMPLETED for s in statuses):
            overall_status = "completed"
        elif any(s == ManufacturingOrderStatusEnum.BLOCKED for s in statuses):
            overall_status = "blocked"
        elif any(s == ManufacturingOrderStatusEnum.IN_PRODUCTION for s in statuses):
            overall_status = "in_production"
        elif all(s in [ManufacturingOrderStatusEnum.PENDING, ManufacturingOrderStatusEnum.MR_SENT] for s in statuses):
            overall_status = "scheduled"
        else:
            overall_status = "in_progress"
        
        # Get MO details
        mo_details = []
        for mo in mos:
            mo_info = {
                "mo_id": mo.id,
                "mo_number": f"MO-{mo.id}",
                "product_id": mo.product_id,
                "quantity": mo.quantity,
                "status": mo.status.value,
                "scheduled_start": mo.scheduled_start,
                "scheduled_end": mo.scheduled_end,
                "production_start_at": mo.production_start_at,
                "end_at": mo.end_at,
                "total_scheduled_duration_minutes": mo.total_scheduled_duration_minutes
            }
            mo_details.append(mo_info)
        
        # Calculate estimated delivery
        estimated_delivery = await self.calculate_delivery_date(sales_order_id)
        
        return {
            "sales_order_id": sales_order_id,
            "has_production": True,
            "manufacturing_orders": mo_details,
            "overall_status": overall_status,
            "estimated_delivery_date": estimated_delivery,
            "total_mos": len(mos)
        }
    
    async def update_so_status_from_production(
        self, 
        sales_order_id: int
    ) -> SalesOrder:
        """
        Update sales order status based on production progress.
        
        This could be called as a webhook/trigger when MO status changes.
        
        Args:
            sales_order_id: Sales Order ID
        
        Returns:
            Updated SalesOrder
        """
        # Get sales order
        result = await self.db.execute(
            select(SalesOrder).where(SalesOrder.id == sales_order_id)
        )
        sales_order = result.scalar_one_or_none()
        
        if not sales_order:
            raise ValueError(f"Sales Order {sales_order_id} not found")
        
        # Get manufacturing orders
        result = await self.db.execute(
            select(ManufacturingOrder).where(
                ManufacturingOrder.sales_order_id == sales_order_id
            )
        )
        mos = result.scalars().all()
        
        if not mos:
            # No production, leave status as is
            return sales_order
        
        # Update delivery date
        estimated_delivery = await self.calculate_delivery_date(sales_order_id)
        if estimated_delivery:
            sales_order.delivery_date = estimated_delivery
        
        # Optionally update SO status based on production
        # This depends on your business logic
        # For now, we'll just update the delivery date
        
        await self.db.commit()
        await self.db.refresh(sales_order)
        
        return sales_order
    
    async def get_production_timeline(
        self, 
        sales_order_id: int
    ) -> List[Dict[str, any]]:
        """
        Get a timeline of production events for a sales order.
        
        Useful for customer communication and tracking.
        
        Args:
            sales_order_id: Sales Order ID
        
        Returns:
            List of timeline events sorted by date
        """
        # Get manufacturing orders
        result = await self.db.execute(
            select(ManufacturingOrder).where(
                ManufacturingOrder.sales_order_id == sales_order_id
            )
        )
        mos = result.scalars().all()
        
        timeline = []
        
        for mo in mos:
            # MO created
            timeline.append({
                "date": mo.created_at,
                "event": "Manufacturing Order Created",
                "mo_id": mo.id,
                "mo_number": f"MO-{mo.id}",
                "details": f"Production planned for {mo.quantity} units"
            })
            
            # Scheduled
            if mo.scheduled_start:
                timeline.append({
                    "date": mo.scheduled_start,
                    "event": "Production Scheduled to Start",
                    "mo_id": mo.id,
                    "mo_number": f"MO-{mo.id}",
                    "details": f"Expected completion: {mo.scheduled_end}"
                })
            
            # Started production
            if mo.production_start_at:
                timeline.append({
                    "date": mo.production_start_at,
                    "event": "Production Started",
                    "mo_id": mo.id,
                    "mo_number": f"MO-{mo.id}",
                    "details": "Manufacturing in progress"
                })
            
            # Completed
            if mo.end_at:
                timeline.append({
                    "date": mo.end_at,
                    "event": "Production Completed",
                    "mo_id": mo.id,
                    "mo_number": f"MO-{mo.id}",
                    "details": f"Completed in {mo.production_lead_time if mo.production_lead_time else 'N/A'}"
                })
        
        # Sort by date
        timeline.sort(key=lambda x: x["date"])
        
        return timeline
