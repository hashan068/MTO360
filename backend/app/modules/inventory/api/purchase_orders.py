"""
Purchase Order API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.inventory import (
    PurchaseOrderCreate,
    PurchaseOrderResponse,
)
from app.modules.inventory.application.services.purchase_service import PurchaseService

router = APIRouter(prefix="/api/inventory/purchase-orders", tags=["Purchase Orders"])


@router.get("/", response_model=List[PurchaseOrderResponse])
async def get_purchase_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all purchase orders"""
    service = PurchaseService(db)
    orders = await service.get_purchase_orders(skip=skip, limit=limit)
    return orders


@router.get("/{order_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get purchase order by ID"""
    service = PurchaseService(db)
    order = await service.get_purchase_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    response_data = PurchaseOrderResponse.model_validate(order)
    if order.purchase_requisition:
        response_data.purchase_requisition = {
            "id": order.purchase_requisition.id,
            "component_id": order.purchase_requisition.component_id,
            "quantity": order.purchase_requisition.quantity,
            "status": order.purchase_requisition.status.value,
        }
    return response_data


@router.post("/", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    data: PurchaseOrderCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new purchase order"""
    service = PurchaseService(db)
    order = await service.create_purchase_order(
        creator_id=user_id,
        **data.model_dump()
    )
    response_data = PurchaseOrderResponse.model_validate(order)
    if order.purchase_requisition:
        response_data.purchase_requisition = {
            "id": order.purchase_requisition.id,
            "component_id": order.purchase_requisition.component_id,
            "quantity": order.purchase_requisition.quantity,
            "status": order.purchase_requisition.status.value,
        }
    return response_data

