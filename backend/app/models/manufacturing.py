"""
Manufacturing module database models
"""
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Enum as SQLEnum,
    Interval,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime, timedelta
import enum

from app.models.base import Base, TimestampMixin


class ManufacturingOrderStatusEnum(str, enum.Enum):
    """Manufacturing order status"""
    PENDING = "pending"
    MR_SENT = "mr_sent"
    MR_APPROVED = "mr_approved"
    MR_REJECTED = "mr_rejected"
    IN_PRODUCTION = "in_production"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaterialRequisitionStatusEnum(str, enum.Enum):
    """Material requisition status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PARTIALLY_APPROVED = "partialy_approved"
    FULFILLED = "fulfilled"


class MaterialRequisitionItemStatusEnum(str, enum.Enum):
    """Material requisition item status"""
    PENDING = "pending"
    APPROVED = "approved"


class ManufacturingOrder(Base, TimestampMixin):
    """Manufacturing Order model"""
    __tablename__ = "manufacturing_orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sales_order_item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sales_order_items.id"), nullable=True)
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    bom_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bill_of_materials.id"), nullable=True)
    status: Mapped[ManufacturingOrderStatusEnum] = mapped_column(SQLEnum(ManufacturingOrderStatusEnum), default=ManufacturingOrderStatusEnum.PENDING, nullable=False)
    creator_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    end_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    production_start_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_mfg_lead_time: Mapped[Optional[timedelta]] = mapped_column(Interval, nullable=True)
    mfg_lead_time: Mapped[Optional[timedelta]] = mapped_column(Interval, nullable=True)
    production_lead_time: Mapped[Optional[timedelta]] = mapped_column(Interval, nullable=True)
    
    # Relationships
    sales_order_item = relationship("SalesOrderItem", back_populates="manufacturing_orders")
    product = relationship("Product", back_populates="manufacturing_orders")
    bom: Mapped[Optional["BillOfMaterial"]] = relationship("BillOfMaterial", back_populates="manufacturing_orders")
    material_requisitions: Mapped[list["MaterialRequisition"]] = relationship("MaterialRequisition", back_populates="manufacturing_order")
    
    def __repr__(self):
        return f"<ManufacturingOrder(id={self.id}, status={self.status.value})>"


class MaterialRequisition(Base, TimestampMixin):
    """Material Requisition model"""
    __tablename__ = "material_requisitions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manufacturing_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False)
    bom_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bill_of_materials.id"), nullable=True)
    status: Mapped[MaterialRequisitionStatusEnum] = mapped_column(SQLEnum(MaterialRequisitionStatusEnum), default=MaterialRequisitionStatusEnum.PENDING, nullable=False)
    
    # Relationships
    manufacturing_order: Mapped["ManufacturingOrder"] = relationship("ManufacturingOrder", back_populates="material_requisitions")
    bom: Mapped[Optional["BillOfMaterial"]] = relationship("BillOfMaterial", back_populates="material_requisitions")
    items: Mapped[list["MaterialRequisitionItem"]] = relationship("MaterialRequisitionItem", back_populates="material_requisition", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MaterialRequisition(id={self.id}, manufacturing_order_id={self.manufacturing_order_id}, status={self.status.value})>"


class MaterialRequisitionItem(Base):
    """Material Requisition Item model"""
    __tablename__ = "material_requisition_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    material_requisition_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_requisitions.id"), nullable=False)
    component_id: Mapped[int] = mapped_column(Integer, ForeignKey("components.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[MaterialRequisitionItemStatusEnum] = mapped_column(SQLEnum(MaterialRequisitionItemStatusEnum), default=MaterialRequisitionItemStatusEnum.PENDING, nullable=False)
    
    # Relationships
    material_requisition: Mapped["MaterialRequisition"] = relationship("MaterialRequisition", back_populates="items")
    component = relationship("Component", back_populates="material_requisition_items")
    consumption_transactions = relationship("ConsumptionTransaction", back_populates="material_requisition_item")
    
    def __repr__(self):
        return f"<MaterialRequisitionItem(id={self.id}, material_requisition_id={self.material_requisition_id}, component_id={self.component_id})>"


class BillOfMaterial(Base, TimestampMixin):
    """Bill of Material model"""
    __tablename__ = "bill_of_materials"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id"), nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="bill_of_materials")
    bom_items: Mapped[list["BOMItem"]] = relationship("BOMItem", back_populates="bill_of_material", cascade="all, delete-orphan")
    manufacturing_orders = relationship("ManufacturingOrder", back_populates="bom")
    material_requisitions = relationship("MaterialRequisition", back_populates="bom")
    
    def __repr__(self):
        return f"<BillOfMaterial(id={self.id}, name={self.name})>"


class BOMItem(Base):
    """BOM Item model"""
    __tablename__ = "bom_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bill_of_material_id: Mapped[int] = mapped_column(Integer, ForeignKey("bill_of_materials.id"), nullable=False)
    component_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("components.id"), nullable=True, default=1)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    bill_of_material: Mapped["BillOfMaterial"] = relationship("BillOfMaterial", back_populates="bom_items")
    component = relationship("Component", back_populates="bom_items")
    
    def __repr__(self):
        return f"<BOMItem(id={self.id}, bill_of_material_id={self.bill_of_material_id}, component_id={self.component_id})>"

