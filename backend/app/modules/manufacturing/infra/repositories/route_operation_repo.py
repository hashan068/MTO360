"""
Route Operation Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.models.manufacturing import RouteOperation
from app.modules.manufacturing.domain.interfaces import RouteOperationRepository as RouteOperationRepositoryProtocol


class RouteOperationRepository:
    """Repository implementation for RouteOperation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, operation_id: int) -> Optional[RouteOperation]:
        """Get route operation by ID"""
        result = await self.db.execute(
            select(RouteOperation)
            .options(selectinload(RouteOperation.work_center))
            .where(RouteOperation.id == operation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_route_id(self, route_id: int) -> List[RouteOperation]:
        """Get all operations for a route, ordered by sequence"""
        result = await self.db.execute(
            select(RouteOperation)
            .options(selectinload(RouteOperation.work_center))
            .where(RouteOperation.route_id == route_id)
            .order_by(RouteOperation.sequence)
        )
        return list(result.scalars().all())
    
    async def create(self, *, route_id: int, sequence: int, name: str,
                     work_center_id: int, standard_time_minutes: int,
                     setup_time_minutes: int = 0, description: Optional[str] = None) -> RouteOperation:
        """Create a new route operation"""
        operation = RouteOperation(
            route_id=route_id,
            sequence=sequence,
            name=name,
            work_center_id=work_center_id,
            standard_time_minutes=standard_time_minutes,
            setup_time_minutes=setup_time_minutes,
            description=description,
        )
        self.db.add(operation)
        await self.db.flush()
        await self.db.refresh(operation)
        return operation
    
    async def update(self, operation_id: int, **kwargs) -> Optional[RouteOperation]:
        """Update route operation"""
        operation = await self.get_by_id(operation_id)
        if not operation:
            return None
        
        for key, value in kwargs.items():
            if hasattr(operation, key):
                setattr(operation, key, value)
        
        await self.db.flush()
        await self.db.refresh(operation)
        return operation
    
    async def delete(self, operation_id: int) -> bool:
        """Delete route operation"""
        operation = await self.get_by_id(operation_id)
        if not operation:
            return False
        
        await self.db.delete(operation)
        await self.db.flush()
        return True
    
    async def delete_by_route_id(self, route_id: int) -> bool:
        """Delete all operations for a route"""
        await self.db.execute(
            delete(RouteOperation).where(RouteOperation.route_id == route_id)
        )
        await self.db.flush()
        return True
