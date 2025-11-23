"""
Analytics API Endpoints - Production performance analytics and reporting
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.config.database import get_db
from app.modules.manufacturing.application.services.analytics_service import (
    AnalyticsService,
)


# Response Schemas
class UtilizationDataPoint(BaseModel):
    """Capacity utilization data point"""
    work_center_id: int
    work_center_name: str
    date: date
    capacity_minutes: int
    scheduled_minutes: int
    utilization_pct: float
    status: str  # underutilized, optimal, overallocated


class BottleneckInfo(BaseModel):
    """Bottleneck analysis information"""
    work_center_id: int
    work_center_name: str
    avg_utilization_pct: float
    pending_operations_count: int
    avg_wait_time_hours: float
    bottleneck_score: float
    rank: int


class OperationPerformance(BaseModel):
    """Operation performance metrics"""
    operation_name: str
    route_operation_id: Optional[int]
    completed_count: int
    avg_scheduled_minutes: float
    avg_actual_minutes: float
    avg_variance_minutes: float
    accuracy_pct: float
    on_time_count: int
    late_count: int


class CycleTimeMetrics(BaseModel):
    """Cycle time analysis metrics"""
    product_id: Optional[int]
    product_name: Optional[str]
    mo_count: int
    avg_cycle_time_hours: float
    min_cycle_time_hours: float
    max_cycle_time_hours: float
    avg_scheduled_duration_hours: float
    on_time_completion_rate: float
    trend: str  # improving, stable, degrading


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/capacity-utilization", response_model=List[UtilizationDataPoint])
async def get_capacity_utilization(
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    work_center_id: Optional[int] = Query(None, description="Filter by work center"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get capacity utilization report over a date range.
    
    Returns daily utilization metrics for each work center showing:
    - Capacity vs scheduled minutes
    - Utilization percentage
    - Status classification (underutilized, optimal, overallocated)
    
    Use this to:
    - Identify underutilized work centers
    - Find overallocated capacity
    - Balance workload across work centers
    """
    # Validate date range
    if end_date < start_date:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="end_date must be after start_date",
        )

    # Limit to reasonable range
    days_diff = (end_date - start_date).days
    if days_diff > 365:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 365 days",
        )

    service = AnalyticsService(db)

    utilization_data = await service.get_utilization_report(
        start_date, end_date, work_center_id
    )

    return [UtilizationDataPoint(**item) for item in utilization_data]


@router.get("/bottlenecks", response_model=List[BottleneckInfo])
async def get_bottlenecks(
    limit: int = Query(10, ge=1, le=50, description="Max number of bottlenecks to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Identify production bottlenecks by analyzing work center metrics.
    
    Bottleneck score is calculated from:
    - Average utilization (40% weight)
    - Pending operations count (30% weight)
    - Average wait time (30% weight)
    
    Returns work centers ranked by bottleneck score (highest first).
    
    Use this to:
    - Focus improvement efforts on biggest constraints
    - Allocate additional resources
    - Identify capacity expansion needs
    """
    service = AnalyticsService(db)

    bottlenecks = await service.get_bottleneck_analysis(limit)

    return [BottleneckInfo(**item) for item in bottlenecks]


@router.get("/operation-performance", response_model=List[OperationPerformance])
async def get_operation_performance(
    work_center_id: Optional[int] = Query(None, description="Filter by work center"),
    product_id: Optional[int] = Query(None, description="Filter by product"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze operation performance comparing actual vs estimated times.
    
    Returns metrics for each operation type showing:
    - Average scheduled vs actual duration
    - Variance (positive = took longer than expected)
    - Accuracy percentage (100% = perfect estimate)
    - On-time vs late count
    
    Use this to:
    - Improve time estimates
    - Identify operations needing efficiency improvements
    - Find training opportunities
    - Validate standard times
    """
    # Validate date range if both provided
    if start_date and end_date and end_date < start_date:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="end_date must be after start_date",
        )

    service = AnalyticsService(db)

    performance_data = await service.get_operation_performance(
        work_center_id, product_id, start_date, end_date
    )

    return [OperationPerformance(**item) for item in performance_data]


@router.get("/cycle-times", response_model=List[CycleTimeMetrics])
async def get_cycle_times(
    product_id: Optional[int] = Query(None, description="Filter by product"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze manufacturing cycle times per product.
    
    Cycle time = time from first operation start to last operation completion
    
    Returns metrics per product showing:
    - Average, min, max cycle time
    - Comparison to scheduled duration
    - On-time completion rate
    - Trend (improving, stable, degrading)
    
    Use this to:
    - Set accurate delivery promises
    - Track lead time improvements
    - Identify products with long cycle times
    - Measure continuous improvement initiatives
    """
    # Validate date range
    if start_date and end_date and end_date < start_date:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="end_date must be after start_date",
        )

    service = AnalyticsService(db)

    cycle_time_data = await service.get_cycle_time_analysis(
        product_id, start_date, end_date
    )

    return [CycleTimeMetrics(**item) for item in cycle_time_data]
