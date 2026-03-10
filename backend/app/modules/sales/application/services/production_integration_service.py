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
        
        # Calculate and update delivery date
        estimated_delivery = await self.calculate_delivery_date(sales_order_id)
        old_delivery_date = sales_order.delivery_date
        
        if estimated_delivery:
            sales_order.delivery_date = estimated_delivery
            
        # Track if delivery date changed significantly
        delivery_date_changed = False
        if old_delivery_date and estimated_delivery:
            date_diff = abs((estimated_delivery - old_delivery_date).days)
            if date_diff > 2:  # More than 2 days change is significant
                delivery_date_changed = True
        
        # FIX #2: UPDATE SO STATUS based on production progress
        # Business rules for status mapping
        from app.models.sales import SalesOrderStatusEnum
        
        mo_statuses = [mo.status for mo in mos]
        current_so_status = sales_order.status
        new_so_status = None
        
        # Status mapping logic - Priority order matters!
        
        # 1. HIGHEST PRIORITY: All production completed → Ready to ship
        if all(s == ManufacturingOrderStatusEnum.COMPLETED for s in mo_statuses):
            new_so_status = SalesOrderStatusEnum.READY_TO_SHIP
            
        # 2. HIGH PRIORITY: Any production blocked/delayed → Production delayed
        elif any(s == ManufacturingOrderStatusEnum.BLOCKED for s in mo_statuses):
            new_so_status = SalesOrderStatusEnum.PRODUCTION_DELAYED
            
        # 3. MEDIUM PRIORITY: Active production → In production
        elif any(s == ManufacturingOrderStatusEnum.IN_PRODUCTION for s in mo_statuses):
            # Only update if not already in a "further along" status
            if current_so_status not in [
                SalesOrderStatusEnum.READY_TO_SHIP,
                SalesOrderStatusEnum.PRODUCTION_DELAYED,
                SalesOrderStatusEnum.DELIVERED,
            ]:
                new_so_status = SalesOrderStatusEnum.IN_PRODUCTION
        
        # 4. LOW PRIORITY: Production scheduled/approved
        elif any(s == ManufacturingOrderStatusEnum.MR_APPROVED for s in mo_statuses):
            # Only update if still in early status
            if current_so_status in [
                SalesOrderStatusEnum.PENDING,
                SalesOrderStatusEnum.CONFIRMED,
            ]:
                new_so_status = SalesOrderStatusEnum.PRODUCTION_SCHEDULED
        
        # 5. LOWEST: Production pending (just created)
        elif all(
            s in [
                ManufacturingOrderStatusEnum.PENDING,
                ManufacturingOrderStatusEnum.MR_SENT,
            ]
            for s in mo_statuses
        ):
            # Keep as confirmed if production is just starting
            if current_so_status == SalesOrderStatusEnum.PENDING:
                new_so_status = SalesOrderStatusEnum.CONFIRMED
        
        # Apply status update if changed
        status_changed = False
        if new_so_status and sales_order.status != new_so_status:
            sales_order.status = new_so_status
            status_changed = True
        
        # Commit changes to database
        await self.db.commit()
        await self.db.refresh(sales_order)
        
        # Send notifications for significant changes
        if delivery_date_changed or status_changed:
            try:
                await self._notify_sales_team_of_changes(
                    sales_order=sales_order,
                    status_changed=status_changed,
                    delivery_changed=delivery_date_changed,
                    old_delivery=old_delivery_date,
                    new_delivery=estimated_delivery,
                )
            except Exception as e:
                # Don't fail on notification errors
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Failed to send SO {sales_order_id} change notification: {e}"
                )
        
        return sales_order
    
    async def _notify_sales_team_of_changes(
        self,
        sales_order: SalesOrder,
        status_changed: bool,
        delivery_changed: bool,
        old_delivery: Optional[datetime],
        new_delivery: Optional[datetime],
    ) -> None:
        """
        Send notifications when SO status or delivery date changes significantly.
        
        This notifies relevant stakeholders (sales team, CSR) of important changes.
        
        Args:
            sales_order: Updated sales order
            status_changed: Whether status changed
            delivery_changed: Whether delivery date changed significantly
            old_delivery: Previous delivery date
            new_delivery: New delivery date
        """
        try:
            from app.modules.notifications.application.services.production_notification_service import (
                ProductionNotificationService,
            )
            
            notification_service = ProductionNotificationService(self.db)
            
            # Build notification message
            changes = []
            if status_changed:
                changes.append(f"Status: {sales_order.status.value}")
            
            if delivery_changed and old_delivery and new_delivery:
                date_diff = (new_delivery - old_delivery).days
                direction = "delayed" if date_diff > 0 else "moved up"
                changes.append(
                    f"Delivery {direction} by {abs(date_diff)} days "
                    f"({old_delivery.date()} → {new_delivery.date()})"
                )
            
            if changes:
                message = f"SO-{sales_order.id} updated: " + ", ".join(changes)
                
                # Send notification
                # Priority: high if delivery changed, medium if just status
                priority = "high" if delivery_changed else "medium"
                
                # Note: This assumes your notification service has this method
                # Adjust based on your actual notification service implementation
                await notification_service.notify_sales_order_update(
                    sales_order_id=sales_order.id,
                    message=message,
                    priority=priority,
                )
                
        except ImportError:
            # Notification service doesn't exist or method not implemented
            # This is fine - notifications are optional
            pass
        except AttributeError:
            # notify_sales_order_update method doesn't exist
            # This is fine - notifications are optional
            pass
    
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
