"""
Bill of Material API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.manufacturing import BillOfMaterialCreate, BillOfMaterialResponse
from app.modules.manufacturing.application.services.bom_service import BOMService

router = APIRouter(prefix="/api/manufacturing/boms", tags=["Bill of Materials"])


@router.get("/", response_model=List[BillOfMaterialResponse])
async def get_boms(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all BOMs"""
    service = BOMService(db)
    boms = await service.get_boms(skip=skip, limit=limit)
    for bom in boms:
        if bom.product:
            bom.product_name = bom.product.name
        for item in bom.bom_items:
            if item.component:
                item.component_name = item.component.name
    return boms


@router.get("/{bom_id}", response_model=BillOfMaterialResponse)
async def get_bom(
    bom_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get BOM by ID"""
    service = BOMService(db)
    bom = await service.get_bom(bom_id)
    if not bom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="BOM not found")
    if bom.product:
        bom.product_name = bom.product.name
    for item in bom.bom_items:
        if item.component:
            item.component_name = item.component.name
    return bom


@router.post("/", response_model=BillOfMaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_bom(
    data: BillOfMaterialCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new BOM"""
    service = BOMService(db)
    bom = await service.create_bom(
        name=data.name,
        product_id=data.product_id,
        bom_items=[item.model_dump() for item in data.bom_items],
    )
    if bom.product:
        bom.product_name = bom.product.name
    for item in bom.bom_items:
        if item.component:
            item.component_name = item.component.name
    return bom

