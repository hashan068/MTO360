"""
Quality Management System database models
"""
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Enum as SQLEnum,
    DateTime,
    Numeric,
    Boolean,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
from decimal import Decimal
import enum

from app.models.base import Base, TimestampMixin


# ========== Enums ==========

class InspectionTypeEnum(str, enum.Enum):
    """Inspection type classification"""
    IN_PROCESS = "in_process"  # During manufacturing operations
    FINAL = "final"  # Before delivery
    RECEIVING = "receiving"  # Incoming materials
    FIRST_ARTICLE = "first_article"  # FAI - first piece inspection


class InspectionResultEnum(str, enum.Enum):
    """Inspection result"""
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"  # Pass with notes/conditions


class DefectTypeEnum(str, enum.Enum):
    """Defect type classification"""
    MATERIAL = "material"  # Raw material defects
    WORKMANSHIP = "workmanship"  # Manufacturing/assembly defects
    DESIGN = "design"  # Design-related defects
    OTHER = "other"  # Other defects


class SeverityEnum(str, enum.Enum):
    """Defect severity levels"""
    CRITICAL = "critical"  # Safety or critical function impact
    MAJOR = "major"  # Significant functional impact
    MINOR = "minor"  # Minor impact on function or appearance
    COSMETIC = "cosmetic"  # Appearance only, no functional impact


class ResponsiblePartyEnum(str, enum.Enum):
    """Party responsible for defect"""
    INTERNAL = "internal"  # Internal manufacturing/process
    SUPPLIER = "supplier"  # Supplier materials/components
    DESIGN = "design"  # Design/engineering
    CUSTOMER = "customer"  # Customer-caused


class DefectStatusEnum(str, enum.Enum):
    """Defect status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class NCRStatusEnum(str, enum.Enum):
    """Non-conformance report status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    CLOSED = "closed"


class PriorityEnum(str, enum.Enum):
    """Priority levels for NCRs and CAPAs"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class DispositionEnum(str, enum.Enum):
    """NCR disposition decision"""
    REWORK = "rework"  # Rework to meet specifications
    SCRAP = "scrap"  # Scrap the items
    USE_AS_IS = "use_as_is"  # Accept as-is (deviation)
    RETURN_TO_SUPPLIER = "return_to_supplier"  # Return to supplier


class ActionTypeEnum(str, enum.Enum):
    """CAPA action type"""
    CORRECTIVE = "corrective"  # Fix the immediate problem
    PREVENTIVE = "preventive"  # Prevent recurrence


class CAPAStatusEnum(str, enum.Enum):
    """CAPA status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    VERIFICATION = "verification"  # Verifying effectiveness
    CLOSED = "closed"


class HoldTypeEnum(str, enum.Enum):
    """Quality hold type"""
    INVENTORY = "inventory"  # Hold inventory/components
    MANUFACTURING_ORDER = "manufacturing_order"  # Hold MO
    SALES_ORDER = "sales_order"  # Hold SO shipment


class HoldStatusEnum(str, enum.Enum):
    """Quality hold status"""
    ACTIVE = "active"
    RELEASED = "released"
    CANCELLED = "cancelled"


# ========== Models ==========

