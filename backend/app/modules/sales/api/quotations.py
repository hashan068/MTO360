"""
Quotation API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.sales import QuotationCreate, QuotationResponse
from app.modules.sales.application.services.quotation_service import QuotationService

router = APIRouter(prefix="/api/sales/quotations", tags=["Quotations"])


@router.get("/", response_model=List[QuotationResponse])
async def get_quotations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all quotations"""
    service = QuotationService(db)
    quotations = await service.get_quotations(skip=skip, limit=limit)
    for quotation in quotations:
        if quotation.customer:
            quotation.customer_name = quotation.customer.name
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
    return quotation


@router.post("/", response_model=QuotationResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation(
    data: QuotationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new quotation"""
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
    return quotation


@router.delete("/{quotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quotation(
    quotation_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete quotation"""
    service = QuotationService(db)
    result = await service.delete_quotation(quotation_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")


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

