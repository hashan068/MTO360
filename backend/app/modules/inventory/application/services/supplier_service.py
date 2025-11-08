"""
Supplier Service

Business logic for supplier management.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Supplier
from app.modules.inventory.domain.interfaces import SupplierRepository
from app.modules.inventory.infra.repositories.supplier_repo import SupplierRepository as SupplierRepositoryImpl


class SupplierService:
    """Service for supplier operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        supplier_repo: Optional[SupplierRepository] = None,
    ):
        self.db = db
        self.supplier_repo = supplier_repo or SupplierRepositoryImpl(db)
    
    async def get_supplier(self, supplier_id: int) -> Optional[Supplier]:
        """Get supplier by ID"""
        return await self.supplier_repo.get_by_id(supplier_id)
    
    async def get_suppliers(self, skip: int = 0, limit: int = 100) -> List[Supplier]:
        """Get all suppliers"""
        return await self.supplier_repo.get_all(skip=skip, limit=limit)
    
    async def create_supplier(
        self,
        name: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        website: Optional[str] = None,
        is_active: bool = True,
        notes: Optional[str] = None,
    ) -> Supplier:
        """Create a new supplier"""
        supplier = await self.supplier_repo.create(
            name=name,
            email=email,
            address=address,
            website=website,
            is_active=is_active,
            notes=notes,
        )
        await self.db.commit()
        return supplier
    
    async def update_supplier(self, supplier_id: int, **kwargs) -> Optional[Supplier]:
        """Update supplier"""
        supplier = await self.supplier_repo.update(supplier_id, **kwargs)
        if supplier:
            await self.db.commit()
        return supplier
    
    async def delete_supplier(self, supplier_id: int) -> bool:
        """Delete supplier"""
        result = await self.supplier_repo.delete(supplier_id)
        if result:
            await self.db.commit()
        return result

