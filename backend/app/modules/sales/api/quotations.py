"""
Quotation API endpoints
"""
from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.sales import (
    QuotationCreate,
    QuotationResponse,
    QuotationStatusUpdate,
    SalesOrderResponse,
)
from app.models.sales import QuotationStatusEnum
from app.modules.sales.application.services.quotation_service import QuotationService
from app.modules.sales.domain.exceptions import (
    DocumentNotFoundError,
    InvalidStatusTransitionError,
    DocumentLockedException,
    DuplicateConversionError,
    ValidationError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sales/quotations", tags=["Quotations"])


@router.get("/", response_model=List[QuotationResponse])
async def get_quotations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[QuotationStatusEnum] = Query(None, description="Filter by quotation status"),
    search: Optional[str] = Query(None, description="Search by quotation number, customer name"),
    db: AsyncSession = Depends(get_db),
):
    """Get all quotations with filtering and search"""
    service = QuotationService(db)
    quotations = await service.get_quotations(
        skip=skip,
        limit=limit,
        status_filter=status,
        search=search,
    )
    for quotation in quotations:
        if quotation.customer:
            quotation.customer_name = quotation.customer.name
        # Set computed fields
        quotation.is_expired = service.check_expiration(quotation)
        quotation.can_edit = service.can_edit(quotation)
    return quotations


@router.get("/{quotation_id}", response_model=QuotationResponse)
async def get_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get quotation by ID"""
    service = QuotationService(db)
    quotation = await service.get_quotation(quotation_id)
    if not quotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
    if quotation.customer:
        quotation.customer_name = quotation.customer.name
    # Set computed fields
    quotation.is_expired = service.check_expiration(quotation)
    quotation.can_edit = service.can_edit(quotation)
    return quotation


@router.post("/", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation(
    data: QuotationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new quotation"""
    try:
        service = QuotationService(db)
        quotation = await service.create_quotation(
            customer_id=data.customer_id,
            date=data.date,
            expiration_date=data.expiration_date,
            invoicing_and_shipping_address=data.invoicing_and_shipping_address,
            quotation_items=[item.model_dump() for item in data.quotation_items],
            created_by_id=user_id,
            status=data.status,
        )
        if quotation.customer:
            quotation.customer_name = quotation.customer.name
        # Set computed fields
        quotation.is_expired = service.check_expiration(quotation)
        quotation.can_edit = service.can_edit(quotation)
        logger.info(f"Created Quotation {quotation.id} by user {user_id}")
        return quotation
    except ValidationError as e:
        logger.warning(f"Validation error creating quotation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating quotation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the quotation"
        )


@router.delete("/{quotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete quotation"""
    try:
        service = QuotationService(db)
        result = await service.delete_quotation(quotation_id)
        if not result:
            logger.warning(f"Quotation {quotation_id} not found for deletion")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")
        logger.info(f"Deleted Quotation {quotation_id} by user {user_id}")
    except HTTPException:
        raise
    except DocumentLockedException as e:
        logger.warning(f"Attempt to delete locked quotation {quotation_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting quotation {quotation_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the quotation"
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quotation_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete quotation item"""
    service = QuotationService(db)
    result = await service.delete_quotation_item(item_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation item not found")


@router.put("/{quotation_id}/status", response_model=QuotationResponse)
async def update_quotation_status(
    quotation_id: int,
    data: QuotationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update quotation status"""
    service = QuotationService(db)
    try:
        quotation = await service.update_quotation_status(
            quotation_id=quotation_id,
            new_status=data.status,
            user_id=user_id,
        )
        if quotation.customer:
            quotation.customer_name = quotation.customer.name
        # Set computed fields
        quotation.is_expired = service.check_expiration(quotation)
        quotation.can_edit = service.can_edit(quotation)
        logger.info(f"Updated Quotation {quotation_id} status to {data.status.value} by user {user_id}")
        return quotation
    except DocumentNotFoundError as e:
        logger.warning(f"Quotation {quotation_id} not found for status update")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStatusTransitionError as e:
        logger.warning(f"Invalid status transition for quotation {quotation_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating quotation {quotation_id} status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating quotation status"
        )


@router.post("/{quotation_id}/convert", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
async def convert_quotation_to_sales_order(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Convert Quotation to Sales Order"""
    service = QuotationService(db)
    try:
        sales_order = await service.convert_to_sales_order(
            quotation_id=quotation_id,
            user_id=user_id,
        )
        # Add customer name and date to response
        if sales_order.customer:
            sales_order.customer_name = sales_order.customer.name
        if sales_order.created_at:
            sales_order.created_at_date = sales_order.created_at.date()
        # Add product names to items
        for item in sales_order.order_items:
            if item.product:
                item.product_name = item.product.name
            item.sales_order_item_id = item.id
        logger.info(f"Converted Quotation {quotation_id} to Sales Order {sales_order.id} by user {user_id}")
        return sales_order
    except DocumentNotFoundError as e:
        logger.warning(f"Document not found during quotation conversion: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStatusTransitionError as e:
        logger.warning(f"Invalid status transition during quotation conversion: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DuplicateConversionError as e:
        logger.warning(f"Duplicate conversion attempt for quotation {quotation_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error during quotation conversion: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error converting quotation {quotation_id} to sales order: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while converting quotation to sales order"
        )


@router.post("/{quotation_id}/send-email", response_model=QuotationResponse)
async def send_quotation_email(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Send quotation email to customer"""
    service = QuotationService(db)
    try:
        quotation = await service.send_email(quotation_id=quotation_id, user_id=user_id)
        if quotation.customer:
            quotation.customer_name = quotation.customer.name
        # Set computed fields
        quotation.is_expired = service.check_expiration(quotation)
        quotation.can_edit = service.can_edit(quotation)
        logger.info(f"Sent email for Quotation {quotation_id} by user {user_id}")
        return quotation
    except DocumentNotFoundError as e:
        logger.warning(f"Quotation {quotation_id} not found for email sending")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error sending quotation email: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending quotation {quotation_id} email: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while sending quotation email"
        )

