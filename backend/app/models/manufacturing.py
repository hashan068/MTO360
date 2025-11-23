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
    Numeric,
    Boolean,
    Date,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime, timedelta, date
from decimal import Decimal
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
    BLOCKED = "blocked"  # New status for blocked operations
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


class OperationStatusEnum(str, enum.Enum):
    """Operation status for manufacturing order operations"""
    PENDING = "pending"  # Not yet scheduled
    SCHEDULED = "scheduled"  # Scheduled but not started
    IN_PROGRESS = "in_progress"  # Currently being worked on
    COMPLETED = "completed"  # Finished
    BLOCKED = "blocked"  # Cannot proceed due to issue
    CANCELLED = "cancelled"  # Cancelled


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
    
    # Scheduling fields (new)
    scheduled_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # Earliest operation start
    scheduled_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # Latest operation end
    total_scheduled_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Total duration of all operations
    
    # Relationships
    sales_order_item = relationship("SalesOrderItem", back_populates="manufacturing_orders")
    product = relationship("Product", back_populates="manufacturing_orders")
    bom: Mapped[Optional["BillOfMaterial"]] = relationship("BillOfMaterial", back_populates="manufacturing_orders")
    material_requisitions: Mapped[list["MaterialRequisition"]] = relationship("MaterialRequisition", back_populates="manufacturing_order")
    operations: Mapped[list["ManufacturingOrderOperation"]] = relationship("ManufacturingOrderOperation", back_populates="manufacturing_order", cascade="all, delete-orphan")
    
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
    operation_routes: Mapped[list["OperationRoute"]] = relationship("OperationRoute", back_populates="bom")
    
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


# ========== Production Scheduling Models ==========

class WorkCenter(Base, TimestampMixin):
    """Work Center model for production scheduling"""
    __tablename__ = "work_centers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "Assembly Station 1"
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # e.g., "ASM-01"
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    capacity_hours_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # e.g., 8.0, 16.0 for two shifts
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    route_operations: Mapped[list["RouteOperation"]] = relationship("RouteOperation", back_populates="work_center")
    mo_operations: Mapped[list["ManufacturingOrderOperation"]] = relationship("ManufacturingOrderOperation", back_populates="work_center")
    work_center_schedules: Mapped[list["WorkCenterSchedule"]] = relationship("WorkCenterSchedule", back_populates="work_center", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkCenter(id={self.id}, code={self.code}, name={self.name})>"


class OperationRoute(Base, TimestampMixin):
    """Operation Route model - defines manufacturing steps for a product"""
    __tablename__ = "operation_routes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)  # e.g., "Standard Inverter Assembly"
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id"), nullable=True)
    bom_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bill_of_materials.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="operation_routes")
    bom: Mapped[Optional["BillOfMaterial"]] = relationship("BillOfMaterial", back_populates="operation_routes")
    route_operations: Mapped[list["RouteOperation"]] = relationship("RouteOperation", back_populates="route", cascade="all, delete-orphan", order_by="RouteOperation.sequence")
    
    def __repr__(self):
        return f"<OperationRoute(id={self.id}, name={self.name})>"


class RouteOperation(Base):
    """Route Operation model - individual step in an operation route"""
    __tablename__ = "route_operations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("operation_routes.id"), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3...
    name: Mapped[str] = mapped_column(String(200), nullable=False)  # e.g., "PCB Assembly"
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    work_center_id: Mapped[int] = mapped_column(Integer, ForeignKey("work_centers.id"), nullable=False)
    standard_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False)  # Estimated duration
    setup_time_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Optional setup time
    
    # Relationships
    route: Mapped["OperationRoute"] = relationship("OperationRoute", back_populates="route_operations")
    work_center: Mapped["WorkCenter"] = relationship("WorkCenter", back_populates="route_operations")
    mo_operations: Mapped[list["ManufacturingOrderOperation"]] = relationship("ManufacturingOrderOperation", back_populates="route_operation")
    
    def __repr__(self):
        return f"<RouteOperation(id={self.id}, route_id={self.route_id}, sequence={self.sequence}, name={self.name})>"


class ManufacturingOrderOperation(Base, TimestampMixin):
    """Manufacturing Order Operation model - actual operations for a specific MO"""
    __tablename__ = "manufacturing_order_operations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    manufacturing_order_id: Mapped[int] = mapped_column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False)
    route_operation_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("route_operations.id"), nullable=True)  # Template reference
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    work_center_id: Mapped[int] = mapped_column(Integer, ForeignKey("work_centers.id"), nullable=False)
    
    # Scheduling
    scheduled_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Execution
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Status
    status: Mapped[OperationStatusEnum] = mapped_column(SQLEnum(OperationStatusEnum), default=OperationStatusEnum.PENDING, nullable=False)
    
    # Assignment
    assigned_operator_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    blocking_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # If status is blocked
    
    # Relationships
    manufacturing_order: Mapped["ManufacturingOrder"] = relationship("ManufacturingOrder", back_populates="operations")
    work_center: Mapped["WorkCenter"] = relationship("WorkCenter", back_populates="mo_operations")
    assigned_operator = relationship("User")  # Assumes User model exists
    route_operation: Mapped[Optional["RouteOperation"]] = relationship("RouteOperation", back_populates="mo_operations")
    
    def __repr__(self):
        return f"<ManufacturingOrderOperation(id={self.id}, mo_id={self.manufacturing_order_id}, sequence={self.sequence}, status={self.status.value})>"


class WorkCenterSchedule(Base):
    """Work Center Schedule model - tracks capacity allocation per work center per day"""
    __tablename__ = "work_center_schedules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    work_center_id: Mapped[int] = mapped_column(Integer, ForeignKey("work_centers.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    available_capacity_minutes: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g., 480 for 8 hours
    scheduled_capacity_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Sum of scheduled operations
    utilization_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)  # Calculated field
    
    # Relationships
    work_center: Mapped["WorkCenter"] = relationship("WorkCenter", back_populates="work_center_schedules")
    
    def __repr__(self):
        return f"<WorkCenterSchedule(id={self.id}, work_center_id={self.work_center_id}, date={self.date}, utilization={self.utilization_percentage}%)>"
