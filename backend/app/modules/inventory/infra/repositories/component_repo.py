"""
Component Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.inventory import Component
from app.modules.inventory.domain.interfaces import ComponentRepository as ComponentRepositoryProtocol


class ComponentRepository:
    """Repository implementation for Component"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, component_id: int) -> Optional[Component]:
        """Get component by ID"""
        result = await self.db.execute(
            select(Component)
            .options(selectinload(Component.category), selectinload(Component.supplier))
            .where(Component.id == component_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Component]:
        """Get all components with pagination"""
        result = await self.db.execute(
            select(Component)
            .options(selectinload(Component.category), selectinload(Component.supplier))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, *, name: str, description: Optional[str] = None, quantity: int = 0,
                     category_id: Optional[int] = None, reorder_level: int = 0,
                     reorder_quantity: int = 0, unit_of_measure: str = "pcs",
                     supplier_id: Optional[int] = None, cost: float = 0.0) -> Component:
        """Create a new component"""
        component = Component(
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
        self.db.add(component)
        await self.db.flush()
        await self.db.refresh(component)
        return component
    
    async def update(self, component_id: int, **kwargs) -> Optional[Component]:
        """Update component"""
        component = await self.get_by_id(component_id)
        if not component:
            return None
        
        for key, value in kwargs.items():
            if hasattr(component, key):
                setattr(component, key, value)
        
        await self.db.flush()
        await self.db.refresh(component)
        return component
    
    async def delete(self, component_id: int) -> bool:
        """Delete component"""
        component = await self.get_by_id(component_id)
        if not component:
            return False
        
        await self.db.delete(component)
        await self.db.flush()
        return True
    
    async def update_quantity(self, component_id: int, quantity_delta: int) -> Optional[Component]:
        """Update component quantity by delta"""
        component = await self.get_by_id(component_id)
        if not component:
            return None
        
        component.quantity += quantity_delta
        await self.db.flush()
        await self.db.refresh(component)
        return component

