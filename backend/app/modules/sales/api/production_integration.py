"""
Production Integration API Endpoints for Sales Orders
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.modules.sales.application.services.production_integration_service import (
    ProductionIntegrationService,
)


# Response Schemas
class ManufacturingOrderInfo(BaseModel):
    """Manufacturing order information"""
    mo_id: int
    mo_number: str
    product_id: Optional[int]
    quantity: int
    status: str
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    production_start_at: Optional[datetime]
    end_at: Optional[datetime]
    total_scheduled_duration_minutes: Optional[int]


class ProductionScheduleResponse(BaseModel):
    """Production schedule for sales order"""
    sales_order_id: int
    has_production: bool
    manufacturing_orders: list[ManufacturingOrderInfo]
    overall_status: str
    estimated_delivery_date: Optional[datetime]
    total_mos: int


class DeliveryDateResponse(BaseModel):
    """Delivery date calculation response"""
    sales_order_id: int
    estimated_delivery_date: Optional[datetime]
    is_scheduled: bool
    buffer_days: int


class TimelineEvent(BaseModel):
    """Production timeline event"""
    date: datetime
    event: str
    mo_id: int
    mo_number: str
    details: str


router = APIRouter(prefix="/production-integration", tags=["Production Integration"])


@router.get("/sales-orders/{so_id}/delivery-date", response_model=DeliveryDateResponse)
async def get_delivery_date(
    so_id: int,
    buffer_days: int = Query(default=3, description="Buffer days to add after production"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Calculate estimated delivery date for a sales order based on production schedule.
    
    Returns the estimated delivery date considering all manufacturing orders
    and adding buffer days for packaging/shipping.
    """
    service = ProductionIntegrationService(db)
    
    try:
        estimated_date = await service.calculate_delivery_date(so_id, buffer_days)
        
        return DeliveryDateResponse(
            sales_order_id=so_id,
            estimated_delivery_date=estimated_date,
            is_scheduled=estimated_date is not None,
            buffer_days=buffer_days
        )
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/sales-orders/{so_id}/production-schedule", response_model=ProductionScheduleResponse)
async def get_production_schedule(
    so_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get complete production schedule information for a sales order.
    
    Returns:
        - List of manufacturing orders
        - Overall production status
        - Estimated delivery date
        - Progress information
    """
    service = ProductionIntegrationService(db)
    
    try:
        schedule = await service.get_production_schedule_for_so(so_id)
        return ProductionScheduleResponse(**schedule)
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/sales-orders/{so_id}/update-from-production")
async def update_so_from_production(
    so_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update sales order status and delivery date based on current production status.
    
    This can be called manually or triggered automatically when MO status changes.
    """
    service = ProductionIntegrationService(db)
    
    try:
        updated_so = await service.update_so_status_from_production(so_id)
        return {
            "sales_order_id": so_id,
            "updated_delivery_date": updated_so.delivery_date,
            "message": "Sales order updated from production status"
        }
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/sales-orders/{so_id}/production-timeline", response_model=list[TimelineEvent])
async def get_production_timeline(
    so_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get a chronological timeline of production events for a sales order.
    
    Useful for:
        - Customer communication
        - Order tracking
        - Production history
    
    Returns timeline events sorted by date.
    """
    service = ProductionIntegrationService(db)
    
    try:
        timeline = await service.get_production_timeline(so_id)
        return [TimelineEvent(**event) for event in timeline]
    except ValueError as e:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e))
