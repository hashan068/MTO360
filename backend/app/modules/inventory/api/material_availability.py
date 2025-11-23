"""
Material Availability API Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.modules.inventory.application.services.material_availability_service import (
    MaterialAvailabilityService,
)


# Request/Response Schemas
class ComponentAvailabilityResponse(BaseModel):
    """Component availability details"""
    component_id: int
    component_name: str
    component_code: Optional[str]
    required_quantity: float
    available_quantity: float
    unit: str
    is_available: bool
    shortage: float


class BOMAvailabilityResponse(BaseModel):
    """BOM availability check response"""
    all_available: bool
    components: List[ComponentAvailabilityResponse]
    missing_components: List[ComponentAvailabilityResponse]


class ComponentIndicatorResponse(BaseModel):
    """Component availability indicator"""
    component_id: int
    component_name: str
    component_code: Optional[str]
    quantity_on_hand: float
    reorder_point: float
    unit: str
    status: str  # "available", "low", "out_of_stock"


class MaterialValidationResponse(BaseModel):
    """Material validation for MO"""
    can_schedule: bool
    availability: Optional[BOMAvailabilityResponse]
    estimated_ready_date: Optional[datetime]
    blocking_reason: Optional[str]


router = APIRouter(prefix="/material-availability", tags=["Material Availability"])


@router.get("/bom/{bom_id}", response_model=BOMAvailabilityResponse)
async def check_bom_availability(
    bom_id: int,
    quantity: int = Query(..., description="Quantity to produce"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Check material availability for a Bill of Materials.
    
    Returns component-level availability details including shortages.
    """
    service = MaterialAvailabilityService(db)
    
    try:
        availability = await service.check_bom_availability(bom_id, quantity)
        return BOMAvailabilityResponse(**availability)
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/components/indicators", response_model=List[ComponentIndicatorResponse])
async def get_component_indicators(
    component_ids: str = Query(..., description="Comma-separated component IDs"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get availability indicators for multiple components.
    
    Returns current stock levels and status (available/low/out_of_stock).
    """
    # Parse component IDs
    try:
        ids = [int(id.strip()) for id in component_ids.split(",")]
    except ValueError:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Invalid component_ids format. Expected comma-separated integers."
        )
    
    service = MaterialAvailabilityService(db)
    indicators = await service.get_availability_indicators(ids)
    
    return [ComponentIndicatorResponse(**indicator) for indicator in indicators.values()]


@router.get("/mo/{mo_id}/validate", response_model=MaterialValidationResponse)
async def validate_mo_materials(
    mo_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Validate material availability for a manufacturing order.
    
    Returns:
        - Whether the MO can be scheduled
        - Material availability details
        - Estimated date when materials will be ready
        - Blocking reason if cannot schedule
    """
    service = MaterialAvailabilityService(db)
    
    try:
        validation = await service.validate_materials_for_mo(mo_id)
        return MaterialValidationResponse(**validation)
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/mo/{mo_id}/shortages", response_model=List[ComponentAvailabilityResponse])
async def get_mo_material_shortages(
    mo_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get list of material shortages for a manufacturing order.
    
    Returns details of components with insufficient stock.
    """
    service = MaterialAvailabilityService(db)
    
    try:
        shortages = await service.get_material_shortages(mo_id)
        return [ComponentAvailabilityResponse(**shortage) for shortage in shortages]
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/bom/{bom_id}/ready-date")
async def calculate_material_ready_date(
    bom_id: int,
    quantity: int = Query(..., description="Quantity to produce"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Calculate estimated date when all materials will be available.
    
    Based on lead times and pending orders.
    """
    service = MaterialAvailabilityService(db)
    
    try:
        ready_date = await service.calculate_material_ready_date(bom_id, quantity)
        return {
            "bom_id": bom_id,
            "quantity": quantity,
            "estimated_ready_date": ready_date,
            "is_ready_now": ready_date is not None and ready_date <= datetime.utcnow()
        }
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))
