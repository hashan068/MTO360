"""
Pydantic schemas for Inventory module
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

from app.models.inventory import StatusEnum, PriorityEnum, PurchaseOrderStatusEnum


# Component Schemas
class ComponentBase(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = 0
    reorder_level: int = 0
    reorder_quantity: int = 0
    unit_of_measure: str = "pcs"
    supplier_id: Optional[int] = None
    cost: Decimal = Decimal("0.0")
    category_id: Optional[int] = None


class ComponentCreate(ComponentBase):
    pass


class ComponentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    reorder_level: Optional[int] = None
    reorder_quantity: Optional[int] = None
    unit_of_measure: Optional[str] = None
    supplier_id: Optional[int] = None
    cost: Optional[Decimal] = None
    category_id: Optional[int] = None


class ComponentResponse(ComponentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Supplier Schemas
class SupplierBase(BaseModel):
    name: str
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class SupplierResponse(SupplierBase):
    id: int
    date_added: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True


# Purchase Requisition Schemas
class PurchaseRequisitionBase(BaseModel):
    component_id: int
    quantity: int
    status: StatusEnum = StatusEnum.PENDING
    notes: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    priority: PriorityEnum = PriorityEnum.HIGH


class PurchaseRequisitionCreate(PurchaseRequisitionBase):
    pass


class PurchaseRequisitionResponse(PurchaseRequisitionBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    component_name: Optional[str] = None
    created_at_date: Optional[date] = None
    
    class Config:
        from_attributes = True


# Purchase Order Schemas
class PurchaseOrderBase(BaseModel):
    purchase_requisition_id: int
    supplier_id: Optional[int] = None
    status: PurchaseOrderStatusEnum = PurchaseOrderStatusEnum.DRAFT
    notes: Optional[str] = None
    price_per_unit: Optional[Decimal] = None
    total_price: Optional[Decimal] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    pass


class PurchaseOrderResponse(PurchaseOrderBase):
    id: int
    creator_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    purchase_requisition: Optional[dict] = None
    
    class Config:
        from_attributes = True


# Replenish Transaction Schemas
class ReplenishTransactionCreate(BaseModel):
    purchase_requisition_id: int
    component_id: int
    quantity: int


class ReplenishTransactionResponse(BaseModel):
    id: int
    purchase_requisition_id: int
    component_id: int
    component_name: Optional[str] = None
    quantity: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


# Consumption Transaction Schemas
class ConsumptionTransactionCreate(BaseModel):
    material_requisition_item_id: int
    component_id: int
    quantity: int


class ConsumptionTransactionResponse(BaseModel):
    id: int
    material_requisition_item_id: int
    component_id: int
    component_name: Optional[str] = None
    quantity: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