class InspectionPoint(Base, TimestampMixin):
    """
    Inspection Point model - defines inspection criteria and requirements
    Can be attached to route operations (template) or used standalone
    """
    __tablename__ = "inspection_points"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_operation_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("route_operations.id"), nullable=True
    )
    inspection_type: Mapped[InspectionTypeEnum] = mapped_column(
        SQLEnum(InspectionTypeEnum), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_required: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )  # If true, operation cannot complete if failed
    
    # Inspection criteria stored as JSON
    # Example: [{"item": "Solder quality", "min": null, "max": null, "pass_criteria": "No cold joints"},...]
    checklist_items: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    route_operation = relationship("RouteOperation", foreign_keys=[route_operation_id])
    inspection_results: Mapped[list["InspectionResult"]] = relationship(
        "InspectionResult", back_populates="inspection_point", cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<InspectionPoint(id={self.id}, name={self.name}, type={self.inspection_type.value})>"


class InspectionResult(Base, TimestampMixin):
    """
    Inspection Result model - records results of an inspection
    """
    __tablename__ = "inspection_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inspection_point_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inspection_points.id"), nullable=False
    )
    
    # Context - what is being inspected
    mo_operation_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("manufacturing_order_operations.id"), nullable=True
    )
    manufacturing_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("manufacturing_orders.id"), nullable=True
    )
    component_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("components.id"), nullable=True
    )
    
    # Inspector and timing
    inspector_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    inspection_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    
    # Result
    result: Mapped[InspectionResultEnum] = mapped_column(
        SQLEnum(InspectionResultEnum), nullable=False
    )
    
    # Detailed results stored as JSON
    # Example: [{"item": "Solder quality", "result": "pass", "measurement": null, "notes": "Good"}]
    checklist_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    measurements: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Attachments (URLs to photos/documents)
    photo_urls: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    document_urls: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    inspection_point: Mapped["InspectionPoint"] = relationship(
        "InspectionPoint", back_populates="inspection_results"
    )
    mo_operation = relationship(
        "ManufacturingOrderOperation", 
        foreign_keys=[mo_operation_id],
        back_populates="inspection_results"
    )
    manufacturing_order = relationship(
        "ManufacturingOrder", 
        foreign_keys=[manufacturing_order_id],
        back_populates="inspection_results"
    )
    component = relationship("Component", foreign_keys=[component_id])
    inspector = relationship("User", foreign_keys=[inspector_id])
    defects: Mapped[list["Defect"]] = relationship(
        "Defect", back_populates="inspection_result", cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<InspectionResult(id={self.id}, result={self.result.value}, inspection_point_id={self.inspection_point_id})>"


class Defect(Base, TimestampMixin):
    """
    Defect model - records quality defects found during production or inspection
    """
    __tablename__ = "defects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    defect_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # Auto-generated: DEF-YYYYMMDD-XXXX
    
    # Context - where was the defect found
    manufacturing_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("manufacturing_orders.id"), nullable=True
    )
    mo_operation_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("manufacturing_order_operations.id"), nullable=True
    )
    inspection_result_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("inspection_results.id"), nullable=True
    )
    component_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("components.id"), nullable=True
    )
    sales_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_orders.id"), nullable=True
    )  # For customer returns
    
    # Classification
    defect_type: Mapped[DefectTypeEnum] = mapped_column(
        SQLEnum(DefectTypeEnum), nullable=False
    )
    defect_category: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[SeverityEnum] = mapped_column(SQLEnum(SeverityEnum), nullable=False)
    
    # Details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity_affected: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Responsibility
    reported_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    responsible_party: Mapped[ResponsiblePartyEnum] = mapped_column(
        SQLEnum(ResponsiblePartyEnum), nullable=False
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    supplier_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=True
    )
    
    # Status
    status: Mapped[DefectStatusEnum] = mapped_column(
        SQLEnum(DefectStatusEnum), default=DefectStatusEnum.OPEN, nullable=False
    )
    
    # Attachments
    photo_urls: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    manufacturing_order = relationship(
        "ManufacturingOrder", foreign_keys=[manufacturing_order_id], back_populates="defects"
    )
    mo_operation = relationship(
        "ManufacturingOrderOperation", foreign_keys=[mo_operation_id], back_populates="defects"
    )
    inspection_result: Mapped[Optional["InspectionResult"]] = relationship(
        "InspectionResult", back_populates="defects"
    )
    component = relationship("Component", foreign_keys=[component_id])
    sales_order = relationship("SalesOrder", foreign_keys=[sales_order_id])
    reported_by = relationship("User", foreign_keys=[reported_by_id])
    operator = relationship("User", foreign_keys=[operator_id])
    supplier = relationship("Supplier", foreign_keys=[supplier_id])
    ncr: Mapped[Optional["NonConformanceReport"]] = relationship(
        "NonConformanceReport", back_populates="defect", uselist=False
    )
    capas: Mapped[list["CorrectiveAction"]] = relationship(
        "CorrectiveAction", back_populates="defect", foreign_keys="[CorrectiveAction.defect_id]"
    )
    
    def __repr__(self):
        return f"<Defect(id={self.id}, number={self.defect_number}, type={self.defect_type.value}, severity={self.severity.value})>"


