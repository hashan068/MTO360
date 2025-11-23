/**
 * Manufacturing API Types
 * TypeScript interfaces for Manufacturing module
 */

// Enums
export type OperationStatus = 
  | 'pending' 
  | 'scheduled' 
  | 'in_progress' 
  | 'completed' 
  | 'blocked'
  | 'cancelled';

export type MOStatus =
  | 'pending'
  | 'mr_sent'
  | 'mr_approved'
  | 'in_production'
  | 'completed'
  | 'blocked';

// Work Center
export interface WorkCenter {
  id: number;
  code: string;
  name: string;
  description?: string;
  capacity_hours_per_day: number;
  location?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkCenterCreate {
  code: string;
  name: string;
  description?: string;
  capacity_hours_per_day: number;
  location?: string;
  is_active?: boolean;
}

export interface WorkCenterUpdate extends Partial<WorkCenterCreate> {}

// Operation Route
export interface OperationRoute {
  id: number;
  name: string;
  product_id?: number;
  bom_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  operations?: RouteOperation[];
}

export interface RouteOperation {
  id: number;
  route_id: number;
  sequence: number;
  name: string;
  description?: string;
  work_center_id: number;
  work_center_name?: string;
  standard_time_minutes: number;
  setup_time_minutes: number;
}

export interface OperationRouteCreate {
  name: string;
  product_id?: number;
  bom_id?: number;
  is_active?: boolean;
}

export interface RouteOperationCreate {
  sequence: number;
  name: string;
  description?: string;
  work_center_id: number;
  standard_time_minutes: number;
  setup_time_minutes: number;
}

// Manufacturing Order Operation
export interface ManufacturingOrderOperation {
  id: number;
  manufacturing_order_id: number;
  route_operation_id?: number;
  sequence: number;
  name: string;
  work_center_id: number;
  status: OperationStatus;
  scheduled_start?: string;
  scheduled_end?: string;
  scheduled_duration_minutes: number;
  actual_start?: string;
  actual_end?: string;
  actual_duration_minutes?: number;
  assigned_operator_id?: number;
  notes?: string;
  blocking_reason?: string;
}

// Scheduling
export interface ScheduleSlot {
  start_datetime: string;
  end_datetime: string;
}

export interface CapacityData {
  work_center_id: number;
  work_center_name: string;
  date: string;
  capacity_minutes: number;
  scheduled_minutes: number;
  utilization_pct: number;
  status: 'underutilized' | 'optimal' | 'overallocated';
}

// Shop Floor
export interface WorkCenterQueueItem {
  operation_id: number;
  operation_name: string;
  sequence: number;
  status: OperationStatus;
  scheduled_start?: string;
  scheduled_duration_minutes: number;
  mo_id: number;
  mo_number?: string;
  product_id?: number;
  quantity?: number;
}

export interface DashboardMetrics {
  active_operations: number;
  pending_operations: number;
  blocked_operations: number;
  completed_today: number;
  avg_utilization_pct: number;
  timestamp: string;
}

// Analytics
export interface BottleneckInfo {
  work_center_id: number;
  work_center_name: string;
  avg_utilization_pct: number;
  pending_operations_count: number;
  avg_wait_time_hours: number;
  bottleneck_score: number;
  rank: number;
}

export interface OperationPerformance {
  operation_name: string;
  route_operation_id?: number;
  completed_count: number;
  avg_scheduled_minutes: number;
  avg_actual_minutes: number;
  avg_variance_minutes: number;
  accuracy_pct: number;
  on_time_count: number;
  late_count: number;
}

export interface CycleTimeMetrics {
  product_id?: number;
  product_name?: string;
  mo_count: number;
  avg_cycle_time_hours: number;
  min_cycle_time_hours: number;
  max_cycle_time_hours: number;
  avg_scheduled_duration_hours: number;
  on_time_completion_rate: number;
  trend: 'improving' | 'stable' | 'degrading';
}
