"""
Shop Floor Service - Real-time operation execution and tracking
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_

from app.models.manufacturing import (
    ManufacturingOrder,
    ManufacturingOrderOperation,
    OperationStatusEnum,
    ManufacturingOrderStatusEnum,
)
from app.modules.manufacturing.infra.repositories.mo_operation_repo import (
    ManufacturingOrderOperationRepository,
)


class ShopFloorService:
    """Service for shop floor operations execution and tracking"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.mo_operation_repo = ManufacturingOrderOperationRepository(db)

    async def start_operation(
        self, operation_id: int, operator_id: Optional[int] = None
    ) -> ManufacturingOrderOperation:
        """
        Start an operation - records actual start time and updates status.
        
        Args:
            operation_id: Operation ID
            operator_id: Operator ID (optional)
            
        Returns:
            Updated operation
            
        Raises:
            ValueError: If operation cannot be started
        """
        # Fetch operation
        operation = await self.mo_operation_repo.get_by_id(operation_id)
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")

        # Validate status
        if operation.status not in [
            OperationStatusEnum.SCHEDULED,
            OperationStatusEnum.PENDING,
        ]:
            raise ValueError(
                f"Cannot start operation with status {operation.status.value}. "
                f"Operation must be SCHEDULED or PENDING."
            )

        # Validate previous operation is complete (sequence dependency)
        if operation.sequence > 1:
            # Get previous operation
            result = await self.db.execute(
                select(ManufacturingOrderOperation).where(
                    and_(
                        ManufacturingOrderOperation.manufacturing_order_id
                        == operation.manufacturing_order_id,
                        ManufacturingOrderOperation.sequence == operation.sequence - 1,
                    )
                )
            )
            prev_operation = result.scalar_one_or_none()

            if prev_operation and prev_operation.status != OperationStatusEnum.COMPLETED:
                raise ValueError(
                    f"Cannot start operation {operation.sequence}. "
                    f"Previous operation (sequence {prev_operation.sequence}) "
                    f"is not complete (status: {prev_operation.status.value})."
                )

        # Update operation
        operation.actual_start = datetime.utcnow()
        operation.status = OperationStatusEnum.IN_PROGRESS
        if operator_id:
            operation.assigned_operator_id = operator_id

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(operation)

        # Update MO status if needed
        await self.update_mo_status_from_operations(operation.manufacturing_order_id)

        return operation

    async def complete_operation(
        self, operation_id: int
    ) -> ManufacturingOrderOperation:
        """
        Complete an operation - records actual end time and calculates duration.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Updated operation
            
        Raises:
            ValueError: If operation cannot be completed
        """
        # Fetch operation
        operation = await self.mo_operation_repo.get_by_id(operation_id)
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")

        # Validate status
        if operation.status != OperationStatusEnum.IN_PROGRESS:
            raise ValueError(
                f"Cannot complete operation with status {operation.status.value}. "
                f"Operation must be IN_PROGRESS."
            )

        # Validate actual_start is set
        if not operation.actual_start:
            raise ValueError(
                "Operation actual_start is not set. Cannot complete operation."
            )

        # Update operation
        operation.actual_end = datetime.utcnow()

        # Calculate actual duration in minutes
        duration = operation.actual_end - operation.actual_start
        operation.actual_duration_minutes = int(duration.total_seconds() / 60)

        operation.status = OperationStatusEnum.COMPLETED

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(operation)

        # Update MO status if all operations complete
        await self.update_mo_status_from_operations(operation.manufacturing_order_id)

        return operation

    async def pause_operation(
        self, operation_id: int, reason: str
    ) -> ManufacturingOrderOperation:
        """
        Pause an in-progress operation.
        
        Args:
            operation_id: Operation ID
            reason: Reason for pausing
            
        Returns:
            Updated operation
            
        Raises:
            ValueError: If operation cannot be paused
        """
        # Fetch operation
        operation = await self.mo_operation_repo.get_by_id(operation_id)
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")

        # Validate status
        if operation.status != OperationStatusEnum.IN_PROGRESS:
            raise ValueError(
                f"Cannot pause operation with status {operation.status.value}. "
                f"Operation must be IN_PROGRESS."
            )

        # Add pause note
        pause_note = f"[PAUSED at {datetime.utcnow().isoformat()}] {reason}"
        if operation.notes:
            operation.notes = f"{operation.notes}\n{pause_note}"
        else:
            operation.notes = pause_note

        # Note: Status remains IN_PROGRESS
        # Future: Could add a PAUSED status or track pause duration

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(operation)

        return operation

    async def block_operation(
        self, operation_id: int, blocking_reason: str
    ) -> ManufacturingOrderOperation:
        """
        Block an operation due to an issue.
        
        Args:
            operation_id: Operation ID
            blocking_reason: Reason for blocking
            
        Returns:
            Updated operation
            
        Raises:
            ValueError: If operation cannot be blocked
        """
        # Fetch operation
        operation = await self.mo_operation_repo.get_by_id(operation_id)
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")

        # Validate status - cannot block completed operations
        if operation.status == OperationStatusEnum.COMPLETED:
            raise ValueError("Cannot block a completed operation")

        # Update operation
        operation.status = OperationStatusEnum.BLOCKED
        operation.blocking_reason = blocking_reason

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(operation)

        # Update MO status to BLOCKED
        await self.update_mo_status_from_operations(operation.manufacturing_order_id)
        
        # Send blocking alert notification
        try:
            from app.modules.notifications.application.services.production_notification_service import (
                ProductionNotificationService,
            )
            notification_service = ProductionNotificationService(self.db)
            await notification_service.notify_blocking_alert(
                operation_id=operation_id,
                blocking_reason=blocking_reason
            )
        except Exception as e:
            # Log error but don't fail the blocking operation
            print(f"Failed to send blocking notification: {e}")

        return operation

    async def unblock_operation(
        self, operation_id: int
    ) -> ManufacturingOrderOperation:
        """
        Unblock a blocked operation, returning it to IN_PROGRESS or SCHEDULED.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Updated operation
        """
        # Fetch operation
        operation = await self.mo_operation_repo.get_by_id(operation_id)
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")

        if operation.status != OperationStatusEnum.BLOCKED:
            raise ValueError("Operation is not blocked")

        # Determine new status based on whether it was started
        if operation.actual_start:
            operation.status = OperationStatusEnum.IN_PROGRESS
        else:
            operation.status = OperationStatusEnum.SCHEDULED

        # Clear blocking reason
        operation.blocking_reason = None

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(operation)

        # Update MO status
        await self.update_mo_status_from_operations(operation.manufacturing_order_id)

        return operation

    async def update_mo_status_from_operations(self, mo_id: int) -> ManufacturingOrder:
        """
        Update MO status based on the status of its operations.
        
        Status logic:
        - Any operation BLOCKED → MO status BLOCKED
        - All operations COMPLETED → MO status COMPLETED
        - Any operation IN_PROGRESS → MO status IN_PRODUCTION
        - All operations SCHEDULED/PENDING → MO status MR_APPROVED
        
        Args:
            mo_id: Manufacturing Order ID
            
        Returns:
            Updated MO
        """
        # Fetch MO
        result = await self.db.execute(
            select(ManufacturingOrder).where(ManufacturingOrder.id == mo_id)
        )
        mo = result.scalar_one_or_none()
        if not mo:
            raise ValueError(f"Manufacturing Order {mo_id} not found")

        # Get all operations for this MO
        operations = await self.mo_operation_repo.get_by_mo_id(mo_id)
        if not operations:
            # No operations yet, leave status as is
            return mo

        # Determine new status
        operation_statuses = [op.status for op in operations]

        new_status = None

        # Priority 1: Any blocked → MO blocked
        if OperationStatusEnum.BLOCKED in operation_statuses:
            new_status = ManufacturingOrderStatusEnum.BLOCKED

        # Priority 2: All completed → MO completed
        elif all(status == OperationStatusEnum.COMPLETED for status in operation_statuses):
            new_status = ManufacturingOrderStatusEnum.COMPLETED

        # Priority 3: Any in progress → MO in production
        elif OperationStatusEnum.IN_PROGRESS in operation_statuses:
            new_status = ManufacturingOrderStatusEnum.IN_PRODUCTION

        # Priority 4: All scheduled/pending → MO approved
        elif all(
            status in [OperationStatusEnum.SCHEDULED, OperationStatusEnum.PENDING]
            for status in operation_statuses
        ):
            # Keep current status if it's already MR_APPROVED or higher
            if mo.status in [
                ManufacturingOrderStatusEnum.PENDING,
                ManufacturingOrderStatusEnum.MR_SENT,
            ]:
                new_status = ManufacturingOrderStatusEnum.MR_APPROVED

        # Update MO status if changed
        if new_status and mo.status != new_status:
            mo.status = new_status

            # Set production_start_at when first operation starts
            if (
                new_status == ManufacturingOrderStatusEnum.IN_PRODUCTION
                and not mo.production_start_at
            ):
                mo.production_start_at = datetime.utcnow()

            # Set end_at when all operations complete
            if new_status == ManufacturingOrderStatusEnum.COMPLETED and not mo.end_at:
                mo.end_at = datetime.utcnow()

                # Calculate actual production lead time
                if mo.production_start_at:
                    mo.production_lead_time = mo.end_at - mo.production_start_at

            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(mo)

        return mo

    async def get_work_center_queue(
        self, work_center_id: int, status_filter: Optional[List[OperationStatusEnum]] = None
    ) -> List[Dict]:
        """
        Get the queue of operations for a work center.
        
        Args:
            work_center_id: Work Center ID
            status_filter: Optional list of statuses to filter by
            
        Returns:
            List of operation details with MO context
        """
        # Default filter to active statuses
        if not status_filter:
            status_filter = [
                OperationStatusEnum.PENDING,
                OperationStatusEnum.SCHEDULED,
                OperationStatusEnum.IN_PROGRESS,
            ]

        # Query operations
        query = (
            select(ManufacturingOrderOperation)
            .where(ManufacturingOrderOperation.work_center_id == work_center_id)
            .where(ManufacturingOrderOperation.status.in_(status_filter))
            .order_by(ManufacturingOrderOperation.scheduled_start.asc())
        )

        result = await self.db.execute(query)
        operations = result.scalars().all()

        # Enrich with MO details
        queue_items = []
        for op in operations:
            # Fetch MO
            mo_result = await self.db.execute(
                select(ManufacturingOrder).where(
                    ManufacturingOrder.id == op.manufacturing_order_id
                )
            )
            mo = mo_result.scalar_one_or_none()

            queue_items.append(
                {
                    "operation_id": op.id,
                    "operation_name": op.name,
                    "sequence": op.sequence,
                    "status": op.status.value,
                    "scheduled_start": op.scheduled_start,
                    "scheduled_duration_minutes": op.scheduled_duration_minutes,
                    "mo_id": op.manufacturing_order_id,
                    "mo_number": f"MO-{mo.id}" if mo else None,
                    "product_id": mo.product_id if mo else None,
                    "quantity": mo.quantity if mo else None,
                }
            )

        return queue_items

    async def get_my_assignments(
        self, operator_id: int
    ) -> List[ManufacturingOrderOperation]:
        """
        Get operations assigned to a specific operator.
        
        Args:
            operator_id: Operator ID
            
        Returns:
            List of assigned operations
        """
        query = (
            select(ManufacturingOrderOperation)
            .where(ManufacturingOrderOperation.assigned_operator_id == operator_id)
            .where(
                ManufacturingOrderOperation.status.in_(
                    [
                        OperationStatusEnum.SCHEDULED,
                        OperationStatusEnum.IN_PROGRESS,
                    ]
                )
            )
            .order_by(ManufacturingOrderOperation.scheduled_start.asc())
        )

        result = await self.db.execute(query)
        operations = result.scalars().all()

        return list(operations)

    async def get_dashboard_data(
        self, work_center_id: Optional[int] = None
    ) -> Dict:
        """
        Get aggregated dashboard metrics for shop floor monitoring.
        
        Args:
            work_center_id: Optional filter by work center
            
        Returns:
            Dict with dashboard metrics
        """
        # Build base query filter
        base_filter = []
        if work_center_id:
            base_filter.append(
                ManufacturingOrderOperation.work_center_id == work_center_id
            )

        # Count active operations (IN_PROGRESS)
        active_query = select(func.count(ManufacturingOrderOperation.id)).where(
            and_(
                ManufacturingOrderOperation.status == OperationStatusEnum.IN_PROGRESS,
                *base_filter,
            )
        )
        active_count = (await self.db.execute(active_query)).scalar()

        # Count pending operations (SCHEDULED + PENDING)
        pending_query = select(func.count(ManufacturingOrderOperation.id)).where(
            and_(
                ManufacturingOrderOperation.status.in_(
                    [OperationStatusEnum.SCHEDULED, OperationStatusEnum.PENDING]
                ),
                *base_filter,
            )
        )
        pending_count = (await self.db.execute(pending_query)).scalar()

        # Count blocked operations
        blocked_query = select(func.count(ManufacturingOrderOperation.id)).where(
            and_(
                ManufacturingOrderOperation.status == OperationStatusEnum.BLOCKED,
                *base_filter,
            )
        )
        blocked_count = (await self.db.execute(blocked_query)).scalar()

        # Count completed today
        today_start = datetime.combine(date.today(), datetime.min.time())
        completed_today_query = select(
            func.count(ManufacturingOrderOperation.id)
        ).where(
            and_(
                ManufacturingOrderOperation.status == OperationStatusEnum.COMPLETED,
                ManufacturingOrderOperation.actual_end >= today_start,
                *base_filter,
            )
        )
        completed_today_count = (await self.db.execute(completed_today_query)).scalar()

        # Average utilization would require work center schedules
        # Simplified version for now
        avg_utilization = 0.0

        return {
            "active_operations": active_count or 0,
            "pending_operations": pending_count or 0,
            "blocked_operations": blocked_count or 0,
            "completed_today": completed_today_count or 0,
            "avg_utilization_pct": avg_utilization,
            "timestamp": datetime.utcnow(),
        }
