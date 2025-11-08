"""
Pydantic schemas for Sales module
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

from app.models.sales import RFQStatusEnum, QuotationStatusEnum, SalesOrderStatusEnum, InverterTypeEnum


# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    email: str
    phone: str
    street_address: str
    city: str
    is_active: bool = True
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    description: str
    price: Decimal
    inverter_type: InverterTypeEnum
    power_rating: int
    frequency: Decimal
    efficiency: Decimal
    surge_power: int
    warranty_years: int
    input_voltage: Decimal
    output_voltage: Decimal


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    description: Optional[str] = None
    price: Optional[Decimal] = None
    inverter_type: Optional[InverterTypeEnum] = None
    power_rating: Optional[int] = None
    frequency: Optional[Decimal] = None
    efficiency: Optional[Decimal] = None
    surge_power: Optional[int] = None
    warranty_years: Optional[int] = None
    input_voltage: Optional[Decimal] = None
    output_voltage: Optional[Decimal] = None


class ProductResponse(ProductBase):
    id: int
    name: str
    model_number: str
    product_name: Optional[str] = None
    bom: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# RFQ Schemas
class RFQItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal


class RFQItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    
    class Config:
        from_attributes = True


class RFQCreate(BaseModel):
    status: RFQStatusEnum = RFQStatusEnum.DRAFT
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    items: Optional[List[RFQItemCreate]] = None


class RFQResponse(BaseModel):
    id: int
    creator_id: int
    status: RFQStatusEnum
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[RFQItemResponse] = []
    
    class Config:
        from_attributes = True


# Quotation Schemas
class QuotationItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal


class QuotationItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    
    class Config:
        from_attributes = True


class QuotationCreate(BaseModel):
    customer_id: int
    date: date
    expiration_date: date
    invoicing_and_shipping_address: str
    quotation_items: List[QuotationItemCreate]
    status: QuotationStatusEnum = QuotationStatusEnum.QUOTATION


class QuotationResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    date: date
    expiration_date: date
    invoicing_and_shipping_address: str
    total_amount: Decimal
    status: QuotationStatusEnum
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    quotation_items: List[QuotationItemResponse] = []
    
    class Config:
        from_attributes = True


# Sales Order Schemas
class SalesOrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: Decimal


class SalesOrderItemResponse(BaseModel):
    id: int
    sales_order_item_id: Optional[int] = None
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    price: Decimal
    
    class Config:
        from_attributes = True


class SalesOrderCreate(BaseModel):
    customer_id: int
    order_items: List[SalesOrderItemCreate]


class SalesOrderResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    total_amount: Decimal
    status: SalesOrderStatusEnum
    created_at: datetime
    created_at_date: Optional[date] = None
    updated_at: Optional[datetime] = None
    order_items: List[SalesOrderItemResponse] = []
    
    class Config:
        from_attributes = True

