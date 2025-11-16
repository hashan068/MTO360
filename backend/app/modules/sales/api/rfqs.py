"""
RFQ API endpoints
"""
from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.sales import (
    RFQCreate,
    RFQResponse,
    ConvertRFQToQuotationRequest,
    QuotationResponse,
    QuotationSummary,
)
from app.models.sales import RFQStatusEnum
from app.modules.sales.application.services.rfq_service import RFQService
from app.modules.sales.domain.exceptions import (
    DocumentNotFoundError,
    InvalidStatusTransitionError,
    ValidationError,
    DocumentLockedException,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sales/rfqs", tags=["RFQs"])


@router.get("/", response_model=List[RFQResponse])
async def get_rfqs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[RFQStatusEnum] = Query(None, description="Filter by RFQ status"),
    search: Optional[str] = Query(None, description="Search by RFQ number, description"),
    db: AsyncSession = Depends(get_db),
):
    """Get all RFQs with filtering and search"""
    service = RFQService(db)
    return await service.get_rfqs(
        skip=skip,
        limit=limit,
        status_filter=status,
        search=search,
    )


@router.get("/{rfq_id}", response_model=RFQResponse)
async def get_rfq(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get RFQ by ID"""
    service = RFQService(db)
    rfq = await service.get_rfq(rfq_id)
    if not rfq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ not found")
    return rfq


@router.post("/", response_model=RFQResponse, status_code=status.HTTP_201_CREATED)
async def create_rfq(
    data: RFQCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new RFQ"""
    try:
        service = RFQService(db)
        rfq = await service.create_rfq(
            creator_id=user_id,
            status=data.status,
            due_date=data.due_date,
            description=data.description,
            items=[item.model_dump() for item in data.items] if data.items else None,
        )
        logger.info(f"Created RFQ {rfq.id} by user {user_id}")
        return rfq
    except ValidationError as e:
        logger.warning(f"Validation error creating RFQ: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating RFQ: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the RFQ"
        )


@router.delete("/{rfq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rfq(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete RFQ"""
    try:
        service = RFQService(db)
        result = await service.delete_rfq(rfq_id)
        if not result:
            logger.warning(f"RFQ {rfq_id} not found for deletion")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ not found")
        logger.info(f"Deleted RFQ {rfq_id} by user {user_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting RFQ {rfq_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the RFQ"
        )


@router.post("/{rfq_id}/convert", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def convert_rfq_to_quotation(
    rfq_id: int,
    data: ConvertRFQToQuotationRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Convert RFQ to Quotation"""
    service = RFQService(db)
    try:
        quotation = await service.convert_to_quotation(
            rfq_id=rfq_id,
            customer_id=data.customer_id,
            user_id=user_id,
            quotation_date=data.date,
            expiration_date=data.expiration_date,
            invoicing_and_shipping_address=data.invoicing_and_shipping_address,
        )
        # Add customer name to response
        if quotation.customer:
            quotation.customer_name = quotation.customer.name
        logger.info(f"Converted RFQ {rfq_id} to Quotation {quotation.id} by user {user_id}")
        return quotation
    except DocumentNotFoundError as e:
        logger.warning(f"Document not found during RFQ conversion: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidStatusTransitionError as e:
        logger.warning(f"Invalid status transition during RFQ conversion: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error during RFQ conversion: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error converting RFQ {rfq_id} to quotation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while converting RFQ to quotation"
        )


@router.get("/{rfq_id}/quotations", response_model=List[QuotationSummary])
async def get_rfq_quotations(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all quotations created from this RFQ"""
    service = RFQService(db)
    try:
        quotations = await service.get_rfq_quotations(rfq_id)
        # Add customer names to summaries
        for quotation in quotations:
            if quotation.customer:
                quotation.customer_name = quotation.customer.name
        return quotations
    except DocumentNotFoundError as e:
        logger.warning(f"RFQ {rfq_id} not found when fetching quotations")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching quotations for RFQ {rfq_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching quotations"
        )

