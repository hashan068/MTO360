"""
Supplier Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.inventory import Supplier
from app.modules.inventory.domain.interfaces import SupplierRepository as SupplierRepositoryProtocol


class SupplierRepository:
    """Repository implementation for Supplier"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, supplier_id: int) -> Optional[Supplier]:
        """Get supplier by ID"""
        result = await self.db.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Get all suppliers with pagination"""
        result = await self.db.execute(
            select(Supplier)
            .offset(skip)
            .limit(limit)
            .order_by(Supplier.name)
        )
        return list(result.scalars().all())
    
    async def create(self, *, name: str, email: Optional[str] = None,
                     address: Optional[str] = None, website: Optional[str] = None,
                     is_active: bool = True, notes: Optional[str] = None) -> Supplier:
        """Create a new supplier"""
        supplier = Supplier(
            name=name,
            email=email,
            address=address,
            website=website,
            is_active=is_active,
            notes=notes,
        )
        self.db.add(supplier)
        await self.db.flush()
        await self.db.refresh(supplier)
        return supplier
    
    async def update(self, supplier_id: int, **kwargs) -> Optional[Supplier]:
        """Update supplier"""
        supplier = await self.get_by_id(supplier_id)
        if not supplier:
            return None
        
        for key, value in kwargs.items():
            if hasattr(supplier, key):
                setattr(supplier, key, value)
        
        await self.db.flush()
        await self.db.refresh(supplier)
        return supplier
    
    async def delete(self, supplier_id: int) -> bool:
        """Delete supplier"""
        supplier = await self.get_by_id(supplier_id)
        if not supplier:
            return False
        
        await self.db.delete(supplier)
        await self.db.flush()
        return True

