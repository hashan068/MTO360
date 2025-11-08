"""
Bill of Material Repository Implementation
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.manufacturing import BillOfMaterial
from app.modules.manufacturing.domain.interfaces import BillOfMaterialRepository as BillOfMaterialRepositoryProtocol


class BillOfMaterialRepository:
    """Repository implementation for BillOfMaterial"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, bom_id: int) -> Optional[BillOfMaterial]:
        """Get BOM by ID"""
        result = await self.db.execute(
            select(BillOfMaterial)
            .options(selectinload(BillOfMaterial.bom_items))
            .where(BillOfMaterial.id == bom_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[BillOfMaterial]:
        """Get all BOMs with pagination"""
        result = await self.db.execute(
            select(BillOfMaterial)
            .options(selectinload(BillOfMaterial.bom_items))
            .offset(skip)
            .limit(limit)
            .order_by(BillOfMaterial.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_product_id(self, product_id: int) -> Optional[BillOfMaterial]:
        """Get BOM by product ID"""
        result = await self.db.execute(
            select(BillOfMaterial)
            .options(selectinload(BillOfMaterial.bom_items))
            .where(BillOfMaterial.product_id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, *, name: str, product_id: Optional[int] = None) -> BillOfMaterial:
        """Create a new BOM"""
        bom = BillOfMaterial(
            name=name,
            product_id=product_id,
        )
        self.db.add(bom)
        await self.db.flush()
        await self.db.refresh(bom)
        return bom
    
    async def update(self, bom_id: int, **kwargs) -> Optional[BillOfMaterial]:
        """Update BOM"""
        bom = await self.get_by_id(bom_id)
        if not bom:
            return None
        
        for key, value in kwargs.items():
            if hasattr(bom, key):
                setattr(bom, key, value)
        
        await self.db.flush()
        await self.db.refresh(bom)
        return bom
    
    async def delete(self, bom_id: int) -> bool:
        """Delete BOM"""
        bom = await self.get_by_id(bom_id)
        if not bom:
            return False
        
        await self.db.delete(bom)
        await self.db.flush()
        return True

