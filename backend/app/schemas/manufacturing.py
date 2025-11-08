"""
Pydantic schemas for Manufacturing module
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from app.models.manufacturing import (
    ManufacturingOrderStatusEnum,
    MaterialRequisitionStatusEnum,
    MaterialRequisitionItemStatusEnum,
)


# BOM Schemas
class BOMItemCreate(BaseModel):
    component_id: Optional[int] = None
    quantity: int


class BOMItemResponse(BaseModel):
    id: int
    component_id: Optional[int] = None
    component_name: Optional[str] = None
    quantity: int
    
    class Config:
        from_attributes = True


class BillOfMaterialCreate(BaseModel):
    name: str
    product_id: Optional[int] = None
    bom_items: List[BOMItemCreate] = []


class BillOfMaterialResponse(BaseModel):
    id: int
    name: str
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    bom_items: List[BOMItemResponse] = []
    
    class Config:
        from_attributes = True


# Manufacturing Order Schemas
class ManufacturingOrderCreate(BaseModel):
    product_id: Optional[int] = None
    sales_order_item_id: Optional[int] = None
    quantity: int = 1


class ManufacturingOrderResponse(BaseModel):
    id: int
    sales_order_item_id: Optional[int] = None
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    quantity: int
    bom_id: Optional[int] = None
    status: ManufacturingOrderStatusEnum
    creator_id: Optional[int] = None
    created_at: datetime
    created_at_date: Optional[str] = None
    updated_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    production_start_at: Optional[datetime] = None
    estimated_mfg_lead_time: Optional[timedelta] = None
    mfg_lead_time: Optional[timedelta] = None
    production_lead_time: Optional[timedelta] = None
    
    class Config:
        from_attributes = True


# Material Requisition Schemas
class MaterialRequisitionItemResponse(BaseModel):
    id: int
    component_id: int
    component_name: Optional[str] = None
    quantity: int
    status: MaterialRequisitionItemStatusEnum
    
    class Config:
        from_attributes = True


class MaterialRequisitionCreate(BaseModel):
    manufacturing_order_id: int
    bom_id: Optional[int] = None


class MaterialRequisitionResponse(BaseModel):
    id: int
    manufacturing_order_id: int
    bom_id: Optional[int] = None
    status: MaterialRequisitionStatusEnum
    created_at: datetime
    created_at_date: Optional[str] = None
    updated_at: Optional[datetime] = None
    items: List[MaterialRequisitionItemResponse] = []
    
    class Config:
        from_attributes = True

