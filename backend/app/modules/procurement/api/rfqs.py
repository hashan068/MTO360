"""
RFQ API endpoints
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.procurement import (
    ProcurementRFQCreate,
    ProcurementRFQResponse,
    ProcurementRFQUpdate,
    SupplierQuoteCreate,
    SupplierQuoteResponse,
    QuoteComparisonResponse,
    RFQAwardRequest,
    RFQAwardResponse,
)
from app.models.procurement import ProcurementRFQStatusEnum
from app.modules.procurement.application.services.rfq_service import RFQService


router = APIRouter(prefix="/api/v1/procurement/rfqs", tags=["RFQ & Competitive Bidding"])


@router.post("", response_model=ProcurementRFQResponse, status_code=status.HTTP_201_CREATED)
async def create_rfq(
    data: ProcurementRFQCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Create a new RFQ
    
    Sends RFQ to selected suppliers for competitive bidding.
    """
    service = RFQService(db)
    
    try:
        rfq = await service.create_rfq(
            component_id=data.component_id,
            quantity=data.quantity,
            required_by_date=data.required_by_date,
            closing_datetime=data.closing_datetime,
            specifications=data.specifications,
            internal_notes=data.internal_notes,
            created_by=current_user_id,
            supplier_ids=data.supplier_ids
        )
        return rfq
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating RFQ: {str(e)}"
        )


@router.get("", response_model=List[ProcurementRFQResponse])
async def list_rfqs(
    status_filter: Optional[ProcurementRFQStatusEnum] = Query(None, alias="status"),
    component_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    List RFQs with optional filters
    """
    service = RFQService(db)
    rfqs = await service.list_rfqs(status_filter, component_id, limit, offset)
    return rfqs


@router.get("/{rfq_id}", response_model=ProcurementRFQResponse)
async def get_rfq(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get RFQ details including quotes
    """
    service = RFQService(db)
    rfq = await service.get_rfq(rfq_id)
    
    if not rfq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RFQ {rfq_id} not found"
        )
    
    return rfq


@router.post("/{rfq_id}/send", response_model=ProcurementRFQResponse)
async def send_rfq(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Send RFQ to selected suppliers
    
    Changes status to SENT and triggers email notifications.
    """
    service = RFQService(db)
    
    try:
        rfq = await service.send_rfq(rfq_id)
        return rfq
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending RFQ: {str(e)}"
        )


@router.post("/{rfq_id}/quotes", response_model=SupplierQuoteResponse, status_code=status.HTTP_201_CREATED)
async def submit_quote(
    rfq_id: int,
    data: SupplierQuoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Submit a quote for an RFQ
    
    Suppliers use this endpoint to submit their quotes.
    """
    service = RFQService(db)
    
    try:
        quote = await service.submit_quote(
            rfq_id=rfq_id,
            supplier_id=data.supplier_id,
            unit_price=data.unit_price,
            lead_time_days=data.lead_time_days,
            minimum_order_quantity=data.minimum_order_quantity,
            quote_valid_until=data.quote_valid_until,
            notes=data.notes
        )
        return quote
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting quote: {str(e)}"
        )


@router.get("/{rfq_id}/quotes/compare", response_model=QuoteComparisonResponse)
async def compare_quotes(
    rfq_id: int,
    sort_by: str = Query("price", regex="^(price|lead_time|score)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Compare all quotes for an RFQ
    
    Returns side-by-side comparison with recommendations.
    Sort by: price, lead_time, or score (supplier performance score).
    """
    service = RFQService(db)
    
    try:
        comparison = await service.compare_quotes(rfq_id, sort_by)
        return comparison
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing quotes: {str(e)}"
        )


@router.post("/{rfq_id}/award", response_model=RFQAwardResponse)
async def award_rfq(
    rfq_id: int,
    data: RFQAwardRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Award RFQ to winning supplier
    
    Creates a Purchase Order and notifies suppliers.
    Requires procurement_manager role.
    """
    service = RFQService(db)
    
    try:
        result = await service.award_rfq(
            rfq_id=rfq_id,
            quote_id=data.quote_id,
            justification=data.justification
        )
        
        return {
            'rfq': result['rfq'],
            'awarded_quote': result['awarded_quote'],
            'purchase_order_id': result['purchase_order'].id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error awarding RFQ: {str(e)}"
        )


@router.delete("/{rfq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_rfq(
    rfq_id: int,
    reason: str = Query(..., min_length=10),
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Cancel an RFQ
    
    Requires reason for audit trail.
    """
    service = RFQService(db)
    
    try:
        await service.cancel_rfq(rfq_id, reason, current_user_id)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling RFQ: {str(e)}"
        )
