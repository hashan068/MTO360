"""
Manufacturing Order API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.manufacturing import ManufacturingOrderCreate, ManufacturingOrderResponse
from app.modules.manufacturing.application.services.manufacturing_service import ManufacturingService

router = APIRouter(prefix="/api/manufacturing/orders", tags=["Manufacturing Orders"])


@router.get("/", response_model=List[ManufacturingOrderResponse])
async def get_manufacturing_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all manufacturing orders"""
    service = ManufacturingService(db)
    orders = await service.get_manufacturing_orders(skip=skip, limit=limit)
    for order in orders:
        if order.product:
            order.product_name = order.product.name
        if order.created_at:
            order.created_at_date = order.created_at.date().isoformat()
    return orders


@router.get("/{order_id}", response_model=ManufacturingOrderResponse)
async def get_manufacturing_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get manufacturing order by ID"""
    service = ManufacturingService(db)
    order = await service.get_manufacturing_order(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manufacturing order not found")
    if order.product:
        order.product_name = order.product.name
    if order.created_at:
        order.created_at_date = order.created_at.date().isoformat()
    return order


@router.post("/", response_model=ManufacturingOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_manufacturing_order(
    data: ManufacturingOrderCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new manufacturing order"""
    service = ManufacturingService(db)
    order = await service.create_manufacturing_order(
        product_id=data.product_id,
        sales_order_item_id=data.sales_order_item_id,
        quantity=data.quantity,
        creator_id=user_id,
    )
    if order.product:
        order.product_name = order.product.name
    if order.created_at:
        order.created_at_date = order.created_at.date().isoformat()
    return order

