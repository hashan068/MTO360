"""
Analytics Service - Production performance analytics and reporting
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, case, desc
from decimal import Decimal

from app.models.manufacturing import (
    ManufacturingOrder,
    ManufacturingOrderOperation,
    WorkCenter,
    WorkCenterSchedule,
    OperationStatusEnum,
    ManufacturingOrderStatusEnum,
)
from app.modules.manufacturing.infra.repositories.work_center_repo import (
    WorkCenterRepository as WorkCenterRepositoryImpl,
)
from app.modules.manufacturing.infra.repositories.work_center_schedule_repo import (
    WorkCenterScheduleRepository,
)


class AnalyticsService:
    """Service for production analytics and reporting"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.work_center_repo = WorkCenterRepositoryImpl(db)
        self.wc_schedule_repo = WorkCenterScheduleRepository(db)

    async def get_utilization_report(
        self,
        start_date: date,
        end_date: date,
        work_center_id: Optional[int] = None,
    ) -> List[Dict]:
        """
        Get capacity utilization report over a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            work_center_id: Optional work center filter
            
        Returns:
            List of utilization data points
        """
        # Build query for work center schedules
        query = select(WorkCenterSchedule).where(
            and_(
                WorkCenterSchedule.date >= start_date,
                WorkCenterSchedule.date <= end_date,
            )
        )

        if work_center_id:
            query = query.where(WorkCenterSchedule.work_center_id == work_center_id)

        result = await self.db.execute(query)
        schedules = result.scalars().all()

        # Enrich with work center names and classify utilization
        utilization_data = []
        for schedule in schedules:
            # Get work center name
            work_center = await self.work_center_repo.get_by_id(
                schedule.work_center_id
            )

            # Calculate utilization
            utilization_pct = float(schedule.utilization_percentage)

            # Classify utilization status
            if utilization_pct < 60:
                status = "underutilized"
            elif utilization_pct <= 85:
                status = "optimal"
            else:
                status = "overallocated"

            utilization_data.append(
                {
                    "work_center_id": schedule.work_center_id,
                    "work_center_name": work_center.name if work_center else "Unknown",
                    "date": schedule.date,
                    "capacity_minutes": schedule.available_capacity_minutes,
                    "scheduled_minutes": schedule.scheduled_capacity_minutes,
                    "utilization_pct": utilization_pct,
                    "status": status,
                }
            )

        return utilization_data

    async def get_bottleneck_analysis(
        self, limit: int = 10
    ) -> List[Dict]:
        """
        Identify production bottlenecks by analyzing work center metrics.
        
        Bottlenecks are work centers with:
        - High utilization
        - Large queue of pending operations
        - Long average wait times
        
        Args:
            limit: Max number of bottlenecks to return
            
        Returns:
            List of bottleneck info, ranked by score
        """
        # Get all active work centers
        work_centers = await self.work_center_repo.get_active_work_centers()

        bottleneck_data = []

        for wc in work_centers:
            # Calculate average utilization (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=30)

            utilization_query = select(
                func.avg(WorkCenterSchedule.utilization_percentage)
            ).where(
                and_(
                    WorkCenterSchedule.work_center_id == wc.id,
                    WorkCenterSchedule.date >= start_date,
                    WorkCenterSchedule.date <= end_date,
                )
            )
            avg_utilization = (await self.db.execute(utilization_query)).scalar()
            avg_utilization = float(avg_utilization) if avg_utilization else 0.0

            # Count pending operations
            pending_query = select(
                func.count(ManufacturingOrderOperation.id)
            ).where(
                and_(
                    ManufacturingOrderOperation.work_center_id == wc.id,
                    ManufacturingOrderOperation.status.in_(
                        [OperationStatusEnum.PENDING, OperationStatusEnum.SCHEDULED]
                    ),
                )
            )
            pending_count = (await self.db.execute(pending_query)).scalar() or 0

            # Calculate average wait time (simplified)
            # Wait time = time from MO creation to operation scheduled_start
            wait_time_query = select(
                func.avg(
                    func.extract(
                        "epoch",
                        ManufacturingOrderOperation.scheduled_start
                        - ManufacturingOrder.created_at,
                    )
                    / 3600.0  # Convert to hours
                )
            ).where(
                and_(
                    ManufacturingOrderOperation.work_center_id == wc.id,
                    ManufacturingOrderOperation.scheduled_start.isnot(None),
                    ManufacturingOrderOperation.manufacturing_order_id
                    == ManufacturingOrder.id,
                )
            )

            # Note: This join requires accessing MO table
            # Simplified version without join for now
            avg_wait_time = 0.0  # TODO: Implement proper join query

            # Calculate bottleneck score
            # Higher score = bigger bottleneck
            bottleneck_score = (
                (avg_utilization * 0.4) +
                (pending_count * 5 * 0.3) +
                (avg_wait_time * 0.3)
            )

            bottleneck_data.append(
                {
                    "work_center_id": wc.id,
                    "work_center_name": wc.name,
                    "avg_utilization_pct": round(avg_utilization, 2),
                    "pending_operations_count": pending_count,
                    "avg_wait_time_hours": round(avg_wait_time, 2),
                    "bottleneck_score": round(bottleneck_score, 2),
                }
            )

        # Sort by bottleneck score (highest first) and add rank
        bottleneck_data.sort(key=lambda x: x["bottleneck_score"], reverse=True)

        for idx, item in enumerate(bottleneck_data[:limit], 1):
            item["rank"] = idx

        return bottleneck_data[:limit]

    async def get_operation_performance(
        self,
        work_center_id: Optional[int] = None,
        product_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """
        Analyze operation performance comparing actual vs estimated times.
        
        Args:
            work_center_id: Optional work center filter
            product_id: Optional product filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of performance metrics by operation type
        """
        # Build query for completed operations
        query_filters = [
            ManufacturingOrderOperation.status == OperationStatusEnum.COMPLETED,
            ManufacturingOrderOperation.actual_duration_minutes.isnot(None),
        ]

        if work_center_id:
            query_filters.append(
                ManufacturingOrderOperation.work_center_id == work_center_id
            )

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query_filters.append(
                ManufacturingOrderOperation.actual_end >= start_datetime
            )

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query_filters.append(
                ManufacturingOrderOperation.actual_end <= end_datetime
            )

        # Group by operation name and route_operation_id
        query = (
            select(
                ManufacturingOrderOperation.name,
                ManufacturingOrderOperation.route_operation_id,
                func.count(ManufacturingOrderOperation.id).label("completed_count"),
                func.avg(ManufacturingOrderOperation.scheduled_duration_minutes).label(
                    "avg_scheduled"
                ),
                func.avg(ManufacturingOrderOperation.actual_duration_minutes).label(
                    "avg_actual"
                ),
            )
            .where(and_(*query_filters))
            .group_by(
                ManufacturingOrderOperation.name,
                ManufacturingOrderOperation.route_operation_id,
            )
        )

        result = await self.db.execute(query)
        rows = result.all()

        performance_data = []
        for row in rows:
            avg_scheduled = float(row.avg_scheduled)
            avg_actual = float(row.avg_actual)
            avg_variance = avg_actual - avg_scheduled

            # Calculate accuracy percentage
            # 100% = perfect, lower = worse accuracy
            if avg_scheduled > 0:
                accuracy_pct = (1 - abs(avg_variance) / avg_scheduled) * 100
                accuracy_pct = max(0, min(100, accuracy_pct))  # Clamp to 0-100
            else:
                accuracy_pct = 0

            # Count on-time vs late (simplified)
            # On-time if actual <= scheduled * 1.1 (10% tolerance)
            on_time_count = 0  # TODO: Implement precise counting
            late_count = 0

            performance_data.append(
                {
                    "operation_name": row.name,
                    "route_operation_id": row.route_operation_id,
                    "completed_count": row.completed_count,
                    "avg_scheduled_minutes": round(avg_scheduled, 2),
                    "avg_actual_minutes": round(avg_actual, 2),
                    "avg_variance_minutes": round(avg_variance, 2),
                    "accuracy_pct": round(accuracy_pct, 2),
                    "on_time_count": on_time_count,
                    "late_count": late_count,
                }
            )

        # Sort by completed count (most frequent first)
        performance_data.sort(key=lambda x: x["completed_count"], reverse=True)

        return performance_data

    async def get_cycle_time_analysis(
        self,
        product_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict]:
        """
        Analyze manufacturing cycle times per product.
        
        Cycle time = time from first operation start to last operation end
        
        Args:
            product_id: Optional product filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of cycle time metrics per product
        """
        # Build query for completed MOs
        query_filters = [
            ManufacturingOrder.status == ManufacturingOrderStatusEnum.COMPLETED,
            ManufacturingOrder.production_start_at.isnot(None),
            ManufacturingOrder.end_at.isnot(None),
        ]

        if product_id:
            query_filters.append(ManufacturingOrder.product_id == product_id)

        if start_date:
            start_datetime = datetime.combine(start_date, datetime.min.time())
            query_filters.append(ManufacturingOrder.end_at >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query_filters.append(ManufacturingOrder.end_at <= end_datetime)

        # Group by product_id
        # Calculate cycle time as interval between production_start_at and end_at
        query = (
            select(
                ManufacturingOrder.product_id,
                func.count(ManufacturingOrder.id).label("mo_count"),
                func.avg(
                    func.extract(
                        "epoch", ManufacturingOrder.end_at - ManufacturingOrder.production_start_at
                    )
                    / 3600.0  # Convert to hours
                ).label("avg_cycle_time_hours"),
                func.min(
                    func.extract(
                        "epoch", ManufacturingOrder.end_at - ManufacturingOrder.production_start_at
                    )
                    / 3600.0
                ).label("min_cycle_time_hours"),
                func.max(
                    func.extract(
                        "epoch", ManufacturingOrder.end_at - ManufacturingOrder.production_start_at
                    )
                    / 3600.0
                ).label("max_cycle_time_hours"),
                func.avg(ManufacturingOrder.total_scheduled_duration_minutes / 60.0).label(
                    "avg_scheduled_hours"
                ),
            )
            .where(and_(*query_filters))
            .group_by(ManufacturingOrder.product_id)
        )

        result = await self.db.execute(query)
        rows = result.all()

        cycle_time_data = []
        for row in rows:
            avg_cycle = float(row.avg_cycle_time_hours) if row.avg_cycle_time_hours else 0
            avg_scheduled = (
                float(row.avg_scheduled_hours) if row.avg_scheduled_hours else 0
            )

            # Calculate on-time completion rate
            # Simplified: if avg_cycle <= avg_scheduled * 1.1, considered on-time
            if avg_scheduled > 0:
                on_time_rate = min(100, (avg_scheduled / avg_cycle) * 100)
            else:
                on_time_rate = 0

            # Determine trend (simplified - would need historical comparison)
            # For now, use static "stable" - TODO: implement trend calculation
            trend = "stable"

            cycle_time_data.append(
                {
                    "product_id": row.product_id,
                    "product_name": None,  # TODO: Join with products table
                    "mo_count": row.mo_count,
                    "avg_cycle_time_hours": round(avg_cycle, 2),
                    "min_cycle_time_hours": round(float(row.min_cycle_time_hours), 2),
                    "max_cycle_time_hours": round(float(row.max_cycle_time_hours), 2),
                    "avg_scheduled_duration_hours": round(avg_scheduled, 2),
                    "on_time_completion_rate": round(on_time_rate, 2),
                    "trend": trend,
                }
            )

        # Sort by MO count (most manufactured first)
        cycle_time_data.sort(key=lambda x: x["mo_count"], reverse=True)

        return cycle_time_data
