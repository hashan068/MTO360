"""
Material Requisition API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.manufacturing import MaterialRequisitionCreate, MaterialRequisitionResponse
from app.modules.manufacturing.application.services.manufacturing_service import ManufacturingService
from app.modules.manufacturing.application.services.scheduling_service import SchedulingService

router = APIRouter(prefix="/api/manufacturing/material-requisitions", tags=["Material Requisitions"])

logger = logging.getLogger(__name__)


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


@router.post("/{requisition_id}/approve", response_model=MaterialRequisitionResponse)
async def approve_material_requisition(
    requisition_id: int,
    auto_schedule: bool = Query(
        True,
        description="Automatically schedule the manufacturing order after approval"
    ),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Approve a material requisition.
    
    Optionally triggers auto-scheduling for the associated manufacturing order.
    If auto_schedule is True and the MO has operations, they will be automatically
    scheduled based on work center capacity.
    """
    from app.modules.manufacturing.infra.repositories.material_requisition_repo import MaterialRequisitionRepository
    
    mr_repo = MaterialRequisitionRepository(db)
    
    # Get MR
    requisition = await mr_repo.get_by_id(requisition_id)
    if not requisition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material requisition not found"
        )
    
    # Update status to approved (simplified - would normally check current status)
    # This would call a service method in production
    requisition.status = "approved"
    await db.commit()
    await db.refresh(requisition)
    
    # Trigger auto-scheduling if enabled
    if auto_schedule and requisition.manufacturing_order_id:
        try:
            scheduling_service = SchedulingService(db)
            mo = await scheduling_service.auto_schedule_mo(requisition.manufacturing_order_id)
            logger.info(
                f"Auto-scheduled MO {mo.id} after MR {requisition_id} approval"
            )
        except ValueError as e:
            # Operations might not exist or other scheduling error
            logger.warning(
                f"Could not auto-schedule MO after MR {requisition_id} approval: {e}"
            )
    
    # Enrich response
    if requisition.created_at:
        requisition.created_at_date = requisition.created_at.date().isoformat()
    for item in requisition.items:
        if item.component:
            item.component_name = item.component.name
    
    return requisition

