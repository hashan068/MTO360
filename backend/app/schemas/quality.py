"""
Pydantic schemas for Quality Management module
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.models.quality import (
    InspectionTypeEnum,
    InspectionResultEnum,
    DefectTypeEnum,
    SeverityEnum,
    ResponsiblePartyEnum,
    DefectStatusEnum,
    NCRStatusEnum,
    PriorityEnum,
    DispositionEnum,
    ActionTypeEnum,
    CAPAStatusEnum,
    HoldTypeEnum,
    HoldStatusEnum,
)


# ========== Inspection Schemas ==========

class InspectionPointCreate(BaseModel):
    route_operation_id: Optional[int] = None
    inspection_type: InspectionTypeEnum
    name: str
    description: Optional[str] = None
    is_required: bool = True
    checklist_items: Optional[List[Dict[str, Any]]] = None


class InspectionPointUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None
    checklist_items: Optional[List[Dict[str, Any]]] = None


class InspectionPointResponse(BaseModel):
    id: int
    route_operation_id: Optional[int] = None
    inspection_type: InspectionTypeEnum
    name: str
    description: Optional[str] = None
    is_required: bool
    checklist_items: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InspectionResultCreate(BaseModel):
    inspection_point_id: int
    mo_operation_id: Optional[int] = None
    manufacturing_order_id: Optional[int] = None
    component_id: Optional[int] = None
    inspector_id: int
    result: InspectionResultEnum
    checklist_results: Optional[List[Dict[str, Any]]] = None
    measurements: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    document_urls: Optional[List[str]] = None


class InspectionResultUpdate(BaseModel):
    result: Optional[InspectionResultEnum] = None
    checklist_results: Optional[List[Dict[str, Any]]] = None
    measurements: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    document_urls: Optional[List[str]] = None


class InspectionResultResponse(BaseModel):
    id: int
    inspection_point_id: int
    inspection_point_name: Optional[str] = None
    mo_operation_id: Optional[int] = None
    manufacturing_order_id: Optional[int] = None
    component_id: Optional[int] = None
    inspector_id: int
    inspector_name: Optional[str] = None
    inspection_date: datetime
    result: InspectionResultEnum
    checklist_results: Optional[List[Dict[str, Any]]] = None
    measurements: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    document_urls: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ========== Defect Schemas ==========

class DefectCreate(BaseModel):
    manufacturing_order_id: Optional[int] = None
    mo_operation_id: Optional[int] = None
    inspection_result_id: Optional[int] = None
    component_id: Optional[int] = None
    sales_order_id: Optional[int] = None
    defect_type: DefectTypeEnum
    defect_category: str
    severity: SeverityEnum
    description: str
    location: str
    quantity_affected: int = 1
    root_cause: Optional[str] = None
    reported_by_id: int
    responsible_party: ResponsiblePartyEnum
    operator_id: Optional[int] = None
    supplier_id: Optional[int] = None
    photo_urls: Optional[List[str]] = None


class DefectUpdate(BaseModel):
    defect_category: Optional[str] = None
    severity: Optional[SeverityEnum] = None
    description: Optional[str] = None
    location: Optional[str] = None
    quantity_affected: Optional[int] = None
    root_cause: Optional[str] = None
    responsible_party: Optional[ResponsiblePartyEnum] = None
    operator_id: Optional[int] = None
    supplier_id: Optional[int] = None
    status: Optional[DefectStatusEnum] = None
    photo_urls: Optional[List[str]] = None


class DefectResponse(BaseModel):
    id: int
    defect_number: str
    manufacturing_order_id: Optional[int] = None
    mo_operation_id: Optional[int] = None
    inspection_result_id: Optional[int] = None
    component_id: Optional[int] = None
    component_name: Optional[str] = None
    sales_order_id: Optional[int] = None
    defect_type: DefectTypeEnum
    defect_category: str
    severity: SeverityEnum
    description: str
    location: str
    quantity_affected: int
    root_cause: Optional[str] = None
    reported_by_id: int
    reported_by_name: Optional[str] = None
    responsible_party: ResponsiblePartyEnum
    operator_id: Optional[int] = None
    operator_name: Optional[str] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    status: DefectStatusEnum
    photo_urls: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ========== NCR Schemas ==========

class NCRCreate(BaseModel):
    defect_id: Optional[int] = None
    manufacturing_order_id: Optional[int] = None
    priority: PriorityEnum = PriorityEnum.NORMAL
    description: str
    owner_id: int
    created_by_id: int


class NCRUpdate(BaseModel):
    status: Optional[NCRStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    description: Optional[str] = None
    root_cause: Optional[str] = None
    root_cause_category: Optional[str] = None
    containment_actions: Optional[str] = None
    disposition: Optional[DispositionEnum] = None
    disposition_justification: Optional[str] = None
    quantity_affected: Optional[int] = None
    rework_cost: Optional[Decimal] = None
    scrap_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None


class NCRApprove(BaseModel):
    approver_id: int
    approval_notes: Optional[str] = None


class NCRClose(BaseModel):
    closed_by_id: int
    verification_notes: Optional[str] = None


class NCRResponse(BaseModel):
    id: int
    ncr_number: str
    defect_id: Optional[int] = None
    manufacturing_order_id: Optional[int] = None
    status: NCRStatusEnum
    priority: PriorityEnum
    description: str
    root_cause: Optional[str] = None
    root_cause_category: Optional[str] = None
    containment_actions: Optional[str] = None
    disposition: Optional[DispositionEnum] = None
    disposition_justification: Optional[str] = None
    quantity_affected: int
    rework_cost: Optional[Decimal] = None
    scrap_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    owner_id: int
    owner_name: Optional[str] = None
    created_by_id: int
    created_by_name: Optional[str] = None
    approver_id: Optional[int] = None
    approver_name: Optional[str] = None
    approval_date: Optional[datetime] = None
    approval_notes: Optional[str] = None
    closed_by_id: Optional[int] = None
    closed_by_name: Optional[str] = None
    closed_date: Optional[datetime] = None
    verification_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ========== Rework Operation Schemas ==========

class ReworkOperationCreate(BaseModel):
    ncr_id: int
    manufacturing_order_id: int
    work_center_id: int
    scheduled_duration_minutes: int
    rework_description: str
    assigned_operator_id: Optional[int] = None


class ReworkOperationUpdate(BaseModel):
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    scheduled_duration_minutes: Optional[int] = None
    status: Optional[str] = None
    assigned_operator_id: Optional[int] = None
    rework_description: Optional[str] = None
    notes: Optional[str] = None
    labor_cost: Optional[Decimal] = None
    material_cost: Optional[Decimal] = None


class ReworkOperationStart(BaseModel):
    assigned_operator_id: int


class ReworkOperationComplete(BaseModel):
    actual_duration_minutes: int
    re_inspection_result_id: Optional[int] = None
    notes: Optional[str] = None


class ReworkOperationResponse(BaseModel):
    id: int
    ncr_id: int
    ncr_number: Optional[str] = None
    manufacturing_order_id: int
    work_center_id: int
    work_center_name: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    scheduled_duration_minutes: int
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    actual_duration_minutes: Optional[int] = None
    status: str
    assigned_operator_id: Optional[int] = None
    assigned_operator_name: Optional[str] = None
    rework_description: str
    notes: Optional[str] = None
    labor_cost: Optional[Decimal] = None
    material_cost: Optional[Decimal] = None
    re_inspection_result_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ========== CAPA Schemas ==========

class ActionItemSchema(BaseModel):
    id: str
    description: str
    owner_id: int
    due_date: Optional[str] = None
    status: str = "pending"
    completed_date: Optional[str] = None


class CAPACreate(BaseModel):
    ncr_id: Optional[int] = None
    defect_id: Optional[int] = None
    action_type: ActionTypeEnum
    priority: PriorityEnum = PriorityEnum.NORMAL
    problem_statement: str
    root_cause: str
    root_cause_method: Optional[str] = None
    root_cause_analysis: Optional[Dict[str, Any]] = None
    corrective_actions: Optional[List[ActionItemSchema]] = None
    preventive_actions: Optional[List[ActionItemSchema]] = None
    owner_id: int
    created_by_id: int


class CAPAUpdate(BaseModel):
    status: Optional[CAPAStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    problem_statement: Optional[str] = None
    root_cause: Optional[str] = None
    root_cause_method: Optional[str] = None
    root_cause_analysis: Optional[Dict[str, Any]] = None
    corrective_actions: Optional[List[ActionItemSchema]] = None
    preventive_actions: Optional[List[ActionItemSchema]] = None


class CAPAVerify(BaseModel):
    verified_by_id: int
    effectiveness_verification: str


class CAPAClose(BaseModel):
    closed_by_id: int


class CAPAResponse(BaseModel):
    id: int
    capa_number: str
    ncr_id: Optional[int] = None
    ncr_number: Optional[str] = None
    defect_id: Optional[int] = None
    defect_number: Optional[str] = None
    action_type: ActionTypeEnum
    status: CAPAStatusEnum
    priority: PriorityEnum
    problem_statement: str
    root_cause: str
    root_cause_method: Optional[str] = None
    root_cause_analysis: Optional[Dict[str, Any]] = None
    corrective_actions: Optional[List[Dict[str, Any]]] = None
    preventive_actions: Optional[List[Dict[str, Any]]] = None
    owner_id: int
    owner_name: Optional[str] = None
    created_by_id: int
    created_by_name: Optional[str] = None
    effectiveness_verification: Optional[str] = None
    verification_date: Optional[datetime] = None
    verified_by_id: Optional[int] = None
    verified_by_name: Optional[str] = None
    closed_date: Optional[datetime] = None
    closed_by_id: Optional[int] = None
    closed_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ========== Quality Hold Schemas ==========

class QualityHoldCreate(BaseModel):
    ncr_id: int
    hold_type: HoldTypeEnum
    component_id: Optional[int] = None
    manufacturing_order_id: Optional[int] = None
    sales_order_id: Optional[int] = None
    reason: str
    quantity_held: int = 0
    placed_by_id: int


class QualityHoldRelease(BaseModel):
    released_by_id: int
    release_reason: str


class QualityHoldResponse(BaseModel):
    id: int
    hold_number: str
    ncr_id: int
    ncr_number: Optional[str] = None
    hold_type: HoldTypeEnum
    component_id: Optional[int] = None
    component_name: Optional[str] = None
    manufacturing_order_id: Optional[int] = None
    sales_order_id: Optional[int] = None
    status: HoldStatusEnum
    reason: str
    quantity_held: int
    placed_by_id: int
    placed_by_name: Optional[str] = None
    placed_date: datetime
    released_by_id: Optional[int] = None
    released_by_name: Optional[str] = None
    released_date: Optional[datetime] = None
    release_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ========== Analytics Schemas ==========

class QualityMetricsSummary(BaseModel):
    first_pass_yield: Optional[float] = None
    defect_rate: Optional[float] = None
    inspection_pass_rate: Optional[float] = None
    rework_rate: Optional[float] = None
    scrap_rate: Optional[float] = None
    total_cost_of_quality: Optional[Decimal] = None
    open_ncrs: int = 0
    open_capas: int = 0
    overdue_ncrs: int = 0
    overdue_capas: int = 0


class DefectTrendData(BaseModel):
    period: str
    defect_count: int
    defect_rate: float
    severity_breakdown: Dict[str, int]


class ParetoItem(BaseModel):
    category: str
    count: int
    percentage: float
    cumulative_percentage: float


class OperatorQualityPerformance(BaseModel):
    operator_id: int
    operator_name: str
    total_operations: int
    defects_found: int
    defect_rate: float
    first_pass_yield: float


class SupplierQualityPerformance(BaseModel):
    supplier_id: int
    supplier_name: str
    total_receipts: int
    defects_found: int
    defect_rate: float
    failed_inspections: int


class QualityDashboard(BaseModel):
    summary: QualityMetricsSummary
    recent_defects: List[DefectResponse]
    recent_ncrs: List[NCRResponse]
    active_holds: List[QualityHoldResponse]
    overdue_items: Dict[str, Any]
