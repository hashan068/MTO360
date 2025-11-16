"""
Pydantic schemas for Sales module
"""
from pydantic import BaseModel, Field, field_validator
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
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    unit_price: Decimal = Field(gt=0, description="Unit price must be greater than 0")
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v
    
    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v):
        if v <= 0:
            raise ValueError('Unit price must be greater than 0')
        return v


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
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError('At least one item is required')
        return v


class RFQResponse(BaseModel):
    id: int
    creator_id: int
    creator_name: Optional[str] = None  # NEW: Creator name for display
    status: RFQStatusEnum
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[RFQItemResponse] = []
    
    class Config:
        from_attributes = True


# RFQ Summary Schema (for nested references)
class RFQSummary(BaseModel):
    id: int
    creator_id: int
    status: RFQStatusEnum
    due_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# RFQ Conversion Schema
class ConvertRFQToQuotationRequest(BaseModel):
    customer_id: int
    date: date
    expiration_date: date
    invoicing_and_shipping_address: str
    
    @field_validator('expiration_date')
    @classmethod
    def validate_expiration_date(cls, v, info):
        if 'date' in info.data and v <= info.data['date']:
            raise ValueError('Expiration date must be after quotation date')
        return v


# Quotation Schemas
class QuotationItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    unit_price: Decimal = Field(gt=0, description="Unit price must be greater than 0")
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v
    
    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v):
        if v <= 0:
            raise ValueError('Unit price must be greater than 0')
        return v


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
    
    @field_validator('quotation_items')
    @classmethod
    def validate_items(cls, v):
        if len(v) == 0:
            raise ValueError('At least one quotation item is required')
        return v
    
    @field_validator('expiration_date')
    @classmethod
    def validate_expiration_date(cls, v, info):
        if 'date' in info.data and v <= info.data['date']:
            raise ValueError('Expiration date must be after quotation date')
        return v


class QuotationResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    rfq_id: Optional[int] = None  # NEW: Reference to source RFQ
    date: date
    expiration_date: date
    invoicing_and_shipping_address: str
    total_amount: Decimal
    status: QuotationStatusEnum
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    email_sent_at: Optional[datetime] = None
    email_sent_count: int = 0
    email_history: Optional[List[dict]] = None
    quotation_items: List[QuotationItemResponse] = []
    
    class Config:
        from_attributes = True


# Quotation Summary Schema (for nested references)
class QuotationSummary(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    date: date
    total_amount: Decimal
    status: QuotationStatusEnum
    
    class Config:
        from_attributes = True


# Quotation Status Update Schema
class QuotationStatusUpdate(BaseModel):
    status: QuotationStatusEnum


# Sales Order Schemas
class SalesOrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    price: Decimal = Field(gt=0, description="Price must be greater than 0")
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v


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
    
    @field_validator('order_items')
    @classmethod
    def validate_items(cls, v):
        if len(v) == 0:
            raise ValueError('At least one order item is required')
        return v


class SalesOrderResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    quotation_id: Optional[int] = None  # NEW: Reference to source quotation
    total_amount: Decimal
    status: SalesOrderStatusEnum
    delivery_date: Optional[datetime] = None  # NEW: Actual delivery timestamp
    created_at: datetime
    created_at_date: Optional[date] = None
    updated_at: Optional[datetime] = None
    order_items: List[SalesOrderItemResponse] = []
    
    class Config:
        from_attributes = True


# Sales Order Summary Schema (for nested references)
class SalesOrderSummary(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    total_amount: Decimal
    status: SalesOrderStatusEnum
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sales Order Status Update Schema
class SalesOrderStatusUpdate(BaseModel):
    status: SalesOrderStatusEnum
    notes: Optional[str] = None



# Update forward references
RFQResponse.model_rebuild()
QuotationResponse.model_rebuild()
SalesOrderResponse.model_rebuild()
