"""
BOM Service

Business logic for Bill of Material management.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.manufacturing import BillOfMaterial, BOMItem
from app.modules.manufacturing.domain.interfaces import (
    BillOfMaterialRepository,
    BOMItemRepository,
)
from app.modules.manufacturing.infra.repositories.bom_repo import (
    BillOfMaterialRepository as BillOfMaterialRepositoryImpl,
)
from app.modules.manufacturing.infra.repositories.bom_item_repo import (
    BOMItemRepository as BOMItemRepositoryImpl,
)


class BOMService:
    """Service for BOM operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        bom_repo: Optional[BillOfMaterialRepository] = None,
        bom_item_repo: Optional[BOMItemRepository] = None,
    ):
        self.db = db
        self.bom_repo = bom_repo or BillOfMaterialRepositoryImpl(db)
        self.bom_item_repo = bom_item_repo or BOMItemRepositoryImpl(db)
    
    async def get_bom(self, bom_id: int) -> Optional[BillOfMaterial]:
        """Get BOM by ID"""
        return await self.bom_repo.get_by_id(bom_id)
    
    async def get_boms(self, skip: int = 0, limit: int = 100) -> List[BillOfMaterial]:
        """Get all BOMs"""
        return await self.bom_repo.get_all(skip=skip, limit=limit)
    
    async def get_bom_by_product_id(self, product_id: int) -> Optional[BillOfMaterial]:
        """Get BOM by product ID"""
        return await self.bom_repo.get_by_product_id(product_id)
    
    async def create_bom(
        self,
        name: str,
        product_id: Optional[int] = None,
        bom_items: Optional[List[dict]] = None,
    ) -> BillOfMaterial:
        """Create a new BOM with items"""
        bom = await self.bom_repo.create(
            name=name,
            product_id=product_id,
        )
        
        # Create BOM items if provided
        if bom_items:
            for item_data in bom_items:
                await self.bom_item_repo.create(
                    bill_of_material_id=bom.id,
                    component_id=item_data.get('component_id'),
                    quantity=item_data['quantity'],
                )
        
        await self.db.commit()
        await self.db.refresh(bom)
        return bom
    
    async def update_bom(self, bom_id: int, **kwargs) -> Optional[BillOfMaterial]:
        """Update BOM"""
        bom = await self.bom_repo.update(bom_id, **kwargs)
        if bom:
            await self.db.commit()
        return bom
    
    async def delete_bom(self, bom_id: int) -> bool:
        """Delete BOM"""
        result = await self.bom_repo.delete(bom_id)
        if result:
            await self.db.commit()
        return result

