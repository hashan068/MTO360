"""
Cost Analysis & Reporting API endpoints
"""
from typing import Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.procurement import (
    PriceHistoryResponse,
    SpendAnalysisResponse,
    ProcurementBudgetCreate,
    ProcurementBudgetResponse,
    ProcurementBudgetUpdate,
    BudgetTrackingResponse,
)
from app.models.procurement import PriceChangeSourceEnum
from app.modules.procurement.application.services.cost_analysis_service import CostAnalysisService


router = APIRouter(prefix="/api/v1/procurement/cost-analysis", tags=["Cost Analysis & Reporting"])


@router.get("/price-history/{component_id}", response_model=PriceHistoryResponse)
async def get_price_history(
    component_id: int,
    start_date: Optional[date] = Query(None, description="Start date (default: 1 year ago)"),
    end_date: Optional[date] = Query(None, description="End date (default: today)"),
    supplier_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get price history for a component with trend analysis
    
    Returns:
    - Historical prices with dates
    - Trend (increasing, decreasing, stable)
    - Statistics (avg, min, max, volatility)
    """
    service = CostAnalysisService(db)
    
    try:
        history = await service.get_price_history(
            component_id,
            start_date,
            end_date,
            supplier_id
        )
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving price history: {str(e)}"
        )


@router.get("/spend-analysis", response_model=SpendAnalysisResponse)
async def analyze_spend(
    start_date: date = Query(..., description="Analysis start date"),
    end_date: date = Query(..., description="Analysis end date"),
    group_by: str = Query("supplier", regex="^(supplier|category|month)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze procurement spend with breakdowns
    
    Group by:
    - supplier: Spend by supplier
    - category: Spend by component category
    - month: Spend by month
    
    Includes supplier concentration metrics (top 3, top 10)
    """
    service = CostAnalysisService(db)
    
    try:
        analysis = await service.analyze_spend(start_date, end_date, group_by)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing spend: {str(e)}"
        )


@router.post("/budgets", response_model=ProcurementBudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    data: ProcurementBudgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Create or update procurement budget
    
    Budgets can be set at overall level or by category.
    """
    service = CostAnalysisService(db)
    
    try:
        budget = await service.get_or_create_budget(
            fiscal_year=data.fiscal_year,
            category_id=data.category_id,
            budgeted_amount=data.budgeted_amount
        )
        return budget
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating budget: {str(e)}"
        )


@router.get("/budgets/{fiscal_year}", response_model=BudgetTrackingResponse)
async def get_budget_tracking(
    fiscal_year: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get budget tracking for a fiscal year
    
    Returns:
    - All budgets with actual spend
    - Variance and percentage consumed
    - Status (on_track, at_risk, over_budget)
    - Overall totals
    """
    service = CostAnalysisService(db)
    
    try:
        tracking = await service.get_budget_tracking(fiscal_year)
        return tracking
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting budget tracking: {str(e)}"
        )


@router.post("/budgets/{fiscal_year}/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh_budget_actuals(
    fiscal_year: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Refresh actual spend and variance for all budgets in a fiscal year
    
    This recalculates actual spend from purchase orders.
    """
    service = CostAnalysisService(db)
    
    try:
        await service.update_budget_actuals(fiscal_year)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing budget actuals: {str(e)}"
        )
