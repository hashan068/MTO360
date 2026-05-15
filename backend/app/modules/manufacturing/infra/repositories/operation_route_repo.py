"""
Operation Route Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.manufacturing import OperationRoute, RouteOperation
from app.modules.manufacturing.domain.interfaces import OperationRouteRepository as OperationRouteRepositoryProtocol


class OperationRouteRepository:
    """Repository implementation for OperationRoute"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, route_id: int) -> Optional[OperationRoute]:
        """Get operation route by ID with operations"""
        result = await self.db.execute(
            select(OperationRoute)
            .options(selectinload(OperationRoute.route_operations).selectinload(RouteOperation.work_center))
            .where(OperationRoute.id == route_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[OperationRoute]:
        """Get all operation routes with pagination"""
        query = select(OperationRoute).options(
            selectinload(OperationRoute.product),
            selectinload(OperationRoute.route_operations).selectinload(RouteOperation.work_center),
        )
        
        if active_only:
            query = query.where(OperationRoute.is_active == True)
        
        query = query.offset(skip).limit(limit).order_by(OperationRoute.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_product_id(self, product_id: int) -> Optional[OperationRoute]:
        """Get operation route for a product"""
        result = await self.db.execute(
            select(OperationRoute)
            .options(selectinload(OperationRoute.route_operations).selectinload(RouteOperation.work_center))
            .where(OperationRoute.product_id == product_id)
            .where(OperationRoute.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def get_by_bom_id(self, bom_id: int) -> Optional[OperationRoute]:
        """Get operation route by BOM ID"""
        result = await self.db.execute(
            select(OperationRoute)
            .options(selectinload(OperationRoute.route_operations).selectinload(RouteOperation.work_center))
            .where(OperationRoute.bom_id == bom_id)
            .where(OperationRoute.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def create(self, *, name: str, product_id: Optional[int] = None,
                     bom_id: Optional[int] = None, is_active: bool = True) -> OperationRoute:
        """Create a new operation route"""
        route = OperationRoute(
            name=name,
            product_id=product_id,
            bom_id=bom_id,
            is_active=is_active,
        )
        self.db.add(route)
        await self.db.flush()
        await self.db.refresh(route)
        return route
    
    async def update(self, route_id: int, **kwargs) -> Optional[OperationRoute]:
        """Update operation route"""
        route = await self.get_by_id(route_id)
        if not route:
            return None
        
        for key, value in kwargs.items():
            if hasattr(route, key):
                setattr(route, key, value)
        
        await self.db.flush()
        await self.db.refresh(route)
        return route
    
    async def delete(self, route_id: int) -> bool:
        """Delete operation route"""
        route = await self.get_by_id(route_id)
        if not route:
            return False
        
        await self.db.delete(route)
        await self.db.flush()
        return True
