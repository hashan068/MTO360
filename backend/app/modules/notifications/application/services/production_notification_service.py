"""
Production Notification Service
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.notifications import Notification
from app.models.user import User
from app.models.manufacturing import ManufacturingOrderOperation, WorkCenter


class ProductionNotificationService:
    """Service for creating production-related notifications"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def notify_operation_assignment(
        self, 
        operation_id: int, 
        operator_id: int,
        assigned_by_id: Optional[int] = None
    ) -> Notification:
        """
        Notify operator of new operation assignment.
        
        Args:
            operation_id: ID of the manufacturing order operation
            operator_id: ID of the operator being assigned
            assigned_by_id: ID of the user who assigned the operation (optional)
        
        Returns:
            Created notification
        """
        # Get operation details
        query = select(ManufacturingOrderOperation).where(
            ManufacturingOrderOperation.id == operation_id
        )
        result = await self.db.execute(query)
        operation = result.scalar_one_or_none()
        
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")
        
        # Create notification message
        message = (
            f"You have been assigned to operation: {operation.name} "
            f"(Sequence {operation.sequence}) for MO #{operation.manufacturing_order_id}"
        )
        
        # Create notification
        notification = Notification(
            user_id=operator_id,
            message=message,
            notification_type="operation_assignment",
            related_entity_type="manufacturing_order_operation",
            related_entity_id=operation_id,
            severity="info",
            action_url=f"/manufacturing/shop-floor?operation_id={operation_id}"
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        return notification
    
    async def notify_blocking_alert(
        self, 
        operation_id: int, 
        blocking_reason: str,
        notify_user_ids: Optional[List[int]] = None
    ) -> List[Notification]:
        """
        Alert relevant users of operation blocking.
        
        Args:
            operation_id: ID of the blocked operation
            blocking_reason: Reason for blocking
            notify_user_ids: List of user IDs to notify (if None, notifies managers)
        
        Returns:
            List of created notifications
        """
        # Get operation details
        query = select(ManufacturingOrderOperation).where(
            ManufacturingOrderOperation.id == operation_id
        )
        result = await self.db.execute(query)
        operation = result.scalar_one_or_none()
        
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")
        
        # If no specific users provided, notify all production managers
        if not notify_user_ids:
            # Get users with production manager or planner roles
            # For now, notify all active staff users (can be refined)
            user_query = select(User).where(User.is_staff == True, User.is_active == True)
            result = await self.db.execute(user_query)
            users = result.scalars().all()
            notify_user_ids = [u.id for u in users]
        
        # Create notification message
        message = (
            f"⚠️ BLOCKED: Operation {operation.name} "
            f"(MO #{operation.manufacturing_order_id}) - Reason: {blocking_reason}"
        )
        
        # Create notifications for all target users
        notifications = []
        for user_id in notify_user_ids:
            notification = Notification(
                user_id=user_id,
                message=message,
                notification_type="blocking_alert",
                related_entity_type="manufacturing_order_operation",
                related_entity_id=operation_id,
                severity="error",
                action_url=f"/manufacturing/shop-floor?operation_id={operation_id}"
            )
            self.db.add(notification)
            notifications.append(notification)
        
        await self.db.commit()
        
        for notification in notifications:
            await self.db.refresh(notification)
        
        return notifications
    
    async def notify_overallocation_warning(
        self, 
        work_center_id: int, 
        date: str,
        utilization_pct: float,
        notify_user_ids: Optional[List[int]] = None
    ) -> List[Notification]:
        """
        Warn planners of work center capacity overallocation.
        
        Args:
            work_center_id: ID of the overallocated work center
            date: Date of overallocation
            utilization_pct: Utilization percentage (>100 indicates overallocation)
            notify_user_ids: List of user IDs to notify (if None, notifies planners)
        
        Returns:
            List of created notifications
        """
        # Get work center details
        query = select(WorkCenter).where(WorkCenter.id == work_center_id)
        result = await self.db.execute(query)
        work_center = result.scalar_one_or_none()
        
        if not work_center:
            raise ValueError(f"Work center {work_center_id} not found")
        
        # If no specific users provided, notify production planners/managers
        if not notify_user_ids:
            # Get users with production planning or manager roles
            # For now, notify all active staff users (can be refined with role checking)
            user_query = select(User).where(User.is_staff == True, User.is_active == True)
            result = await self.db.execute(user_query)
            users = result.scalars().all()
            notify_user_ids = [u.id for u in users]
        
        # Create notification message
        message = (
            f"⚠️ OVERALLOCATED: Work Center '{work_center.name}' "
            f"is at {utilization_pct:.1f}% capacity on {date}"
        )
        
        # Create notifications for all target users
        notifications = []
        for user_id in notify_user_ids:
            notification = Notification(
                user_id=user_id,
                message=message,
                notification_type="overallocation_warning",
                related_entity_type="work_center",
                related_entity_id=work_center_id,
                severity="warning",
                action_url=f"/manufacturing/scheduling?work_center_id={work_center_id}&date={date}"
            )
            self.db.add(notification)
            notifications.append(notification)
        
        await self.db.commit()
        
        for notification in notifications:
            await self.db.refresh(notification)
        
        return notifications
    
    async def notify_schedule_change(
        self, 
        mo_id: int, 
        change_description: str,
        affected_user_ids: List[int]
    ) -> List[Notification]:
        """
        Notify affected users of schedule modifications.
        
        Args:
            mo_id: ID of the manufacturing order
            change_description: Description of what changed
            affected_user_ids: IDs of users affected by the change
        
        Returns:
            List of created notifications
        """
        message = f"📅 Schedule Change: MO #{mo_id} - {change_description}"
        
        # Create notifications for all affected users
        notifications = []
        for user_id in affected_user_ids:
            notification = Notification(
                user_id=user_id,
                message=message,
                notification_type="schedule_change",
                related_entity_type="manufacturing_order",
                related_entity_id=mo_id,
                severity="info",
                action_url=f"/manufacturing/orders/{mo_id}"
            )
            self.db.add(notification)
            notifications.append(notification)
        
        await self.db.commit()
        
        for notification in notifications:
            await self.db.refresh(notification)
        
        return notifications
