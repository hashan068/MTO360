"""
Manufacturing Service

Business logic for manufacturing operations.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.manufacturing import (
    ManufacturingOrder,
    MaterialRequisition,
    ManufacturingOrderStatusEnum,
    MaterialRequisitionStatusEnum,
)
from app.modules.manufacturing.domain.interfaces import (
    ManufacturingOrderRepository,
    MaterialRequisitionRepository,
    MaterialRequisitionItemRepository,
    BillOfMaterialRepository,
)
from app.modules.manufacturing.infra.repositories.manufacturing_order_repo import (
    ManufacturingOrderRepository as ManufacturingOrderRepositoryImpl,
)
from app.modules.manufacturing.infra.repositories.material_requisition_repo import (
    MaterialRequisitionRepository as MaterialRequisitionRepositoryImpl,
)
from app.modules.manufacturing.infra.repositories.material_requisition_item_repo import (
    MaterialRequisitionItemRepository as MaterialRequisitionItemRepositoryImpl,
)
from app.modules.manufacturing.infra.repositories.bom_repo import (
    BillOfMaterialRepository as BillOfMaterialRepositoryImpl,
)


class ManufacturingService:
    """Service for manufacturing operations"""
    
    def __init__(
        self,
        db: AsyncSession,
        manufacturing_order_repo: Optional[ManufacturingOrderRepository] = None,
        material_requisition_repo: Optional[MaterialRequisitionRepository] = None,
        material_requisition_item_repo: Optional[MaterialRequisitionItemRepository] = None,
        bom_repo: Optional[BillOfMaterialRepository] = None,
    ):
        self.db = db
        self.manufacturing_order_repo = manufacturing_order_repo or ManufacturingOrderRepositoryImpl(db)
        self.material_requisition_repo = material_requisition_repo or MaterialRequisitionRepositoryImpl(db)
        self.material_requisition_item_repo = material_requisition_item_repo or MaterialRequisitionItemRepositoryImpl(db)
        self.bom_repo = bom_repo or BillOfMaterialRepositoryImpl(db)
    
    async def get_manufacturing_order(self, order_id: int) -> Optional[ManufacturingOrder]:
        """Get manufacturing order by ID"""
        return await self.manufacturing_order_repo.get_by_id(order_id)
    
    async def get_manufacturing_orders(self, skip: int = 0, limit: int = 100) -> List[ManufacturingOrder]:
        """Get all manufacturing orders"""
        return await self.manufacturing_order_repo.get_all(skip=skip, limit=limit)
    
    async def create_manufacturing_order(
        self,
        product_id: Optional[int] = None,
        sales_order_item_id: Optional[int] = None,
        quantity: int = 1,
        creator_id: Optional[int] = None,
    ) -> ManufacturingOrder:
        """Create a new manufacturing order"""
        # Get BOM for product if product_id provided
        bom_id = None
        if product_id:
            bom = await self.bom_repo.get_by_product_id(product_id)
            if bom:
                bom_id = bom.id
        
        order = await self.manufacturing_order_repo.create(
            sales_order_item_id=sales_order_item_id,
            product_id=product_id,
            quantity=quantity,
            bom_id=bom_id,
            status=ManufacturingOrderStatusEnum.PENDING,
            creator_id=creator_id,
        )
        await self.db.commit()
        return order
    
    async def create_material_requisition(
        self,
        manufacturing_order_id: int,
        bom_id: Optional[int] = None,
    ) -> MaterialRequisition:
        """Create a material requisition from manufacturing order and BOM"""
        # Get manufacturing order
        order = await self.manufacturing_order_repo.get_by_id(manufacturing_order_id)
        if not order:
            raise ValueError(f"Manufacturing order {manufacturing_order_id} not found")
        
        # Use BOM from order if not provided
        if not bom_id:
            bom_id = order.bom_id
        
        if not bom_id:
            raise ValueError("No BOM available for material requisition")
        
        # Get BOM with items
        bom = await self.bom_repo.get_by_id(bom_id)
        if not bom:
            raise ValueError(f"BOM {bom_id} not found")
        
        # Create material requisition
        requisition = await self.material_requisition_repo.create(
            manufacturing_order_id=manufacturing_order_id,
            bom_id=bom_id,
            status=MaterialRequisitionStatusEnum.PENDING,
        )
        
        # Create material requisition items from BOM
        for bom_item in bom.bom_items:
            quantity = order.quantity * bom_item.quantity
            await self.material_requisition_item_repo.create(
                material_requisition_id=requisition.id,
                component_id=bom_item.component_id,
                quantity=quantity,
            )
        
        # Update manufacturing order status
        await self.manufacturing_order_repo.update(
            manufacturing_order_id,
            status=ManufacturingOrderStatusEnum.MR_SENT,
        )
        
        await self.db.commit()
        await self.db.refresh(requisition)
        return requisition
    
    async def update_manufacturing_order_status(
        self,
        order_id: int,
        new_status: ManufacturingOrderStatusEnum,
    ) -> Optional[ManufacturingOrder]:
        """Update manufacturing order status"""
        order = await self.manufacturing_order_repo.get_by_id(order_id)
        if not order:
            return None
        
        updates = {"status": new_status}
        
        if new_status == ManufacturingOrderStatusEnum.IN_PRODUCTION:
            updates["production_start_at"] = datetime.utcnow()
        elif new_status == ManufacturingOrderStatusEnum.COMPLETED:
            now = datetime.utcnow()
            updates["end_at"] = now
            if order.created_at:
                updates["mfg_lead_time"] = now - order.created_at
            if order.production_start_at:
                updates["production_lead_time"] = now - order.production_start_at
        
        order = await self.manufacturing_order_repo.update(order_id, **updates)
        if order:
            await self.db.commit()
        return order

