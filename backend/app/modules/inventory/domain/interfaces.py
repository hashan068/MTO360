"""
Inventory Domain Repository Interfaces

Protocol-based repository interfaces for inventory domain entities.
Enables dependency inversion and supports multiple backend implementations.
"""
from typing import Protocol, Optional, List
from uuid import UUID
from datetime import datetime

from app.models.inventory import (
    Component,
    Supplier,
    Category,
    PurchaseRequisition,
    PurchaseOrder,
    ReplenishTransaction,
    ConsumptionTransaction,
)
from app.models.inventory import StatusEnum, PriorityEnum, PurchaseOrderStatusEnum


class ComponentRepository(Protocol):
    """Repository interface for Component"""
    
    async def get_by_id(self, component_id: int) -> Optional[Component]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Component]: ...
    
    async def create(self, *, name: str, description: Optional[str] = None, quantity: int = 0, 
                     category_id: Optional[int] = None, reorder_level: int = 0,
                     reorder_quantity: int = 0, unit_of_measure: str = "pcs",
                     supplier_id: Optional[int] = None, cost: float = 0.0) -> Component: ...
    
    async def update(self, component_id: int, **kwargs) -> Optional[Component]: ...
    
    async def delete(self, component_id: int) -> bool: ...
    
    async def update_quantity(self, component_id: int, quantity_delta: int) -> Optional[Component]: ...


class SupplierRepository(Protocol):
    """Repository interface for Supplier"""
    
    async def get_by_id(self, supplier_id: int) -> Optional[Supplier]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Supplier]: ...
    
    async def create(self, *, name: str, email: Optional[str] = None,
                     address: Optional[str] = None, website: Optional[str] = None,
                     is_active: bool = True, notes: Optional[str] = None) -> Supplier: ...
    
    async def update(self, supplier_id: int, **kwargs) -> Optional[Supplier]: ...
    
    async def delete(self, supplier_id: int) -> bool: ...


class CategoryRepository(Protocol):
    """Repository interface for Category"""
    
    async def get_by_id(self, category_id: int) -> Optional[Category]: ...
    
    async def get_all(self) -> List[Category]: ...
    
    async def create(self, *, name: str, description: Optional[str] = None) -> Category: ...
    
    async def update(self, category_id: int, **kwargs) -> Optional[Category]: ...
    
    async def delete(self, category_id: int) -> bool: ...


class PurchaseRequisitionRepository(Protocol):
    """Repository interface for PurchaseRequisition"""
    
    async def get_by_id(self, requisition_id: int) -> Optional[PurchaseRequisition]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[PurchaseRequisition]: ...
    
    async def create(self, *, user_id: Optional[int], component_id: int, quantity: int,
                     status: StatusEnum = StatusEnum.PENDING, notes: Optional[str] = None,
                     expected_delivery_date: Optional[datetime] = None,
                     priority: PriorityEnum = PriorityEnum.HIGH) -> PurchaseRequisition: ...
    
    async def update(self, requisition_id: int, **kwargs) -> Optional[PurchaseRequisition]: ...
    
    async def delete(self, requisition_id: int) -> bool: ...


class PurchaseOrderRepository(Protocol):
    """Repository interface for PurchaseOrder"""
    
    async def get_by_id(self, order_id: int) -> Optional[PurchaseOrder]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]: ...
    
    async def create(self, *, creator_id: Optional[int], purchase_requisition_id: int,
                     supplier_id: Optional[int] = None, status: PurchaseOrderStatusEnum = PurchaseOrderStatusEnum.DRAFT,
                     notes: Optional[str] = None, price_per_unit: Optional[float] = None,
                     total_price: Optional[float] = None) -> PurchaseOrder: ...
    
    async def update(self, order_id: int, **kwargs) -> Optional[PurchaseOrder]: ...
    
    async def delete(self, order_id: int) -> bool: ...


class ReplenishTransactionRepository(Protocol):
    """Repository interface for ReplenishTransaction"""
    
    async def get_by_id(self, transaction_id: int) -> Optional[ReplenishTransaction]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ReplenishTransaction]: ...
    
    async def create(self, *, purchase_requisition_id: int, component_id: int,
                     quantity: int, user_id: Optional[int] = None) -> ReplenishTransaction: ...


class ConsumptionTransactionRepository(Protocol):
    """Repository interface for ConsumptionTransaction"""
    
    async def get_by_id(self, transaction_id: int) -> Optional[ConsumptionTransaction]: ...
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ConsumptionTransaction]: ...
    
    async def create(self, *, material_requisition_item_id: int, component_id: int,
                     quantity: int, user_id: Optional[int] = None) -> ConsumptionTransaction: ...

