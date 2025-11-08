"""
Sales Order API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.sales import SalesOrderCreate, SalesOrderResponse
from app.modules.sales.application.services.sales_order_service import SalesOrderService

router = APIRouter(prefix="/api/sales/sales-orders", tags=["Sales Orders"])


@router.get("/", response_model=List[SalesOrderResponse])
async def get_sales_orders(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get all sales orders with optional date filtering"""
    service = SalesOrderService(db)
    orders = await service.get_sales_orders(
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )
    # Add customer_name and created_at_date for response
    for order in orders:
        if order.customer:
            order.customer_name = order.customer.name
        if order.created_at:
            order.created_at_date = order.created_at.date()
        # Add product names to items
        for item in order.order_items:
            if item.product:
                item.product_name = item.product.name
            item.sales_order_item_id = item.id
    return orders


@router.get("/{order_id}", response_model=SalesOrderResponse)
async def get_sales_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get sales order by ID"""
    service = SalesOrderService(db)
    order = await service.get_sales_order(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
    if order.customer:
        order.customer_name = order.customer.name
    if order.created_at:
        order.created_at_date = order.created_at.date()
    for item in order.order_items:
        if item.product:
            item.product_name = item.product.name
        item.sales_order_item_id = item.id
    return order


@router.post("/", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    data: SalesOrderCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new sales order"""
    service = SalesOrderService(db)
    order = await service.create_sales_order(
        customer_id=data.customer_id,
        order_items=[item.model_dump() for item in data.order_items],
    )
    if order.customer:
        order.customer_name = order.customer.name
    if order.created_at:
        order.created_at_date = order.created_at.date()
    for item in order.order_items:
        if item.product:
            item.product_name = item.product.name
        item.sales_order_item_id = item.id
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sales_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete sales order"""
    service = SalesOrderService(db)
    result = await service.delete_sales_order(order_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sales_order_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete sales order item"""
    service = SalesOrderService(db)
    result = await service.delete_sales_order_item(item_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order item not found")

