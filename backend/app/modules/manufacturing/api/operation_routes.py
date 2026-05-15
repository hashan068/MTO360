"""
Operation Routes API Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user_id
from app.schemas.manufacturing import (
    OperationRouteCreate,
    OperationRouteResponse,
    RouteOperationCreate,
    RouteOperationResponse,
)
from app.modules.manufacturing.application.services.operation_route_service import OperationRouteService

router = APIRouter(prefix="/api/manufacturing/operation-routes", tags=["Operation Routes"])


@router.get("/", response_model=List[OperationRouteResponse])
async def list_operation_routes(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """Get all operation routes"""
    service = OperationRouteService(db)
    routes = await service.get_operation_routes(skip=skip, limit=limit, active_only=active_only)
    return routes


@router.get("/{route_id}", response_model=OperationRouteResponse)
async def get_operation_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get operation route by ID"""
    service = OperationRouteService(db)
    route = await service.get_operation_route(route_id)
    if not route:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Operation route {route_id} not found"
        )
    return route


@router.get("/by-product/{product_id}", response_model=OperationRouteResponse)
async def get_route_by_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get operation route for a product"""
    service = OperationRouteService(db)
    route = await service.get_route_by_product(product_id)
    if not route:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"No operation route found for product {product_id}"
        )
    return route


@router.post("/", response_model=OperationRouteResponse, status_code=http_status.HTTP_201_CREATED)
async def create_operation_route(
    data: OperationRouteCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Create a new operation route with operations"""
    service = OperationRouteService(db)
    
    # Extract operations data
    operations = [op.model_dump() for op in data.route_operations] if data.route_operations else None
    
    route = await service.create_operation_route(
        name=data.name,
        product_id=data.product_id,
        bom_id=data.bom_id,
        is_active=data.is_active,
        operations=operations,
    )
    return route


@router.post("/{route_id}/copy", response_model=OperationRouteResponse, status_code=http_status.HTTP_201_CREATED)
async def copy_operation_route(
    route_id: int,
    new_name: str,
    new_product_id: int = None,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Copy an existing operation route"""
    service = OperationRouteService(db)
    route = await service.copy_operation_route(route_id, new_name, new_product_id)
    if not route:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Operation route {route_id} not found"
        )
    return route


@router.delete("/{route_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_operation_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete operation route"""
    service = OperationRouteService(db)
    success = await service.delete_operation_route(route_id)
    if not success:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Operation route {route_id} not found"
        )


# Route Operations Management
@router.post("/{route_id}/operations", response_model=RouteOperationResponse, status_code=http_status.HTTP_201_CREATED)
async def add_operation_to_route(
    route_id: int,
    data: RouteOperationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Add an operation to a route"""
    service = OperationRouteService(db)
    operation = await service.add_operation_to_route(
        route_id=route_id,
        sequence=data.sequence,
        name=data.name,
        work_center_id=data.work_center_id,
        standard_time_minutes=data.standard_time_minutes,
        setup_time_minutes=data.setup_time_minutes,
        description=data.description,
    )
    return operation


@router.delete("/{route_id}/operations/{operation_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_route_operation(
    route_id: int,
    operation_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete a route operation"""
    service = OperationRouteService(db)
    success = await service.delete_route_operation(operation_id)
    if not success:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Route operation {operation_id} not found"
        )


@router.put("/{route_id}/operations/reorder", status_code=http_status.HTTP_204_NO_CONTENT)
async def reorder_route_operations(
    route_id: int,
    operation_sequence: List[dict],
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Reorder operations in a route
    
    Body: [{"id": 1, "sequence": 1}, {"id": 2, "sequence": 2}, ...]
    """
    service = OperationRouteService(db)
    await service.reorder_route_operations(route_id, operation_sequence)
