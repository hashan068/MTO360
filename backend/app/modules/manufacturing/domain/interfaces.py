"""
Manufacturing Domain Repository Interfaces

Protocol-based repository interfaces for manufacturing domain entities.
"""
from typing import Protocol, Optional, List
from datetime import datetime, timedelta

from app.models.manufacturing import (
    ManufacturingOrder,
    MaterialRequisition,
    MaterialRequisitionItem,
    BillOfMaterial,
    BOMItem,
)
from app.models.manufacturing import (
    ManufacturingOrderStatusEnum,
    MaterialRequisitionStatusEnum,
    MaterialRequisitionItemStatusEnum,
)


class ManufacturingOrderRepository(Protocol):
    """Repository interface for ManufacturingOrder"""
    
    async def get_by_id(self, order_id: int) -> Optional[ManufacturingOrder]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ManufacturingOrder]: ...
    
    async def create(self, *, sales_order_item_id: Optional[int] = None,
                     product_id: Optional[int] = None, quantity: int = 1,
                     bom_id: Optional[int] = None,
                     status: ManufacturingOrderStatusEnum = ManufacturingOrderStatusEnum.PENDING,
                     creator_id: Optional[int] = None) -> ManufacturingOrder: ...
    
    async def update(self, order_id: int, **kwargs) -> Optional[ManufacturingOrder]: ...
    
    async def delete(self, order_id: int) -> bool: ...


class MaterialRequisitionRepository(Protocol):
    """Repository interface for MaterialRequisition"""
    
    async def get_by_id(self, requisition_id: int) -> Optional[MaterialRequisition]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[MaterialRequisition]: ...
    
    async def create(self, *, manufacturing_order_id: int, bom_id: Optional[int] = None,
                     status: MaterialRequisitionStatusEnum = MaterialRequisitionStatusEnum.PENDING) -> MaterialRequisition: ...
    
    async def update(self, requisition_id: int, **kwargs) -> Optional[MaterialRequisition]: ...
    
    async def delete(self, requisition_id: int) -> bool: ...


class MaterialRequisitionItemRepository(Protocol):
    """Repository interface for MaterialRequisitionItem"""
    
    async def get_by_id(self, item_id: int) -> Optional[MaterialRequisitionItem]: ...
    
    async def get_by_requisition_id(self, requisition_id: int) -> List[MaterialRequisitionItem]: ...
    
    async def create(self, *, material_requisition_id: int, component_id: int,
                     quantity: int, status: MaterialRequisitionItemStatusEnum = MaterialRequisitionItemStatusEnum.PENDING) -> MaterialRequisitionItem: ...
    
    async def update(self, item_id: int, **kwargs) -> Optional[MaterialRequisitionItem]: ...
    
    async def delete(self, item_id: int) -> bool: ...


class BillOfMaterialRepository(Protocol):
    """Repository interface for BillOfMaterial"""
    
    async def get_by_id(self, bom_id: int) -> Optional[BillOfMaterial]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[BillOfMaterial]: ...
    
    async def get_by_product_id(self, product_id: int) -> Optional[BillOfMaterial]: ...
    
    async def create(self, *, name: str, product_id: Optional[int] = None) -> BillOfMaterial: ...
    
    async def update(self, bom_id: int, **kwargs) -> Optional[BillOfMaterial]: ...
    
    async def delete(self, bom_id: int) -> bool: ...


class BOMItemRepository(Protocol):
    """Repository interface for BOMItem"""
    
    async def get_by_id(self, item_id: int) -> Optional[BOMItem]: ...
    
    async def get_by_bom_id(self, bom_id: int) -> List[BOMItem]: ...
    
    async def create(self, *, bill_of_material_id: int, component_id: Optional[int] = None,
                     quantity: int) -> BOMItem: ...
    
    async def delete(self, item_id: int) -> bool: ...
