"""
Inventory module database models
"""
from sqlalchemy import (
    String,
    Integer,
    Text,
    ForeignKey,
    Numeric,
    Boolean,
    DateTime,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
from datetime import datetime
import enum

from app.models.base import Base, TimestampMixin


class StatusEnum(str, enum.Enum):
    """Purchase requisition status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    FULFILLED = "fulfilled"


class PriorityEnum(str, enum.Enum):
    """Purchase requisition priority"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PurchaseOrderStatusEnum(str, enum.Enum):
    """Purchase order status"""
    DRAFT = "draft"
    OPEN_ORDER = "open_order"
    APPROVED = "approved"
    RECEIVED = "received"
    INVOICED = "invoiced"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Supplier(Base, TimestampMixin):
    """Supplier model"""
    __tablename__ = "suppliers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_added: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    components: Mapped[list["Component"]] = relationship("Component", back_populates="supplier")
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="supplier")
    
    # Procurement module relationships
    performance_records: Mapped[list["SupplierPerformance"]] = relationship(
        "SupplierPerformance",
        back_populates="supplier",
        cascade="all, delete-orphan"
    )
    contracts: Mapped[list["SupplierContract"]] = relationship(
        "SupplierContract",
        back_populates="supplier",
        cascade="all, delete-orphan"
    )

    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name={self.name})>"


class Category(Base):
    """Category model"""
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    components: Mapped[list["Component"]] = relationship("Component", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class Component(Base, TimestampMixin):
    """Component model"""
    __tablename__ = "components"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reorder_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    order_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="pcs", nullable=False)
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("suppliers.id"), nullable=True)
    cost: Mapped[Numeric] = mapped_column(Numeric(10, 2), default=0.0, nullable=False)
    
    # Relationships
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="components")
    supplier: Mapped[Optional["Supplier"]] = relationship("Supplier", back_populates="components")
    purchase_requisitions: Mapped[list["PurchaseRequisition"]] = relationship("PurchaseRequisition", back_populates="component")
    replenish_transactions: Mapped[list["ReplenishTransaction"]] = relationship("ReplenishTransaction", back_populates="component")
    consumption_transactions = relationship("ConsumptionTransaction", back_populates="component")
    material_requisition_items = relationship("MaterialRequisitionItem", back_populates="component")
    bom_items = relationship("BOMItem", back_populates="component")
    
    # Procurement module relationship
    inventory_policy: Mapped[Optional["ComponentInventoryPolicy"]] = relationship(
        "ComponentInventoryPolicy",
        back_populates="component",
        uselist=False,
        cascade="all, delete-orphan"
    )

    
    def __repr__(self):
        return f"<Component(id={self.id}, name={self.name}, quantity={self.quantity})>"


class PurchaseRequisition(Base, TimestampMixin):
    """Purchase Requisition model"""
    __tablename__ = "purchase_requisitions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("components.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[StatusEnum] = mapped_column(SQLEnum(StatusEnum), default=StatusEnum.PENDING, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    priority: Mapped[PriorityEnum] = mapped_column(SQLEnum(PriorityEnum), default=PriorityEnum.HIGH, nullable=False)
    
    # Relationships
    component: Mapped["Component"] = relationship("Component", back_populates="purchase_requisitions")
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship("PurchaseOrder", back_populates="purchase_requisition")
    replenish_transactions: Mapped[list["ReplenishTransaction"]] = relationship("ReplenishTransaction", back_populates="purchase_requisition")
    
    def __repr__(self):
        return f"<PurchaseRequisition(id={self.id}, component_id={self.component_id}, quantity={self.quantity}, status={self.status.value})>"


class PurchaseOrder(Base, TimestampMixin):
    """Purchase Order model"""
    __tablename__ = "purchase_orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    creator_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    purchase_requisition_id: Mapped[int] = mapped_column(Integer, ForeignKey("purchase_requisitions.id"), nullable=False)
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("suppliers.id"), nullable=True)
    status: Mapped[PurchaseOrderStatusEnum] = mapped_column(SQLEnum(PurchaseOrderStatusEnum), default=PurchaseOrderStatusEnum.DRAFT, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price_per_unit: Mapped[Optional[Numeric]] = mapped_column(Numeric(10, 2), nullable=True)
    total_price: Mapped[Optional[Numeric]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Relationships
    purchase_requisition: Mapped["PurchaseRequisition"] = relationship("PurchaseRequisition", back_populates="purchase_orders")
    supplier: Mapped[Optional["Supplier"]] = relationship("Supplier", back_populates="purchase_orders")
    
    def __repr__(self):
        return f"<PurchaseOrder(id={self.id}, purchase_requisition_id={self.purchase_requisition_id}, status={self.status.value})>"


class ReplenishTransaction(Base):
    """Replenish Transaction model"""
    __tablename__ = "replenish_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purchase_requisition_id: Mapped[int] = mapped_column(Integer, ForeignKey("purchase_requisitions.id"), nullable=False)
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("components.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    purchase_requisition: Mapped["PurchaseRequisition"] = relationship("PurchaseRequisition", back_populates="replenish_transactions")
    component: Mapped["Component"] = relationship("Component", back_populates="replenish_transactions")
    
    def __repr__(self):
        return f"<ReplenishTransaction(id={self.id}, component_id={self.component_id}, quantity={self.quantity})>"


class ConsumptionTransaction(Base):
    """Consumption Transaction model"""
    __tablename__ = "consumption_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    material_requisition_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_requisition_items.id"), nullable=False)
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("components.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    component = relationship("Component", back_populates="consumption_transactions")
    material_requisition_item = relationship("MaterialRequisitionItem", back_populates="consumption_transactions")
    
    def __repr__(self):
        return f"<ConsumptionTransaction(id={self.id}, component_id={self.component_id}, quantity={self.quantity})>"

