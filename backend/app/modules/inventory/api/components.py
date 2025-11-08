"""
Component API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.inventory import (
    ComponentCreate,
    ComponentUpdate,
    ComponentResponse,
)
from app.modules.inventory.application.services.component_service import ComponentService

router = APIRouter(prefix="/api/inventory/components", tags=["Components"])


@router.get("/", response_model=List[ComponentResponse])
async def get_components(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all components"""
    service = ComponentService(db)
    components = await service.get_components(skip=skip, limit=limit)
    return components


@router.get("/{component_id}", response_model=ComponentResponse)
async def get_component(
    component_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get component by ID"""
    service = ComponentService(db)
    component = await service.get_component(component_id)
    if not component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found"
        )
    return component


@router.post("/", response_model=ComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_component(
    data: ComponentCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new component"""
    service = ComponentService(db)
    component = await service.create_component(**data.model_dump())
    return component


@router.put("/{component_id}", response_model=ComponentResponse)
async def update_component(
    component_id: int,
    data: ComponentUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Update component"""
    service = ComponentService(db)
    component = await service.update_component(
        component_id,
        **data.model_dump(exclude_unset=True)
    )
    if not component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found"
        )
    return component


@router.delete("/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_component(
    component_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete component"""
    service = ComponentService(db)
    result = await service.delete_component(component_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component not found"
        )