class NonConformanceReport(Base, TimestampMixin):
    """
    Non-Conformance Report (NCR) model - formal quality issue investigation and disposition
    """
    __tablename__ = "non_conformance_reports"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ncr_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # Auto-generated: NCR-YYYYMMDD-XXXX
    
    # Context
    defect_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("defects.id"), nullable=True
    )
    manufacturing_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("manufacturing_orders.id"), nullable=True
    )
    
    # Status and priority
    status: Mapped[NCRStatusEnum] = mapped_column(
        SQLEnum(NCRStatusEnum), default=NCRStatusEnum.OPEN, nullable=False
    )
    priority: Mapped[PriorityEnum] = mapped_column(
        SQLEnum(PriorityEnum), default=PriorityEnum.NORMAL, nullable=False
    )
    
    # Investigation
    description: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_cause_category: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # 5M: Man, Machine, Material, Method, Measurement
    containment_actions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Disposition
    disposition: Mapped[Optional[DispositionEnum]] = mapped_column(
        SQLEnum(DispositionEnum), nullable=True
    )
    disposition_justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quantity_affected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Cost impact
    rework_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    scrap_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    total_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Ownership
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Quality Engineer
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    
    # Approval
    approver_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    approval_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Closure
    closed_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    closed_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    defect: Mapped[Optional["Defect"]] = relationship("Defect", back_populates="ncr")
    manufacturing_order = relationship(
        "ManufacturingOrder", foreign_keys=[manufacturing_order_id], back_populates="ncrs"
    )
    owner = relationship("User", foreign_keys=[owner_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    approver = relationship("User", foreign_keys=[approver_id])
    closed_by = relationship("User", foreign_keys=[closed_by_id])
    capa: Mapped[Optional["CorrectiveAction"]] = relationship(
        "CorrectiveAction", back_populates="ncr", uselist=False, foreign_keys="[CorrectiveAction.ncr_id]"
    )
    rework_operations: Mapped[list["ReworkOperation"]] = relationship(
        "ReworkOperation", back_populates="ncr", cascade="all, delete-orphan"
    )
    quality_holds: Mapped[list["QualityHold"]] = relationship(
        "QualityHold", back_populates="ncr", cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<NonConformanceReport(id={self.id}, number={self.ncr_number}, status={self.status.value})>"


class ReworkOperation(Base, TimestampMixin):
    """
    Rework Operation model - tracks rework activities to correct defects
    """
    __tablename__ = "rework_operations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ncr_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("non_conformance_reports.id"), nullable=False
    )
    manufacturing_order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("manufacturing_orders.id"), nullable=False
    )
    work_center_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("work_centers.id"), nullable=False
    )
    
    # Scheduling
    scheduled_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scheduled_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scheduled_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Execution
    actual_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    
    # Status (reusing OperationStatusEnum from manufacturing)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    
    # Assignment
    assigned_operator_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    
    # Details
    rework_description: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Cost
    labor_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    material_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Verification
    re_inspection_result_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("inspection_results.id"), nullable=True
    )
    
    # Relationships
    ncr: Mapped["NonConformanceReport"] = relationship(
        "NonConformanceReport", back_populates="rework_operations"
    )
    manufacturing_order = relationship(
        "ManufacturingOrder", foreign_keys=[manufacturing_order_id]
    )
    work_center = relationship("WorkCenter", foreign_keys=[work_center_id])
    assigned_operator = relationship("User", foreign_keys=[assigned_operator_id])
    re_inspection_result = relationship(
        "InspectionResult", foreign_keys=[re_inspection_result_id]
    )
    
    def __repr__(self):
        return f"<ReworkOperation(id={self.id}, ncr_id={self.ncr_id}, status={self.status})>"


