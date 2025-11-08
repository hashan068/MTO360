"""
Category Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.inventory import Category
from app.modules.inventory.domain.interfaces import CategoryRepository as CategoryRepositoryProtocol


class CategoryRepository:
    """Repository implementation for Category"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Category]:
        """Get all categories"""
        result = await self.db.execute(
            select(Category).order_by(Category.name)
        )
        return list(result.scalars().all())
    
    async def create(self, *, name: str, description: Optional[str] = None) -> Category:
        """Create a new category"""
        category = Category(
            name=name,
            description=description,
        )
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category
    
    async def update(self, category_id: int, **kwargs) -> Optional[Category]:
        """Update category"""
        category = await self.get_by_id(category_id)
        if not category:
            return None
        
        for key, value in kwargs.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        await self.db.flush()
        await self.db.refresh(category)
        return category
    
    async def delete(self, category_id: int) -> bool:
        """Delete category"""
        category = await self.get_by_id(category_id)
        if not category:
            return False
        
        await self.db.delete(category)
        await self.db.flush()
        return True

