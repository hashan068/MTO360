"""
Scheduling Service - Core scheduling logic for production planning
"""
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.manufacturing import (
    ManufacturingOrder,
    ManufacturingOrderOperation,
    OperationRoute,
    RouteOperation,
    WorkCenter,
    WorkCenterSchedule,
    OperationStatusEnum,
    ManufacturingOrderStatusEnum,
)
from app.modules.manufacturing.infra.repositories.mo_operation_repo import (
    ManufacturingOrderOperationRepository,
)
from app.modules.manufacturing.infra.repositories.operation_route_repo import (
    OperationRouteRepository,
)
from app.modules.manufacturing.infra.repositories.work_center_repo import (
    WorkCenterRepository as WorkCenterRepositoryImpl,
)
from app.modules.manufacturing.infra.repositories.work_center_schedule_repo import (
    WorkCenterScheduleRepository,
)


class SchedulingService:
    """Service for production scheduling operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.mo_operation_repo = ManufacturingOrderOperationRepository(db)
        self.operation_route_repo = OperationRouteRepository(db)
        self.work_center_repo = WorkCenterRepositoryImpl(db)
        self.wc_schedule_repo = WorkCenterScheduleRepository(db)

    async def generate_operations_for_mo(
        self, mo_id: int
    ) -> List[ManufacturingOrderOperation]:
        """
        Generate operations for a manufacturing order from its route template.
        
        Args:
            mo_id: Manufacturing Order ID
            
        Returns:
            List of created ManufacturingOrderOperation instances
            
        Raises:
            ValueError: If MO not found or no route exists for the product
        """
        # Fetch MO
        result = await self.db.execute(
            select(ManufacturingOrder).where(ManufacturingOrder.id == mo_id)
        )
        mo = result.scalar_one_or_none()
        if not mo:
            raise ValueError(f"Manufacturing Order {mo_id} not found")

        # Find active operation route for the product or BOM
        route = None
        if mo.product_id:
            route = await self.operation_route_repo.get_by_product_id(mo.product_id)
        elif mo.bom_id:
            result = await self.db.execute(
                select(OperationRoute).where(
                    and_(
                        OperationRoute.bom_id == mo.bom_id,
                        OperationRoute.is_active == True,
                    )
                )
            )
            route = result.scalar_one_or_none()

        if not route:
            raise ValueError(f"No active operation route found for MO {mo_id}")

        # Get route operations
        result = await self.db.execute(
            select(RouteOperation)
            .where(RouteOperation.route_id == route.id)
            .order_by(RouteOperation.sequence)
        )
        route_operations = result.scalars().all()

        if not route_operations:
            raise ValueError(f"Route {route.id} has no operations defined")

        # Create MO operations from route template
        created_operations = []
        for route_op in route_operations:
            mo_operation = ManufacturingOrderOperation(
                manufacturing_order_id=mo_id,
                route_operation_id=route_op.id,
                sequence=route_op.sequence,
                name=route_op.name,
                work_center_id=route_op.work_center_id,
                scheduled_duration_minutes=route_op.standard_time_minutes
                + route_op.setup_time_minutes,
                status=OperationStatusEnum.PENDING,
            )
            self.db.add(mo_operation)
            created_operations.append(mo_operation)

        await self.db.flush()
        await self.db.commit()

        # Refresh to get IDs
        for op in created_operations:
            await self.db.refresh(op)

        return created_operations

    async def calculate_work_center_capacity(
        self, work_center_id: int, target_date: date
    ) -> Dict[str, float]:
        """
        Calculate capacity metrics for a work center on a specific date.
        
        Args:
            work_center_id: Work Center ID
            target_date: Date to calculate capacity for
            
        Returns:
            Dict with capacity_minutes, scheduled_minutes, available_minutes, utilization_pct
        """
        # Get work center
        work_center = await self.work_center_repo.get_by_id(work_center_id)
        if not work_center:
            raise ValueError(f"Work Center {work_center_id} not found")

        # Get or create schedule record
        schedule = await self.wc_schedule_repo.get_or_create(
            work_center_id, target_date
        )

        # Calculate capacity in minutes
        capacity_minutes = float(work_center.capacity_hours_per_day) * 60

        # Get scheduled operations for this date
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        result = await self.db.execute(
            select(ManufacturingOrderOperation).where(
                and_(
                    ManufacturingOrderOperation.work_center_id == work_center_id,
                    ManufacturingOrderOperation.scheduled_start >= start_of_day,
                    ManufacturingOrderOperation.scheduled_start < end_of_day,
                    ManufacturingOrderOperation.status.in_(
                        [
                            OperationStatusEnum.SCHEDULED,
                            OperationStatusEnum.IN_PROGRESS,
                            OperationStatusEnum.COMPLETED,
                        ]
                    ),
                )
            )
        )
        scheduled_operations = result.scalars().all()

        # Calculate total scheduled minutes
        scheduled_minutes = sum(
            op.scheduled_duration_minutes for op in scheduled_operations
        )

        # Calculate available and utilization
        available_minutes = max(0, capacity_minutes - scheduled_minutes)
        utilization_pct = (
            (scheduled_minutes / capacity_minutes * 100) if capacity_minutes > 0 else 0
        )

        return {
            "capacity_minutes": capacity_minutes,
            "scheduled_minutes": scheduled_minutes,
            "available_minutes": available_minutes,
            "utilization_pct": round(utilization_pct, 2),
        }

    async def find_available_slot(
        self, work_center_id: int, duration_minutes: int, after_datetime: datetime
    ) -> Dict[str, datetime]:
        """
        Find the next available time slot for an operation.
        
        Uses simple forward scheduling - finds the earliest slot with enough capacity.
        
        Args:
            work_center_id: Work Center ID
            duration_minutes: Duration needed
            after_datetime: Earliest acceptable start time
            
        Returns:
            Dict with start_datetime and end_datetime
        """
        # Start searching from the given datetime
        current_date = after_datetime.date()
        max_days_ahead = 365  # Search up to 1 year ahead

        for day_offset in range(max_days_ahead):
            search_date = current_date + timedelta(days=day_offset)

            # Get capacity for this date
            capacity_info = await self.calculate_work_center_capacity(
                work_center_id, search_date
            )

            # Check if there's enough available capacity
            if capacity_info["available_minutes"] >= duration_minutes:
                # Find the actual start time within this day
                # For simplicity, schedule at start of work day or after the given time
                start_of_day = datetime.combine(search_date, datetime.min.time().replace(hour=8))
                
                # If this is the first day and after_datetime is later, use that
                if day_offset == 0 and after_datetime > start_of_day:
                    # Round up to next hour for cleaner scheduling
                    start_time = after_datetime + timedelta(
                        minutes=(60 - after_datetime.minute) % 60
                    )
                else:
                    start_time = start_of_day

                # Check for conflicts with existing operations
                end_time = start_time + timedelta(minutes=duration_minutes)
                conflicts = await self.detect_scheduling_conflicts(
                    work_center_id, start_time, end_time
                )

                if not conflicts:
                    return {"start_datetime": start_time, "end_datetime": end_time}
                else:
                    # If there are conflicts, try to schedule after the last conflict
                    last_conflict_end = max(
                        op.scheduled_end for op in conflicts if op.scheduled_end
                    )
                    if last_conflict_end:
                        # Recursively find slot after the conflict
                        return await self.find_available_slot(
                            work_center_id, duration_minutes, last_conflict_end
                        )

        # No slot found within search window
        raise ValueError(
            f"No available slot found for {duration_minutes} minutes within {max_days_ahead} days"
        )

    async def schedule_operation(
        self, operation_id: int, start_datetime: datetime
    ) -> ManufacturingOrderOperation:
        """
        Manually schedule an operation at a specific time.
        
        Args:
            operation_id: Operation ID
            start_datetime: Desired start time
            
        Returns:
            Updated ManufacturingOrderOperation
            
        Raises:
            ValueError: If operation not found or conflicts exist
        """
        # Fetch operation
        operation = await self.mo_operation_repo.get_by_id(operation_id)
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")

        # Calculate end time
        end_datetime = start_datetime + timedelta(
            minutes=operation.scheduled_duration_minutes
        )

        # Check for conflicts
        conflicts = await self.detect_scheduling_conflicts(
            operation.work_center_id, start_datetime, end_datetime, operation_id
        )

        if conflicts:
            conflict_details = [
                f"Op {op.id} ({op.scheduled_start} - {op.scheduled_end})"
                for op in conflicts
            ]
            raise ValueError(
                f"Scheduling conflict detected with operations: {', '.join(conflict_details)}"
            )

        # Update operation
        operation.scheduled_start = start_datetime
        operation.scheduled_end = end_datetime
        operation.status = OperationStatusEnum.SCHEDULED

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(operation)

        # Update work center schedule
        await self.wc_schedule_repo.update_utilization(
            operation.work_center_id, start_datetime.date()
        )

        return operation

    async def auto_schedule_mo(self, mo_id: int) -> ManufacturingOrder:
        """
        Automatically schedule all operations for a manufacturing order.
        
        Uses forward scheduling algorithm:
        1. Get all operations sorted by sequence
        2. For each operation, find next available slot after previous operation
        3. Schedule the operation
        4. Update MO with overall schedule times
        
        Args:
            mo_id: Manufacturing Order ID
            
        Returns:
            Updated ManufacturingOrder with scheduling info
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
            raise ValueError(f"No operations found for MO {mo_id}")

        # Sort by sequence
        operations.sort(key=lambda op: op.sequence)

        # Determine earliest start time
        # Use max of: current time, MO creation time, material available time
        earliest_start = max(datetime.utcnow(), mo.created_at)
        
        # Check material availability if BOM exists
        if mo.bom_id:
            try:
                from app.modules.inventory.application.services.material_availability_service import (
                    MaterialAvailabilityService,
                )
                material_service = MaterialAvailabilityService(self.db)
                validation = await material_service.validate_materials_for_mo(mo.id)
                
                if not validation["can_schedule"]:
                    # Materials not available, use estimated ready date
                    if validation["estimated_ready_date"]:
                        earliest_start = max(earliest_start, validation["estimated_ready_date"])
                        print(f"Materials not ready for MO {mo.id}. Scheduling from {validation['estimated_ready_date']}")
                    else:
                        # Cannot determine ready date, proceed with warning
                        print(f"Warning: Materials not available for MO {mo.id}, but lead time unknown")
            except Exception as e:
                # Log error but continue with scheduling
                print(f"Material check failed for MO {mo.id}: {e}")

        # Schedule each operation in sequence
        prev_end_time = earliest_start

        for operation in operations:
            # Find available slot for this operation
            slot = await self.find_available_slot(
                operation.work_center_id,
                operation.scheduled_duration_minutes,
                prev_end_time,
            )

            # Schedule the operation
            await self.schedule_operation(operation.id, slot["start_datetime"])

            # Update for next iteration
            prev_end_time = slot["end_datetime"]

        # Refresh operations to get updated times
        for op in operations:
            await self.db.refresh(op)

        # Update MO with overall schedule
        mo.scheduled_start = operations[0].scheduled_start
        mo.scheduled_end = operations[-1].scheduled_end
        mo.total_scheduled_duration_minutes = sum(
            op.scheduled_duration_minutes for op in operations
        )

        # Update MO status if still pending
        if mo.status == ManufacturingOrderStatusEnum.PENDING:
            mo.status = ManufacturingOrderStatusEnum.MR_SENT

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(mo)
        
        # Check for overallocation and send warnings
        try:
            from app.modules.notifications.application.services.production_notification_service import (
                ProductionNotificationService,
            )
            notification_service = ProductionNotificationService(self.db)
            
            # Check each unique work center used
            work_centers_checked = set()
            for operation in operations:
                if operation.work_center_id not in work_centers_checked and operation.scheduled_start:
                    work_centers_checked.add(operation.work_center_id)
                    
                    # Get capacity for the operation's scheduled date
                    capacity_info = await self.calculate_work_center_capacity(
                        operation.work_center_id,
                        operation.scheduled_start.date()
                    )
                    
                    # Send warning if overallocated (>100%)
                    if capacity_info["utilization_pct"] > 100:
                        await notification_service.notify_overallocation_warning(
                            work_center_id=operation.work_center_id,
                            date=operation.scheduled_start.date().isoformat(),
                            utilization_pct=capacity_info["utilization_pct"]
                        )
        except Exception as e:
            # Log error but don't fail the scheduling
            print(f"Failed to send overallocation notifications: {e}")

        return mo

    async def reschedule_operation(
        self, operation_id: int, new_start_datetime: datetime
    ) -> ManufacturingOrderOperation:
        """
        Reschedule an existing operation to a new time.
        
        Args:
            operation_id: Operation ID
            new_start_datetime: New start time
            
        Returns:
            Updated operation
            
        Raises:
            ValueError: If operation cannot be rescheduled
        """
        # Fetch operation
        operation = await self.mo_operation_repo.get_by_id(operation_id)
        if not operation:
            raise ValueError(f"Operation {operation_id} not found")

        # Validate status - cannot reschedule completed or in-progress operations
        if operation.status in [
            OperationStatusEnum.COMPLETED,
            OperationStatusEnum.IN_PROGRESS,
        ]:
            raise ValueError(
                f"Cannot reschedule operation with status {operation.status.value}"
            )

        # Store old date for schedule update
        old_date = operation.scheduled_start.date() if operation.scheduled_start else None

        # Calculate new end time
        new_end_datetime = new_start_datetime + timedelta(
            minutes=operation.scheduled_duration_minutes
        )

        # Check for conflicts
        conflicts = await self.detect_scheduling_conflicts(
            operation.work_center_id, new_start_datetime, new_end_datetime, operation_id
        )

        if conflicts:
            raise ValueError(f"Rescheduling would create conflicts")

        # Update operation
        operation.scheduled_start = new_start_datetime
        operation.scheduled_end = new_end_datetime
        operation.status = OperationStatusEnum.SCHEDULED

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(operation)

        # Update work center schedules
        if old_date:
            await self.wc_schedule_repo.update_utilization(
                operation.work_center_id, old_date
            )
        await self.wc_schedule_repo.update_utilization(
            operation.work_center_id, new_start_datetime.date()
        )

        return operation

    async def detect_scheduling_conflicts(
        self,
        work_center_id: int,
        start_datetime: datetime,
        end_datetime: datetime,
        exclude_operation_id: Optional[int] = None,
    ) -> List[ManufacturingOrderOperation]:
        """
        Detect scheduling conflicts in a work center for a given time range.
        
        Args:
            work_center_id: Work Center ID
            start_datetime: Start of time range
            end_datetime: End of time range
            exclude_operation_id: Operation ID to exclude from conflict check
            
        Returns:
            List of conflicting operations
        """
        # Query for overlapping operations
        query = select(ManufacturingOrderOperation).where(
            and_(
                ManufacturingOrderOperation.work_center_id == work_center_id,
                ManufacturingOrderOperation.status.in_(
                    [
                        OperationStatusEnum.SCHEDULED,
                        OperationStatusEnum.IN_PROGRESS,
                    ]
                ),
                ManufacturingOrderOperation.scheduled_start.isnot(None),
                ManufacturingOrderOperation.scheduled_end.isnot(None),
                # Check for overlap: (start1 < end2) AND (end1 > start2)
                and_(
                    ManufacturingOrderOperation.scheduled_start < end_datetime,
                    ManufacturingOrderOperation.scheduled_end > start_datetime,
                ),
            )
        )

        # Exclude specific operation if provided
        if exclude_operation_id:
            query = query.where(ManufacturingOrderOperation.id != exclude_operation_id)

        result = await self.db.execute(query)
        conflicts = result.scalars().all()

        return list(conflicts)
