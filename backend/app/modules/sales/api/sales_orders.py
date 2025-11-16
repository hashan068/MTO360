"""
Sales Order API endpoints
"""
from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.sales import (
    SalesOrderCreate,
    SalesOrderResponse,
    SalesOrderStatusUpdate,
)
from app.models.sales import SalesOrderStatusEnum
from app.modules.sales.application.services.sales_order_service import SalesOrderService
from app.modules.sales.domain.exceptions import (
    DocumentNotFoundError,
    InvalidStatusTransitionError,
    DocumentLockedException,
    ValidationError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sales/orders", tags=["Sales Orders"])


@router.get("/", response_model=List[SalesOrderResponse])
async def get_sales_orders(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    status: Optional[SalesOrderStatusEnum] = Query(None, description="Filter by sales order status"),
    search: Optional[str] = Query(None, description="Search by order number, customer name"),
    db: AsyncSession = Depends(get_db),
):
    """Get all sales orders with filtering and search"""
    service = SalesOrderService(db)
    orders = await service.get_sales_orders(
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        status_filter=status,
        search=search,
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
        # Set computed field
        order.can_edit = service.can_edit(order)
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
    # Set computed field
    order.can_edit = service.can_edit(order)
    return order


@router.post("/", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    data: SalesOrderCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new sales order"""
    try:
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
        # Set computed field
        order.can_edit = service.can_edit(order)
        logger.info(f"Created Sales Order {order.id} by user {user_id}")
        return order
    except ValidationError as e:
        logger.warning(f"Validation error creating sales order: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating sales order: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the sales order"
        )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sales_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete sales order"""
    try:
        service = SalesOrderService(db)
        result = await service.delete_sales_order(order_id)
        if not result:
            logger.warning(f"Sales order {order_id} not found for deletion")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
        logger.info(f"Deleted Sales Order {order_id} by user {user_id}")
    except HTTPException:
        raise
    except DocumentLockedException as e:
        logger.warning(f"Attempt to delete locked sales order {order_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting sales order {order_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the sales order"
        )


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


@router.put("/{order_id}/status", response_model=SalesOrderResponse)
async def update_sales_order_status(
    order_id: int,
    data: SalesOrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update sales order status"""
    service = SalesOrderService(db)
    try:
        order = await service.update_sales_order_status(
            order_id=order_id,
            new_status=data.status,
            user_id=user_id,
        )
        if order.customer:
            order.customer_name = order.customer.name
        if order.created_at:
            order.created_at_date = order.created_at.date()
        for item in order.order_items:
            if item.product:
                item.product_name = item.product.name
            item.sales_order_item_id = item.id
        # Set computed field
        order.can_edit = service.can_edit(order)
        logger.info(f"Updated Sales Order {order_id} status to {data.status.value} by user {user_id}")
        return order
    except DocumentNotFoundError as e:
        logger.warning(f"Sales order {order_id} not found for status update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStatusTransitionError as e:
        logger.warning(f"Invalid status transition for sales order {order_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error updating sales order {order_id} status: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating sales order {order_id} status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating sales order status"
        )

