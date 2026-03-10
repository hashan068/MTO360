"""
Quality Analytics API endpoints
Provides quality metrics, KPIs, and dashboard data
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.modules.quality.application.services import QualityAnalyticsService

router = APIRouter(prefix="/api/quality/analytics", tags=["Quality - Analytics"])


@router.get("/dashboard")
def get_quality_dashboard(
    days_back: int = 30,
    db: Session = Depends(get_db),
):
    """
    Get comprehensive quality dashboard
    Includes all key metrics, trends, and alerts
    """
    service = QualityAnalyticsService(db)
    return service.get_quality_dashboard(days_back=days_back)


@router.get("/metrics/first-pass-yield")
def get_first_pass_yield(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """
    Calculate First Pass Yield (FPY)
    FPY = (Units passing first inspection / Total units inspected) * 100
    """
    service = QualityAnalyticsService(db)
    return service.calculate_first_pass_yield(start_date, end_date)


@router.get("/metrics/defect-rate")
def get_defect_rate(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    per_units: int = 1000,
    db: Session = Depends(get_db),
):
    """
    Calculate defect rate (defects per X units)
    Default: defects per 1000 units
    """
    service = QualityAnalyticsService(db)
    return service.calculate_defect_rate(start_date, end_date, per_units)


@router.get("/metrics/cost-of-quality")
def get_cost_of_quality(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """
    Calculate total Cost of Quality (COQ)
    Includes internal failure, rework, appraisal, and prevention costs
    """
    service = QualityAnalyticsService(db)
    return service.calculate_cost_of_quality(start_date, end_date)


@router.get("/metrics/rework-rate")
def get_rework_rate(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Calculate rework rate and total rework costs"""
    service = QualityAnalyticsService(db)
    return service.calculate_rework_rate(start_date, end_date)


@router.get("/metrics/scrap-rate")
def get_scrap_rate(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Calculate scrap rate and total scrap costs"""
    service = QualityAnalyticsService(db)
    return service.calculate_scrap_rate(start_date, end_date)


@router.get("/performance/operator/{operator_id}")
def get_operator_quality_performance(
    operator_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Get quality performance metrics for an operator"""
    service = QualityAnalyticsService(db)
    return service.get_operator_quality_performance(operator_id, start_date, end_date)


@router.get("/performance/supplier/{supplier_id}")
def get_supplier_quality_performance(
    supplier_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Get quality performance metrics for a supplier"""
    service = QualityAnalyticsService(db)
    return service.get_supplier_quality_performance(supplier_id, start_date, end_date)


@router.get("/trends/{metric}")
def get_quality_trends(
    metric: str,  # fpy, defect_rate, ncr_count
    period: str = "weekly",  # daily, weekly, monthly
    weeks_back: int = 12,
    db: Session = Depends(get_db),
):
    """
    Get quality trends over time for specified metric
    Returns time-series data for charting
    """
    service = QualityAnalyticsService(db)
    return service.get_quality_trends(metric, period, weeks_back)
