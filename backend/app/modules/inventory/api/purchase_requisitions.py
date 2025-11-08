"""
Purchase Requisition API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.inventory import (
    PurchaseRequisitionCreate,
    PurchaseRequisitionResponse,
)
from app.modules.inventory.application.services.purchase_service import PurchaseService

router = APIRouter(prefix="/api/inventory/purchase-requisitions", tags=["Purchase Requisitions"])


@router.get("/", response_model=List[PurchaseRequisitionResponse])
async def get_purchase_requisitions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all purchase requisitions"""
    service = PurchaseService(db)
    requisitions = await service.get_purchase_requisitions(skip=skip, limit=limit)
    return requisitions


@router.get("/{requisition_id}", response_model=PurchaseRequisitionResponse)
async def get_purchase_requisition(
    requisition_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get purchase requisition by ID"""
    service = PurchaseService(db)
    requisition = await service.get_purchase_requisition(requisition_id)
    if not requisition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase requisition not found"
        )
    # Add component name and date for response
    response_data = PurchaseRequisitionResponse.model_validate(requisition)
    if requisition.component:
        response_data.component_name = requisition.component.name
    if requisition.created_at:
        response_data.created_at_date = requisition.created_at.date()
    return response_data


@router.post("/", response_model=PurchaseRequisitionResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_requisition(
    data: PurchaseRequisitionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new purchase requisition"""
    service = PurchaseService(db)
    requisition = await service.create_purchase_requisition(
        user_id=user_id,
        **data.model_dump()
    )
    response_data = PurchaseRequisitionResponse.model_validate(requisition)
    if requisition.component:
        response_data.component_name = requisition.component.name
    if requisition.created_at:
        response_data.created_at_date = requisition.created_at.date()
    return response_data

