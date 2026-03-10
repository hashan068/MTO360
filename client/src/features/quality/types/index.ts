/**
 * Quality Management System - TypeScript Type Definitions
 */

// Enums
export type InspectionType = 'receiving' | 'in_process' | 'final' | 'patrol' | 'first_article';
export type InspectionResult = 'pass' | 'fail' | 'conditional';
export type DefectSeverity = 'critical' | 'major' | 'minor';
export type DefectStatus = 'open' | 'investigating' | 'resolved' | 'closed';
export type NCRStatus = 'open' | 'under_investigation' | 'under_review' | 'approved' | 'closed' | 'rejected';
export type CAPAStatus = 'open' | 'in_progress' | 'verification' | 'closed';
export type HoldStatus = 'active' | 'released' | 'cancelled';

// Inspection Point
export interface InspectionPoint {
  id: number;
  name: string;
  inspection_type: InspectionType;
  description: string | null;
  checklist: ChecklistItem[];
  created_at: string;
  updated_at: string;
}

export interface ChecklistItem {
  item: string;
  required: boolean;
  specification?: string;
}

// Inspection Result
export interface InspectionResultType {
  id: number;
  inspection_point_id: number;
  result: InspectionResult;
  inspector_id: number;
  mo_operation_id: number | null;
  manufacturing_order_id: number | null;
  inspection_date: string;
  measurements: Record<string, any> | null;
  notes: string | null;
  photo_urls: string[];
  created_at: string;
}

// Defect
export interface Defect {
  id: number;
  defect_number: string;
  defect_type: string;
  severity: DefectSeverity;
  status: DefectStatus;
  quantity_affected: number;
  description: string;
  root_cause: string | null;
  corrective_action: string | null;
  mo_operation_id: number | null;
  manufacturing_order_id: number | null;
  operator_id: number | null;
  created_at: string;
  closed_at: string | null;
}

// NCR
export interface NCR {
  id: number;
  ncr_number: string;
  status: NCRStatus;
  priority: 'low' | 'medium' | 'high' | 'critical';
  defect_id: number | null;
  manufacturing_order_id: number | null;
  owner_id: number;
  description: string;
  root_cause_analysis: string | null;
  containment_action: string | null;
  disposition: string | null;
  cost: number | null;
  created_at: string;
  closed_at: string | null;
}

// CAPA
export interface CAPA {
  id: number;
  capa_number: string;
  status: CAPAStatus;
  title: string;
  description: string;
  root_cause: string | null;
  ncr_id: number | null;
  owner_id: number;
  due_date: string | null;
  completed_at: string | null;
  verified_at: string | null;
  created_at: string;
}

export interface CAPAActionItem {
  action_id: string;
  description: string;
  responsible_id: number;
  due_date: string;
  status: 'pending' | 'in_progress' | 'completed';
  completed_at: string | null;
}

// Quality Hold
export interface QualityHold {
  id: number;
  hold_number: string;
  hold_type: string;
  status: HoldStatus;
  hold_reason: string;
  manufacturing_order_id: number | null;
  component_id: number | null;
  placed_by_id: number;
 released_by_id: number | null;
  placed_at: string;
  released_at: string | null;
}

// Quality Metrics
export interface QualityMetrics {
  first_pass_yield: number;
  defect_rate: number;
  cost_of_quality: number;
  active_ncrs: number;
  active_capas: number;
  active_holds: number;
}

export interface QualityDashboard {
  metrics: QualityMetrics;
  recent_defects: Defect[];
  overdue_ncrs: NCR[];
  active_holds: QualityHold[];
  trends: {
    date: string;
    fpy: number;
    defects: number;
  }[];
}

// Request/Response Types
export interface RecordInspectionRequest {
  inspection_point_id: number;
  result: InspectionResult;
  inspector_id: number;
  mo_operation_id?: number;
  manufacturing_order_id?: number;
  measurements?: Record<string, any>;
  notes?: string;
  photo_urls?: string[];
}

export interface CreateDefectRequest {
  defect_type: string;
  severity: DefectSeverity;
  quantity_affected: number;
  description: string;
  mo_operation_id?: number;
  manufacturing_order_id?: number;
  operator_id?: number;
}

export interface CreateNCRRequest {
  defect_id?: number;
  manufacturing_order_id?: number;
  owner_id: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}

// Quality Summary
export interface QualitySummary {
  mo_id: number;
  quality_status: string | null;
  has_quality_hold: boolean;
  hold_info: {
    hold_number: string;
    hold_reason: string;
  } | null;
  defect_count: number;
  ncr_count: number;
  can_ship: boolean;
}
