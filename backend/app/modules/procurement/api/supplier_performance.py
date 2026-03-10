"""
Supplier Performance API endpoints
"""
from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.procurement import (
    SupplierPerformanceCreate,
    SupplierPerformanceResponse,
    SupplierRankingResponse,
)
from app.modules.procurement.application.services.supplier_performance_service import SupplierPerformanceService


router = APIRouter(prefix="/api/v1/procurement/suppliers", tags=["Supplier Performance"])


@router.get("/{supplier_id}/performance", response_model=List[SupplierPerformanceResponse])
async def get_supplier_performance(
    supplier_id: int,
    start_date: Optional[date] = Query(None, description="Start date (default: 6 months ago)"),
    end_date: Optional[date] = Query(None, description="End date (default: today)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get supplier performance metrics history
    
    Returns monthly performance records for the specified date range.
    Includes on-time delivery, quality rating, price competitiveness, and overall score.
    """
    service = SupplierPerformanceService(db)
    
    # Set defaults if not provided
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=180)  # 6 months ago
    
    performance_records = await service.get_supplier_performance(
        supplier_id,
        start_date,
        end_date
    )
    
    if not performance_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No performance data found for supplier {supplier_id} in the specified period"
        )
    
    return performance_records


@router.get("/rankings", response_model=List[SupplierRankingResponse])
async def get_supplier_rankings(
    category_id: Optional[int] = Query(None, description="Filter by component category"),
    limit: int = Query(10, ge=1, le=100, description="Number of top suppliers to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get supplier rankings by overall performance score
    
    Returns top suppliers ranked by their latest overall performance score.
    Optionally filter by component category.
    """
    service = SupplierPerformanceService(db)
    rankings = await service.get_supplier_rankings(category_id, limit)
    
    if not rankings:
        return []
    
    return rankings


@router.post("/{supplier_id}/performance/calculate", response_model=SupplierPerformanceResponse)
async def calculate_supplier_performance(
    supplier_id: int,
    data: SupplierPerformanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Manually trigger performance calculation for a supplier
    
    Calculates all performance metrics for the specified period and stores the results.
    Requires procurement_manager or admin role.
    
    Period should be the first day of the month to calculate.
    """
    service = SupplierPerformanceService(db)
    
    # Validate period is first day of month
    if data.period.day != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period must be the first day of a month"
        )
    
    # Validate supplier_id matches route parameter
    if data.supplier_id != supplier_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier ID in body must match route parameter"
        )
    
    try:
        performance = await service.calculate_supplier_performance(
            supplier_id,
            data.period
        )
        return performance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating performance: {str(e)}"
        )


@router.get("/preferred", response_model=List[dict])
async def get_preferred_suppliers(
    category_id: Optional[int] = Query(None, description="Filter by component category"),
    min_score: Decimal = Query(Decimal("75.00"), ge=0, le=100, description="Minimum score to be preferred"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of preferred suppliers
    
    Returns suppliers with performance score >= min_score (default 75).
    These suppliers are recommended for RFQs and POs.
    """
    service = SupplierPerformanceService(db)
    preferred = await service.get_preferred_suppliers(category_id, min_score)
    
    return preferred
