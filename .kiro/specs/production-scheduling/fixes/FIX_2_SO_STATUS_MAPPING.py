"""
IMPLEMENTATION FIX #2: Sales Order Status Mapping Logic
File to modify: backend/app/modules/sales/application/services/production_integration_service.py
Location: Lines 194-196 (in update_so_status_from_production method)
Priority: HIGH
Estimated Time: 1 hour (includes enum updates and testing)
"""

# STEP 1: UPDATE SalesOrderStatus Enum (if needed)
# File: backend/app/models/sales.py
# Add these statuses to your SalesOrderStatus enum if they don't exist:

class SalesOrderStatus(str, Enum):
    # ... existing statuses ...
    CONFIRMED = "confirmed"  # Order confirmed, pending production
    PRODUCTION_SCHEDULED = "production_scheduled"  # MOs scheduled
    IN_PRODUCTION = "in_production"  # Manufacturing in progress
    PRODUCTION_DELAYED = "production_delayed"  # Production blocked/delayed
    READY_TO_SHIP = "ready_to_ship"  # Production complete
    # ... other statuses ...


# STEP 2: REPLACE lines 194-196 with this enhanced logic
# File: backend/app/modules/sales/application/services/production_integration_service.py

    async def update_so_status_from_production(
        self, 
        sales_order_id: int
    ) -> SalesOrder:
        """
        Update sales order status and delivery date based on production progress.
        
        This is called:
        1. Manually via API endpoint
        2. Automatically when MO status changes (via shop_floor_service hook)
        
        Args:
            sales_order_id: Sales Order ID
            
        Returns:
            Updated SalesOrder with synced status and delivery_date
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
            if old_delivery_date:
                date_diff = abs((estimated_delivery - old_delivery_date).days)
                if date_diff > 2:  # More than 2 days change
                    delivery_date_changed = True
        
        # UPDATE SO STATUS based on production progress
        from app.models.sales import SalesOrderStatus
        
        mo_statuses = [mo.status for mo in mos]
        current_so_status = sales_order.status
        new_so_status = None
        
        # Status mapping logic - BUSINESS RULES
        # Priority order matters!
        
        # 1. HIGHEST PRIORITY: All production completed
        if all(s == ManufacturingOrderStatusEnum.COMPLETED for s in mo_statuses):
            new_so_status = SalesOrderStatus.READY_TO_SHIP
            
        # 2. HIGH PRIORITY: Any production blocked/delayed
        elif any(s == ManufacturingOrderStatusEnum.BLOCKED for s in mo_statuses):
            new_so_status = SalesOrderStatus.PRODUCTION_DELAYED
            
        # 3. MEDIUM PRIORITY: Active production
        elif any(s == ManufacturingOrderStatusEnum.IN_PRODUCTION for s in mo_statuses):
            # Only update if not already in a "further along" status
            if current_so_status not in [
                SalesOrderStatus.READY_TO_SHIP,
                SalesOrderStatus.PRODUCTION_DELAYED,
            ]:
                new_so_status = SalesOrderStatus.IN_PRODUCTION
        
        # 4. LOW PRIORITY: Production scheduled/approved
        elif any(s == ManufacturingOrderStatusEnum.MR_APPROVED for s in mo_statuses):
            # Only update if still in early status
            if current_so_status in [
                SalesOrderStatus.DRAFT,
                SalesOrderStatus.CONFIRMED,
            ]:
                new_so_status = SalesOrderStatus.PRODUCTION_SCHEDULED
        
        # 5. LOWEST: Production pending
        elif all(
            s in [
                ManufacturingOrderStatusEnum.PENDING,
                ManufacturingOrderStatusEnum.MR_SENT,
            ]
            for s in mo_statuses
        ):
            # Keep as confirmed if production is just starting
            if current_so_status == SalesOrderStatus.DRAFT:
                new_so_status = SalesOrderStatus.CONFIRMED
        
        # Apply status update if changed
        status_changed = False
        if new_so_status and sales_order.status != new_so_status:
            sales_order.status = new_so_status
            status_changed = True
        
        # Commit changes
        await self.db.commit()
        await self.db.refresh(sales_order)
        
        # Optional: Send notifications for significant changes
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
        
        This is a helper method to notify relevant stakeholders.
        """
        try:
            from app.modules.notifications.application.services.production_notification_service import (
                ProductionNotificationService,
            )
            
            notification_service = ProductionNotificationService(self.db)
            
            # Build notification message
            changes = []
            if status_changed:
                changes.append(f"Status changed to {sales_order.status.value}")
            
            if delivery_changed and old_delivery and new_delivery:
                date_diff = (new_delivery - old_delivery).days
                direction = "delayed" if date_diff > 0 else "moved up"
                changes.append(
                    f"Delivery date {direction} by {abs(date_diff)} days "
                    f"(was {old_delivery.date()}, now {new_delivery.date()})"
                )
            
            if changes:
                message = f"Sales Order {sales_order.id}: " + ", ".join(changes)
                
                # Send notification (adjust based on your notification system)
                # Example: Send to sales team and customer service
                await notification_service.notify_sales_order_update(
                    sales_order_id=sales_order.id,
                    message=message,
                    priority="high" if delivery_changed else "medium",
                )
                
        except ImportError:
            # Notification service doesn't exist yet
            pass


"""
WHAT THIS DOES:
1. Calculates delivery date based on production schedule
2. Maps production status to sales order status with clear business rules
3. Detects significant changes (delivery date shift > 2 days)
4. Sends notifications to sales team when important changes occur
5. Maintains audit trail with before/after values

STATUS TRANSITION RULES:
- COMPLETED → READY_TO_SHIP (all MOs done)
- BLOCKED → PRODUCTION_DELAYED (any issue)
- IN_PRODUCTION → IN_PRODUCTION (actively manufacturing)
- MR_APPROVED → PRODUCTION_SCHEDULED (scheduled)
- PENDING → CONFIRMED (just created)

TESTING:
1. Create SO → status = CONFIRMED
2. Create and schedule MOs → status = PRODUCTION_SCHEDULED
3. Start production → status = IN_PRODUCTION
4. Block operation → status = PRODUCTION_DELAYED
5. Unblock and complete → status = READY_TO_SHIP
6. Verify delivery_date updates at each step

CONFIGURATION:
- Adjust status names to match your SalesOrderStatus enum
- Modify business rules in the if/elif chain
- Customize notification threshold (currently 2 days)

DEPENDENCIES:
- Requires SalesOrderStatus enum to have the needed statuses
- Optional: ProductionNotificationService for notifications
"""
