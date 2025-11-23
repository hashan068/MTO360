"""
Operation Route Service

Business logic for operation route management.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.manufacturing import OperationRoute, RouteOperation
from app.modules.manufacturing.domain.interfaces import (
    OperationRouteRepository,
    RouteOperationRepository,
)
from app.modules.manufacturing.infra.repositories.operation_route_repo import (
    OperationRouteRepository as OperationRouteRepositoryImpl,
)
from app.modules.manufacturing.infra.repositories.route_operation_repo import (
    RouteOperationRepository as RouteOperationRepositoryImpl,
)


class OperationRouteService:
    """Service for operation route operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        operation_route_repo: Optional[OperationRouteRepository] = None,
        route_operation_repo: Optional[RouteOperationRepository] = None,
    ):
        self.db = db
        self.operation_route_repo = operation_route_repo or OperationRouteRepositoryImpl(db)
        self.route_operation_repo = route_operation_repo or RouteOperationRepositoryImpl(db)
    
    async def get_operation_route(self, route_id: int) -> Optional[OperationRoute]:
        """Get operation route by ID with operations"""
        return await self.operation_route_repo.get_by_id(route_id)
    
    async def get_operation_routes(
        self, skip: int = 0, limit: int = 100, active_only: bool = False
    ) -> List[OperationRoute]:
        """Get all operation routes"""
        return await self.operation_route_repo.get_all(skip=skip, limit=limit, active_only=active_only)
    
    async def get_route_by_product(self, product_id: int) -> Optional[OperationRoute]:
        """Get operation route for a product"""
        return await self.operation_route_repo.get_by_product_id(product_id)
    
    async def get_route_by_bom(self, bom_id: int) -> Optional[OperationRoute]:
        """Get operation route for a BOM"""
        return await self.operation_route_repo.get_by_bom_id(bom_id)
    
    async def create_operation_route(
        self,
        name: str,
        product_id: Optional[int] = None,
        bom_id: Optional[int] = None,
        is_active: bool = True,
        operations: Optional[List[dict]] = None,
    ) -> OperationRoute:
        """Create a new operation route with operations"""
        # Create the route
        route = await self.operation_route_repo.create(
            name=name,
            product_id=product_id,
            bom_id=bom_id,
            is_active=is_active,
        )
        
        # Add operations if provided
        if operations:
            for op_data in operations:
                await self.route_operation_repo.create(
                    route_id=route.id,
                    **op_data,
                )
        
        await self.db.commit()
        await self.db.refresh(route)
        return route
    
    async def update_operation_route(
        self, route_id: int, **updates
    ) -> Optional[OperationRoute]:
        """Update operation route"""
        route = await self.operation_route_repo.update(route_id, **updates)
        if route:
            await self.db.commit()
        return route
    
    async def delete_operation_route(self, route_id: int) -> bool:
        """Delete operation route and its operations"""
        success = await self.operation_route_repo.delete(route_id)
        if success:
            await self.db.commit()
        return success
    
    async def copy_operation_route(
        self, source_route_id: int, new_name: str, new_product_id: Optional[int] = None
    ) -> Optional[OperationRoute]:
        """Copy an existing operation route with all its operations"""
        # Get source route with operations
        source_route = await self.operation_route_repo.get_by_id(source_route_id)
        if not source_route:
            return None
        
        # Create new route
        new_route = await self.operation_route_repo.create(
            name=new_name,
            product_id=new_product_id or source_route.product_id,
            bom_id=source_route.bom_id,
            is_active=source_route.is_active,
        )
        
        # Copy operations
        for source_op in source_route.route_operations:
            await self.route_operation_repo.create(
                route_id=new_route.id,
                sequence=source_op.sequence,
                name=source_op.name,
                description=source_op.description,
                work_center_id=source_op.work_center_id,
                standard_time_minutes=source_op.standard_time_minutes,
                setup_time_minutes=source_op.setup_time_minutes,
            )
        
        await self.db.commit()
        await self.db.refresh(new_route)
        return new_route
    
    # Route Operation Management
    async def add_operation_to_route(
        self,
        route_id: int,
        sequence: int,
        name: str,
        work_center_id: int,
        standard_time_minutes: int,
        setup_time_minutes: int = 0,
        description: Optional[str] = None,
    ) -> RouteOperation:
        """Add an operation to a route"""
        operation = await self.route_operation_repo.create(
            route_id=route_id,
            sequence=sequence,
            name=name,
            work_center_id=work_center_id,
            standard_time_minutes=standard_time_minutes,
            setup_time_minutes=setup_time_minutes,
            description=description,
        )
        await self.db.commit()
        return operation
    
    async def update_route_operation(
        self, operation_id: int, **updates
    ) -> Optional[RouteOperation]:
        """Update a route operation"""
        operation = await self.route_operation_repo.update(operation_id, **updates)
        if operation:
            await self.db.commit()
        return operation
    
    async def delete_route_operation(self, operation_id: int) -> bool:
        """Delete a route operation"""
        success = await self.route_operation_repo.delete(operation_id)
        if success:
            await self.db.commit()
        return success
    
    async def reorder_route_operations(
        self, route_id: int, operation_sequence: List[dict]
    ) -> bool:
        """Reorder operations in a route
        
        Args:
            route_id: The route ID
            operation_sequence: List of {id: int, sequence: int} dictionaries
        """
        for item in operation_sequence:
            await self.route_operation_repo.update(
                item["id"], sequence=item["sequence"]
            )
        await self.db.commit()
        return True
