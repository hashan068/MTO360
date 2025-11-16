"""
Sales module database models
"""
from sqlalchemy import (
    String,
    Integer,
    Text,
    ForeignKey,
    Numeric,
    Boolean,
    DateTime,
    Date,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime, date
import enum

from app.models.base import Base, TimestampMixin


class RFQStatusEnum(str, enum.Enum):
    """RFQ status"""
    DRAFT = "draft"
    SENT = "sent"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class QuotationStatusEnum(str, enum.Enum):
    """Quotation status"""
    QUOTATION = "quotation"
    QUOTATION_SENT = "quotation_sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SalesOrderStatusEnum(str, enum.Enum):
    """Sales order status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    IN_PRODUCTION = "in_Production"
    READY_FOR_DELIVERY = "Ready_for_delivery"
    CANCELLED = "cancelled"
    DELIVERED = "delivered"


class InverterTypeEnum(str, enum.Enum):
    """Inverter type"""
    PURE_SINE_WAVE = "Pure Sine Wave"
    MODIFIED_SINE_WAVE = "Modified Sine Wave"
    SQUARE_WAVE = "Square Wave"


class Customer(Base, TimestampMixin):
    """Customer model"""
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    street_address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    quotations: Mapped[list["Quotation"]] = relationship("Quotation", back_populates="customer")
    sales_orders: Mapped[list["SalesOrder"]] = relationship("SalesOrder", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name})>"


class Product(Base, TimestampMixin):
    """Product model"""
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_number: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    inverter_type: Mapped[InverterTypeEnum] = mapped_column(SQLEnum(InverterTypeEnum), nullable=False)
    power_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # in watts
    frequency: Mapped[Numeric] = mapped_column(Numeric(5, 2), nullable=False)
    efficiency: Mapped[Numeric] = mapped_column(Numeric(5, 2), nullable=False)
    surge_power: Mapped[int] = mapped_column(Integer, nullable=False)  # in watts
    warranty_years: Mapped[int] = mapped_column(Integer, nullable=False)
    input_voltage: Mapped[Numeric] = mapped_column(Numeric(5, 2), nullable=False)
    output_voltage: Mapped[Numeric] = mapped_column(Numeric(5, 2), nullable=False)
    
    # Relationships
    rfq_items: Mapped[list["RFQItem"]] = relationship("RFQItem", back_populates="product")
    quotation_items: Mapped[list["QuotationItem"]] = relationship("QuotationItem", back_populates="product")
    sales_order_items: Mapped[list["SalesOrderItem"]] = relationship("SalesOrderItem", back_populates="product")
    bill_of_materials = relationship("BillOfMaterial", back_populates="product")
    manufacturing_orders = relationship("ManufacturingOrder", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"


class RFQ(Base, TimestampMixin):
    """RFQ model"""
    __tablename__ = "rfqs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[RFQStatusEnum] = mapped_column(SQLEnum(RFQStatusEnum), default=RFQStatusEnum.DRAFT, nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    items: Mapped[list["RFQItem"]] = relationship("RFQItem", back_populates="rfq", cascade="all, delete-orphan")
    quotations: Mapped[list["Quotation"]] = relationship("Quotation", back_populates="rfq")
    
    def __repr__(self):
        return f"<RFQ(id={self.id}, status={self.status.value})>"


class RFQItem(Base):
    """RFQ Item model"""
    __tablename__ = "rfq_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rfq_id: Mapped[int] = mapped_column(Integer, ForeignKey("rfqs.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Relationships
    rfq: Mapped["RFQ"] = relationship("RFQ", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="rfq_items")
    
    def __repr__(self):
        return f"<RFQItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"


class Quotation(Base, TimestampMixin):
    """Quotation model"""
    __tablename__ = "quotations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    rfq_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("rfqs.id", ondelete="SET NULL"), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    expiration_date: Mapped[date] = mapped_column(Date, nullable=False)
    invoicing_and_shipping_address: Mapped[str] = mapped_column(Text, nullable=False)
    total_amount: Mapped[Numeric] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    status: Mapped[QuotationStatusEnum] = mapped_column(SQLEnum(QuotationStatusEnum), default=QuotationStatusEnum.QUOTATION, nullable=False)
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    email_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    email_sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    email_history: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="quotations")
    rfq: Mapped[Optional["RFQ"]] = relationship("RFQ", back_populates="quotations")
    quotation_items: Mapped[list["QuotationItem"]] = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")
    sales_orders: Mapped[list["SalesOrder"]] = relationship("SalesOrder", back_populates="quotation")
    
    def __repr__(self):
        return f"<Quotation(id={self.id}, customer_id={self.customer_id}, total_amount={self.total_amount})>"


class QuotationItem(Base):
    """Quotation Item model"""
    __tablename__ = "quotation_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quotation_id: Mapped[int] = mapped_column(Integer, ForeignKey("quotations.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Relationships
    quotation: Mapped["Quotation"] = relationship("Quotation", back_populates="quotation_items")
    product: Mapped["Product"] = relationship("Product", back_populates="quotation_items")
    
    def __repr__(self):
        return f"<QuotationItem(id={self.id}, quotation_id={self.quotation_id}, product_id={self.product_id})>"


class SalesOrder(Base, TimestampMixin):
    """Sales Order model"""
    __tablename__ = "sales_orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    quotation_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("quotations.id", ondelete="SET NULL"), nullable=True)
    total_amount: Mapped[Numeric] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    status: Mapped[SalesOrderStatusEnum] = mapped_column(SQLEnum(SalesOrderStatusEnum), default=SalesOrderStatusEnum.PENDING, nullable=False)
    delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="sales_orders")
    quotation: Mapped[Optional["Quotation"]] = relationship("Quotation", back_populates="sales_orders")
    order_items: Mapped[list["SalesOrderItem"]] = relationship("SalesOrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SalesOrder(id={self.id}, customer_id={self.customer_id}, status={self.status.value})>"


class SalesOrderItem(Base):
    """Sales Order Item model"""
    __tablename__ = "sales_order_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Relationships
    order: Mapped["SalesOrder"] = relationship("SalesOrder", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product", back_populates="sales_order_items")
    manufacturing_orders = relationship("ManufacturingOrder", back_populates="sales_order_item")
    
    def __repr__(self):
        return f"<SalesOrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id})>"

