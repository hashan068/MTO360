"""
RFQ API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.sales import RFQCreate, RFQResponse
from app.modules.sales.application.services.rfq_service import RFQService

router = APIRouter(prefix="/api/sales/rfqs", tags=["RFQs"])


@router.get("/", response_model=List[RFQResponse])
async def get_rfqs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all RFQs"""
    service = RFQService(db)
    return await service.get_rfqs(skip=skip, limit=limit)


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
    service = RFQService(db)
    rfq = await service.create_rfq(
        creator_id=user_id,
        status=data.status,
        due_date=data.due_date,
        description=data.description,
        items=[item.model_dump() for item in data.items] if data.items else None,
    )
    return rfq


@router.delete("/{rfq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rfq(
    rfq_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete RFQ"""
    service = RFQService(db)
    result = await service.delete_rfq(rfq_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ not found")

