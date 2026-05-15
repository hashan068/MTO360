/**
 * Procurement API Client
 */
import axios from 'axios';
import type {
  SupplierRanking,
  SupplierPerformance,
  ProcurementRFQ,
  SupplierQuote,
  QuoteComparison,
  SupplierContract,
  ComponentInventoryPolicy,
  ComponentBelowROP,
  ABCAnalysis,
  PriceHistory,
  SpendAnalysis,
  BudgetTracking,
  ProcurementBudget,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================================
// Phase 1: Supplier Performance
// ============================================================================

export const supplierPerformanceApi = {
  getSupplierRankings: async (limit = 10): Promise<SupplierRanking[]> => {
    const { data } = await api.get('/api/v1/procurement/suppliers/rankings', { params: { limit } });
    return data;
  },

  getSupplierPerformance: async (
    supplierId: number,
    startDate?: string,
    endDate?: string
  ): Promise<SupplierPerformance[]> => {
    const { data } = await api.get(`/api/v1/procurement/suppliers/${supplierId}/performance`, {
      params: { start_date: startDate, end_date: endDate },
    });
    return data;
  },

  calculatePerformance: async (
    supplierId: number,
    period: string
  ): Promise<SupplierPerformance> => {
    const { data } = await api.post(`/api/v1/procurement/suppliers/${supplierId}/performance/calculate`, {
      supplier_id: supplierId,
      period,
    });
    return data;
  },

  getPreferredSuppliers: async (minScore = 75): Promise<any[]> => {
    const { data } = await api.get('/api/v1/procurement/suppliers/preferred', {
      params: { min_score: minScore },
    });
    return data;
  },
};

// ============================================================================
// Phase 2: RFQ & Competitive Bidding
// ============================================================================

export const rfqApi = {
  listRFQs: async (params?: {
    status?: string;
    component_id?: number;
    limit?: number;
    offset?: number;
  }): Promise<ProcurementRFQ[]> => {
    const { data } = await api.get('/api/v1/procurement/rfqs', { params });
    return data;
  },

  getRFQ: async (rfqId: number): Promise<ProcurementRFQ> => {
    const { data } = await api.get(`/api/v1/procurement/rfqs/${rfqId}`);
    return data;
  },

  createRFQ: async (rfqData: {
    component_id: number;
    quantity: number;
    required_by_date: string;
    closing_datetime: string;
    specifications?: string;
    internal_notes?: string;
    supplier_ids: number[];
  }): Promise<ProcurementRFQ> => {
    const { data } = await api.post('/api/v1/procurement/rfqs', rfqData);
    return data;
  },

  sendRFQ: async (rfqId: number): Promise<ProcurementRFQ> => {
    const { data } = await api.post(`/api/v1/procurement/rfqs/${rfqId}/send`);
    return data;
  },

  submitQuote: async (
    rfqId: number,
    quoteData: {
      supplier_id: number;
      unit_price: number;
      lead_time_days: number;
      minimum_order_quantity: number;
      quote_valid_until: string;
      notes?: string;
    }
  ): Promise<SupplierQuote> => {
    const { data } = await api.post(`/api/v1/procurement/rfqs/${rfqId}/quotes`, quoteData);
    return data;
  },

  compareQuotes: async (rfqId: number, sortBy = 'price'): Promise<QuoteComparison> => {
    const { data } = await api.get(`/api/v1/procurement/rfqs/${rfqId}/quotes/compare`, {
      params: { sort_by: sortBy },
    });
    return data;
  },

  awardRFQ: async (rfqId: number, quoteId: number, justification: string): Promise<any> => {
    const { data } = await api.post(`/api/v1/procurement/rfqs/${rfqId}/award`, {
      quote_id: quoteId,
      justification,
    });
    return data;
  },

  cancelRFQ: async (rfqId: number, reason: string): Promise<void> => {
    await api.delete(`/api/v1/procurement/rfqs/${rfqId}`, {
      params: { reason },
    });
  },
};

// ============================================================================
// Phase 3: Contract Management
// ============================================================================

export const contractApi = {
  listContracts: async (params?: {
    supplier_id?: number;
    status?: string;
    active_only?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<SupplierContract[]> => {
    const { data } = await api.get('/api/v1/procurement/contracts', { params });
    return data;
  },

  getExpiringContracts: async (days = 90): Promise<SupplierContract[]> => {
    const { data } = await api.get('/api/v1/procurement/contracts/expiring', {
      params: { days },
    });
    return data;
  },

  createContract: async (contractData: any): Promise<SupplierContract> => {
    const { data } = await api.post('/api/v1/procurement/contracts', contractData);
    return data;
  },

  activateContract: async (contractId: number): Promise<SupplierContract> => {
    const { data } = await api.post(`/api/v1/procurement/contracts/${contractId}/activate`);
    return data;
  },

  getContractPrice: async (
    contractId: number,
    componentId: number,
    quantity: number,
    referenceDate?: string
  ): Promise<any> => {
    const { data } = await api.get(`/api/v1/procurement/contracts/${contractId}/price`, {
      params: { component_id: componentId, quantity, reference_date: referenceDate },
    });
    return data;
  },

  cancelContract: async (contractId: number, reason: string): Promise<void> => {
    await api.delete(`/api/v1/procurement/contracts/${contractId}`, {
      params: { reason },
    });
  },
};

// ============================================================================
// Phase 4: Inventory Optimization
// ============================================================================

export const inventoryOptimizationApi = {
  createPolicy: async (policyData: {
    component_id: number;
    average_monthly_demand: number;
    lead_time_days: number;
    ordering_cost?: number;
    holding_cost_pct?: number;
    auto_pr_enabled?: boolean;
  }): Promise<ComponentInventoryPolicy> => {
    const { data } = await api.post('/api/v1/procurement/inventory/policies', policyData);
    return data;
  },

  getComponentsBelowROP: async (): Promise<ComponentBelowROP[]> => {
    const { data } = await api.get('/api/v1/procurement/inventory/below-rop');
    return data;
  },

  performABCAnalysis: async (categoryId?: number): Promise<ABCAnalysis> => {
    const { data } = await api.get('/api/v1/procurement/inventory/abc-analysis', {
      params: { category_id: categoryId },
    });
    return data;
  },

  calculateROP: async (
    componentId: number,
    averageDailyDemand: number,
    leadTimeDays: number,
    serviceLevelZ = 1.65
  ): Promise<any> => {
    const { data } = await api.post('/api/v1/procurement/inventory/calculate-rop', null, {
      params: {
        component_id: componentId,
        average_daily_demand: averageDailyDemand,
        lead_time_days: leadTimeDays,
        service_level_z: serviceLevelZ,
      },
    });
    return data;
  },

  calculateEOQ: async (
    annualDemand: number,
    orderingCost: number,
    unitCost: number,
    holdingCostPct = 25
  ): Promise<any> => {
    const { data } = await api.post('/api/v1/procurement/inventory/calculate-eoq', null, {
      params: {
        annual_demand: annualDemand,
        ordering_cost: orderingCost,
        unit_cost: unitCost,
        holding_cost_pct: holdingCostPct,
      },
    });
    return data;
  },
};

// ============================================================================
// Phase 5: Cost Analysis & Reporting
// ============================================================================

export const costAnalysisApi = {
  getPriceHistory: async (
    componentId: number,
    startDate?: string,
    endDate?: string,
    supplierId?: number
  ): Promise<PriceHistory> => {
    const { data } = await api.get(`/api/v1/procurement/cost-analysis/price-history/${componentId}`, {
      params: { start_date: startDate, end_date: endDate, supplier_id: supplierId },
    });
    return data;
  },

  analyzeSpend: async (
    startDate: string,
    endDate: string,
    groupBy = 'supplier'
  ): Promise<SpendAnalysis> => {
    const { data } = await api.get('/api/v1/procurement/cost-analysis/spend-analysis', {
      params: { start_date: startDate, end_date: endDate, group_by: groupBy },
    });
    return data;
  },

  createBudget: async (budgetData: {
    fiscal_year: number;
    category_id?: number;
    budgeted_amount: number;
  }): Promise<ProcurementBudget> => {
    const { data } = await api.post('/api/v1/procurement/cost-analysis/budgets', budgetData);
    return data;
  },

  getBudgetTracking: async (fiscalYear: number): Promise<BudgetTracking> => {
    const { data } = await api.get(`/api/v1/procurement/cost-analysis/budgets/${fiscalYear}`);
    return data;
  },

  refreshBudgetActuals: async (fiscalYear: number): Promise<void> => {
    await api.post(`/api/v1/procurement/cost-analysis/budgets/${fiscalYear}/refresh`);
  },
};

export default api;
