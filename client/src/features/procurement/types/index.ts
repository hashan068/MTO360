/**
 * Procurement module TypeScript types
 */

// ============================================================================
// Enums
// ============================================================================

export enum RFQStatus {
  DRAFT = 'draft',
  SENT = 'sent',
  QUOTES_RECEIVED = 'quotes_received',
  AWARDED = 'awarded',
  CANCELLED = 'cancelled',
}

export enum QuoteStatus {
  PENDING = 'pending',
  SUBMITTED = 'submitted',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
}

export enum ContractStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  EXPIRED = 'expired',
  CANCELLED = 'cancelled',
}

export enum ABCClassification {
  A = 'A',
  B = 'B',
  C = 'C',
}

// ============================================================================
// Supplier Performance
// ============================================================================

export interface SupplierPerformance {
  id: number;
  supplier_id: number;
  period: string;
  on_time_delivery_rate: number;
  quality_rating: number;
  average_lead_time_days: number;
  price_competitiveness_score: number;
  total_spend: number;
  overall_score: number;
  created_at: string;
  updated_at?: string;
}

export interface SupplierRanking {
  rank: number;
  supplier_id: number;
  supplier_name: string;
  overall_score: number;
  on_time_delivery_rate: number;
  quality_rating: number;
  total_spend: number;
  period: string;
}

// ============================================================================
// RFQ & Quotes
// ============================================================================

export interface ProcurementRFQ {
  id: number;
  rfq_number: string;
  component_id: number;
  quantity: number;
  required_by_date: string;
  closing_datetime: string;
  status: RFQStatus;
  specifications?: string;
  internal_notes?: string;
  created_by?: number;
  sent_at?: string;
  awarded_at?: string;
  created_at: string;
  updated_at?: string;
  component_name?: string;
  quotes_count?: number;
}

export interface SupplierQuote {
  id: number;
  rfq_id: number;
  supplier_id: number;
  supplier_name?: string;
  unit_price: number;
  lead_time_days: number;
  minimum_order_quantity: number;
  quote_valid_until: string;
  notes?: string;
  status: QuoteStatus;
  is_awarded: boolean;
  submitted_at?: string;
  awarded_at?: string;
  created_at: string;
  total_price?: number;
  delivery_date?: string;
}

export interface QuoteComparisonItem {
  quote_id: number;
  supplier_id: number;
  supplier_name: string;
  supplier_score?: number;
  unit_price: number;
  total_price: number;
  lead_time_days: number;
  minimum_order_quantity: number;
  delivery_date: string;
  quote_valid_until: string;
  is_best_price: boolean;
  is_best_lead_time: boolean;
}

export interface QuoteComparison {
  rfq: ProcurementRFQ;
  quotes: QuoteComparisonItem[];
  recommendation?: string;
}

// ============================================================================
// Contracts
// ============================================================================

export interface VolumeDiscountTier {
  min_qty: number;
  max_qty?: number;
  discount_pct: number;
}

export interface ContractPricing {
  id: number;
  contract_id: number;
  component_id: number;
  component_name?: string;
  unit_price: number;
  minimum_order_quantity: number;
  lead_time_days: number;
  effective_from?: string;
  effective_to?: string;
  is_active: boolean;
}

export interface SupplierContract {
  id: number;
  contract_number: string;
  supplier_id: number;
  supplier_name?: string;
  start_date: string;
  end_date: string;
  payment_terms: string;
  volume_discounts?: VolumeDiscountTier[];
  status: ContractStatus;
  auto_renew: boolean;
  renewal_notice_days: number;
  contract_file_url?: string;
  created_at: string;
  updated_at?: string;
  pricing_items_count?: number;
  days_until_expiry?: number;
}

// ============================================================================
// Inventory Optimization
// ============================================================================

export interface ComponentInventoryPolicy {
  id: number;
  component_id: number;
  component_name?: string;
  current_stock?: number;
  reorder_point: number;
  safety_stock: number;
  economic_order_quantity: number;
  abc_classification: ABCClassification;
  average_monthly_demand: number;
  lead_time_days: number;
  ordering_cost: number;
  holding_cost_pct: number;
  auto_pr_enabled: boolean;
  last_calculated_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface ComponentBelowROP {
  component_id: number;
  component_name: string;
  current_stock: number;
  reorder_point: number;
  safety_stock: number;
  recommended_order_qty: number;
  priority: 'high' | 'medium' | 'low';
  has_pending_pr: boolean;
  stock_deficit: number;
  days_until_stockout?: number;
}

export interface ABCAnalysisComponent {
  component_id: number;
  component_name: string;
  annual_usage: number;
  unit_cost: number;
  annual_value: number;
  cumulative_value: number;
  cumulative_percentage: number;
  classification: ABCClassification;
}

export interface ABCAnalysis {
  total_components: number;
  total_value: number;
  classifications: {
    A: { count: number; value: number; percentage: number };
    B: { count: number; value: number; percentage: number };
    C: { count: number; value: number; percentage: number };
  };
  components: ABCAnalysisComponent[];
}

// ============================================================================
// Cost Analysis
// ============================================================================

export interface PriceHistoryItem {
  id: number;
  effective_date: string;
  unit_price: number;
  supplier_id?: number;
  price_change_source: string;
  price_change_pct?: number;
}

export interface PriceHistory {
  component_id: number;
  component_name: string;
  history: PriceHistoryItem[];
  trend: 'increasing' | 'decreasing' | 'stable' | 'no_data';
  avg_price: number;
  min_price: number;
  max_price: number;
  price_volatility: number;
}

export interface SpendAnalysisItem {
  name: string;
  spend: number;
  percentage: number;
  order_count: number;
  avg_order_value: number;
}

export interface SpendAnalysis {
  total_spend: number;
  period_start: string;
  period_end: string;
  breakdown: SpendAnalysisItem[];
  top_10_suppliers: SpendAnalysisItem[];
  concentration: {
    top_3_pct: number;
    top_10_pct: number;
  };
}

export interface ProcurementBudget {
  id: number;
  fiscal_year: number;
  category_id?: number;
  category_name?: string;
  budgeted_amount: number;
  actual_spend: number;
  variance: number;
  variance_pct: number;
  consumed_pct?: number;
  status?: 'on_track' | 'at_risk' | 'over_budget';
  projected_annual?: number;
}

export interface BudgetTracking {
  fiscal_year: number;
  budgets: ProcurementBudget[];
  overall_total_budget: number;
  overall_total_actual: number;
  overall_consumed_pct: number;
}
