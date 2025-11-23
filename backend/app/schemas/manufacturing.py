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
    OperationStatusEnum,
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
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    total_scheduled_duration_minutes: Optional[int] = None
    
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


# ========== Production Scheduling Schemas ==========

# Work Center Schemas
class WorkCenterCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    capacity_hours_per_day: float
    is_active: bool = True
    location: Optional[str] = None
    notes: Optional[str] = None


class WorkCenterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    capacity_hours_per_day: Optional[float] = None
    is_active: Optional[bool] = None
    location: Optional[str] = None


class WorkCenterResponseNew(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    capacity_hours_per_day: float
    is_active: bool
    location: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Route Operation Schemas
class RouteOperationCreate(BaseModel):
    sequence: int
    name: str
    description: Optional[str] = None
    work_center_id: int
    standard_time_minutes: int
    setup_time_minutes: int = 0


class RouteOperationResponse(BaseModel):
    id: int
    sequence: int
    name: str
    work_center_id: int
    work_center_name: Optional[str] = None
    standard_time_minutes: int
    setup_time_minutes: int
    
    class Config:
        from_attributes = True


# Operation Route Schemas
class OperationRouteCreate(BaseModel):
    name: str
    product_id: Optional[int] = None
    bom_id: Optional[int] = None
    is_active: bool = True
    route_operations: List[RouteOperationCreate] = []


class OperationRouteResponse(BaseModel):
    id: int
    name: str
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    bom_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    route_operations: List[RouteOperationResponse] = []
    
    class Config:
        from_attributes = True


# Manufacturing Order Operation Schemas
class ManufacturingOrderOperationCreate(BaseModel):
    sequence: int
    name: str
    work_center_id: int
    scheduled_duration_minutes: int


class ManufacturingOrderOperationResponse(BaseModel):
    id: int
    manufacturing_order_id: int
    sequence: int
    name: str
    work_center_id: int
    work_center_name: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    scheduled_duration_minutes: int
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    actual_duration_minutes: Optional[int] = None
    status: OperationStatusEnum
    assigned_operator_id: Optional[int] = None
    notes: Optional[str] = None
    blocking_reason: Optional[str] = None
    
    class Config:
        from_attributes = True
