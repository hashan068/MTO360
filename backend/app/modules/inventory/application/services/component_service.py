"""
Component Service

Business logic for component management.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Component
from app.modules.inventory.domain.interfaces import ComponentRepository
from app.modules.inventory.infra.repositories.component_repo import ComponentRepository as ComponentRepositoryImpl


class ComponentService:
    """Service for component operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        component_repo: Optional[ComponentRepository] = None,
    ):
        self.db = db
        self.component_repo = component_repo or ComponentRepositoryImpl(db)
    
    async def get_component(self, component_id: int) -> Optional[Component]:
        """Get component by ID"""
        return await self.component_repo.get_by_id(component_id)
    
    async def get_components(self, skip: int = 0, limit: int = 100) -> List[Component]:
        """Get all components"""
        return await self.component_repo.get_all(skip=skip, limit=limit)
    
    async def create_component(
        self,
        name: str,
        description: Optional[str] = None,
        quantity: int = 0,
        category_id: Optional[int] = None,
        reorder_level: int = 0,
        reorder_quantity: int = 0,
        unit_of_measure: str = "pcs",
        supplier_id: Optional[int] = None,
        cost: float = 0.0,
    ) -> Component:
        """Create a new component"""
        component = await self.component_repo.create(
            name=name,
            description=description,
            quantity=quantity,
            category_id=category_id,
            reorder_level=reorder_level,
            reorder_quantity=reorder_quantity,
            unit_of_measure=unit_of_measure,
            supplier_id=supplier_id,
            cost=cost,
        )
        await self.db.commit()
        return component
    
    async def update_component(self, component_id: int, **kwargs) -> Optional[Component]:
        """Update component"""
        component = await self.component_repo.update(component_id, **kwargs)
        if component:
            await self.db.commit()
        return component
    
    async def delete_component(self, component_id: int) -> bool:
        """Delete component"""
        result = await self.component_repo.delete(component_id)
        if result:
            await self.db.commit()
        return result
    
    async def update_component_quantity(self, component_id: int, quantity_delta: int) -> Optional[Component]:
        """Update component quantity"""
        component = await self.component_repo.update_quantity(component_id, quantity_delta)
        if component:
            await self.db.commit()
        return component

