"""
Material Requisition API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.manufacturing import MaterialRequisitionCreate, MaterialRequisitionResponse
from app.modules.manufacturing.application.services.manufacturing_service import ManufacturingService

router = APIRouter(prefix="/api/manufacturing/material-requisitions", tags=["Material Requisitions"])


@router.get("/", response_model=List[MaterialRequisitionResponse])
async def get_material_requisitions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all material requisitions"""
    service = ManufacturingService(db)
    requisitions = await service.material_requisition_repo.get_all(skip=skip, limit=limit)
    for req in requisitions:
        if req.created_at:
            req.created_at_date = req.created_at.date().isoformat()
        for item in req.items:
            if item.component:
                item.component_name = item.component.name
    return requisitions


@router.get("/{requisition_id}", response_model=MaterialRequisitionResponse)
async def get_material_requisition(
    requisition_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get material requisition by ID"""
    from app.modules.manufacturing.infra.repositories.material_requisition_repo import MaterialRequisitionRepository
    service = ManufacturingService(db)
    requisition = await service.material_requisition_repo.get_by_id(requisition_id)
    if not requisition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material requisition not found")
    if requisition.created_at:
        requisition.created_at_date = requisition.created_at.date().isoformat()
    for item in requisition.items:
        if item.component:
            item.component_name = item.component.name
    return requisition


@router.post("/", response_model=MaterialRequisitionResponse, status_code=status.HTTP_201_CREATED)
async def create_material_requisition(
    data: MaterialRequisitionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new material requisition"""
    service = ManufacturingService(db)
    try:
        requisition = await service.create_material_requisition(
            manufacturing_order_id=data.manufacturing_order_id,
            bom_id=data.bom_id,
        )
        if requisition.created_at:
            requisition.created_at_date = requisition.created_at.date().isoformat()
        for item in requisition.items:
            if item.component:
                item.component_name = item.component.name
        return requisition
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