class CorrectiveAction(Base, TimestampMixin):
    """
    Corrective Action (CAPA) model - manages corrective and preventive actions
    """
    __tablename__ = "corrective_actions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    capa_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # Auto-generated: CAPA-YYYYMMDD-XXXX
    
    # Context
    ncr_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("non_conformance_reports.id"), nullable=True
    )
    defect_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("defects.id"), nullable=True
    )
    
    # Type
    action_type: Mapped[ActionTypeEnum] = mapped_column(
        SQLEnum(ActionTypeEnum), nullable=False
    )
    
    # Status and priority
    status: Mapped[CAPAStatusEnum] = mapped_column(
        SQLEnum(CAPAStatusEnum), default=CAPAStatusEnum.OPEN, nullable=False
    )
    priority: Mapped[PriorityEnum] = mapped_column(
        SQLEnum(PriorityEnum), default=PriorityEnum.NORMAL, nullable=False
    )
    
    # Root cause analysis
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause_method: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # 5_whys, fishbone, other
    root_cause_analysis: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True
    )  # Structured RCA data
    
    # Actions - stored as JSON array of action items
    # Example: [{"id": "1", "description": "Retrain operators", "owner_id": 5, "due_date": "2024-01-15", "status": "completed"}]
    corrective_actions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    preventive_actions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Ownership
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    
    # Verification
    effectiveness_verification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verification_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    verified_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    
    # Closure
    closed_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    
    # Relationships
    ncr: Mapped[Optional["NonConformanceReport"]] = relationship(
        "NonConformanceReport", back_populates="capa"
    )
    defect: Mapped[Optional["Defect"]] = relationship("Defect", back_populates="capas")
    owner = relationship("User", foreign_keys=[owner_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    closed_by = relationship("User", foreign_keys=[closed_by_id])
    
    def __repr__(self):
        return f"<CorrectiveAction(id={self.id}, number={self.capa_number}, type={self.action_type.value}, status={self.status.value})>"


class QualityHold(Base, TimestampMixin):
    """
    Quality Hold model - tracks quality holds on inventory, MOs, or sales orders
    """
    __tablename__ = "quality_holds"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hold_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # Auto-generated: QH-YYYYMMDD-XXXX
    
    # Context
    ncr_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("non_conformance_reports.id"), nullable=False
    )
    hold_type: Mapped[HoldTypeEnum] = mapped_column(SQLEnum(HoldTypeEnum), nullable=False)
    
    # Target - what is being held
    component_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("components.id"), nullable=True
    )
    manufacturing_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("manufacturing_orders.id"), nullable=True
    )
    sales_order_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sales_orders.id"), nullable=True
    )
    
    # Status
    status: Mapped[HoldStatusEnum] = mapped_column(
        SQLEnum(HoldStatusEnum), default=HoldStatusEnum.ACTIVE, nullable=False
    )
    
    # Details
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    quantity_held: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Ownership
    placed_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    placed_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    
    # Release
    released_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    released_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    release_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    ncr: Mapped["NonConformanceReport"] = relationship(
        "NonConformanceReport", back_populates="quality_holds"
    )
    component = relationship("Component", foreign_keys=[component_id])
    manufacturing_order = relationship(
        "ManufacturingOrder", foreign_keys=[manufacturing_order_id], back_populates="quality_holds"
    )
    sales_order = relationship("SalesOrder", foreign_keys=[sales_order_id])
    placed_by = relationship("User", foreign_keys=[placed_by_id])
    released_by = relationship("User", foreign_keys=[released_by_id])
    
    def __repr__(self):
        return f"<QualityHold(id={self.id}, number={self.hold_number}, type={self.hold_type.value}, status={self.status.value})>"
