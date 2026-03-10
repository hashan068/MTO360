"""
Inventory Optimization API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.procurement import (
    ComponentInventoryPolicyCreate,
    ComponentInventoryPolicyResponse,
    ComponentInventoryPolicyUpdate,
    ComponentBelowROPResponse,
    ABCAnalysisResponse,
)
from app.modules.procurement.application.services.inventory_optimization_service import InventoryOptimizationService


router = APIRouter(prefix="/api/v1/procurement/inventory", tags=["Inventory Optimization"])


@router.post("/policies", response_model=ComponentInventoryPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_policy(
    data: ComponentInventoryPolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Create or update inventory policy for a component
    
    Automatically calculates:
    - Reorder Point (ROP)
    - Safety Stock
    - Economic Order Quantity (EOQ)
    - ABC Classification
    """
    service = InventoryOptimizationService(db)
    
    try:
        policy = await service.create_or_update_inventory_policy(
            component_id=data.component_id,
            average_monthly_demand=data.average_monthly_demand,
            lead_time_days=data.lead_time_days,
            ordering_cost=data.ordering_cost,
            holding_cost_pct=data.holding_cost_pct,
            auto_pr_enabled=data.auto_pr_enabled,
            updated_by=current_user_id
        )
        return policy
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating inventory policy: {str(e)}"
        )


@router.get("/below-rop", response_model=List[ComponentBelowROPResponse])
async def get_components_below_rop(
    db: AsyncSession = Depends(get_db),
):
    """
    Get components below reorder point
    
    Returns components that need replenishment with priority levels.
    """
    service = InventoryOptimizationService(db)
    
    try:
        components = await service.get_components_below_rop()
        return components
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting components below ROP: {str(e)}"
        )


@router.get("/abc-analysis", response_model=ABCAnalysisResponse)
async def perform_abc_analysis(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db),
):
    """
    Perform ABC Analysis on components
    
    Classifies components into:
    - A items: High value (top 80% of value)
    - B items: Medium value (next 15% of value)
    - C items: Low value (remaining 5% of value)
    """
    service = InventoryOptimizationService(db)
    
    try:
        analysis = await service.perform_abc_analysis(category_id)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing ABC analysis: {str(e)}"
        )


@router.post("/calculate-rop", response_model=dict)
async def calculate_reorder_point(
    component_id: int,
    average_daily_demand: int = Query(..., gt=0),
    lead_time_days: int = Query(..., gt=0),
    service_level_z: Decimal = Query(Decimal("1.65"), description="Z-score for service level (1.65=95%)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate Reorder Point for a component
    
    Returns ROP, safety stock, and calculation details.
    Does not save to database - use POST /policies to save.
    """
    service = InventoryOptimizationService(db)
    
    try:
        result = await service.calculate_reorder_point(
            component_id,
            average_daily_demand,
            lead_time_days,
            service_level_z
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating ROP: {str(e)}"
        )


@router.post("/calculate-eoq", response_model=dict)
async def calculate_economic_order_quantity(
    annual_demand: int = Query(..., gt=0),
    ordering_cost: Decimal = Query(..., gt=0),
    unit_cost: Decimal = Query(..., gt=0),
    holding_cost_pct: Decimal = Query(Decimal("25.00"), gt=0, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate Economic Order Quantity
    
    Returns EOQ and total cost analysis.
    Does not save to database - use POST /policies to save.
    """
    service = InventoryOptimizationService(db)
    
    try:
        result = await service.calculate_economic_order_quantity(
            annual_demand,
            ordering_cost,
            unit_cost,
            holding_cost_pct
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating EOQ: {str(e)}"
        )
