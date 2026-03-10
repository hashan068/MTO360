/**
 * Quality Management API Client
 */
import axios from 'axios';
import type {
  InspectionPoint,
  InspectionResultType,
  Defect,
  NCR,
  CAPA,
  QualityHold,
  QualityDashboard,
  QualitySummary,
  RecordInspectionRequest,
  CreateDefectRequest,
  CreateNCRRequest,
} from '../types';

const API_BASE = '/api/quality';

export const qualityApi = {
  // ==================== Inspections ====================

  // Inspection Points
  getInspectionPoints: async (): Promise<InspectionPoint[]> => {
    const { data } = await axios.get(`${API_BASE}/inspections/points`);
    return data;
  },

  getInspectionPoint: async (id: number): Promise<InspectionPoint> => {
    const { data } = await axios.get(`${API_BASE}/inspections/points/${id}`);
    return data;
  },

  // Inspection Results
  getMyInspections: async (): Promise<InspectionResultType[]> => {
    const { data } = await axios.get(`${API_BASE}/inspections/my-assignments`);
    return data;
  },

  recordInspection: async (request: RecordInspectionRequest): Promise<InspectionResultType> => {
    const { data } = await axios.post(`${API_BASE}/inspections/results`, request);
    return data;
  },

  getInspectionResults: async (filters?: {
    mo_id?: number;
    operation_id?: number;
    result?: string;
  }): Promise<InspectionResultType[]> => {
    const { data } = await axios.get(`${API_BASE}/inspections/results`, { params: filters });
    return data;
  },

  // ==================== Defects ====================

  getDefects: async (filters?: {
    severity?: string;
    status?: string;
    search?: string;
    mo_id?: number;
  }): Promise<Defect[]> => {
    const { data } = await axios.get(`${API_BASE}/defects/search`, { params: filters });
    return data;
  },

  getDefect: async (id: number): Promise<Defect> => {
    const { data } = await axios.get(`${API_BASE}/defects/${id}`);
    return data;
  },

  createDefect: async (request: CreateDefectRequest): Promise<Defect> => {
    const { data } = await axios.post(`${API_BASE}/defects`, request);
    return data;
  },

  closeDefect: async (id: number, resolution: string): Promise<Defect> => {
    const { data } = await axios.post(`${API_BASE}/defects/${id}/close`, { resolution });
    return data;
  },

  // Shop floor quick defect reporting
  reportShopFloorDefect: async (
    moOperationId: number,
    defectType: string,
    severity: string,
    quantityAffected: number,
    description: string,
    createNcr: boolean = false
  ): Promise<Defect> => {
    const { data } = await axios.post(`/api/shop-floor/quality/defects`, {
      mo_operation_id: moOperationId,
      defect_type: defectType,
      severity,
      quantity_affected: quantityAffected,
      description,
      create_ncr: createNcr,
    });
    return data;
  },

  // ==================== NCRs ====================

  getNCRs: async (filters?: {
    status?: string;
    priority?: string;
    owner_id?: number;
  }): Promise<NCR[]> => {
    const { data } = await axios.get(`${API_BASE}/ncrs/search`, { params: filters });
    return data;
  },

  getNCR: async (id: number): Promise<NCR> => {
    const { data } = await axios.get(`${API_BASE}/ncrs/${id}`);
    return data;
  },

  createNCR: async (request: CreateNCRRequest): Promise<NCR> => {
    const { data } = await axios.post(`${API_BASE}/ncrs`, request);
    return data;
  },

  startInvestigation: async (id: number, data: {
    root_cause_analysis: string;
    containment_action: string;
  }): Promise<NCR> => {
    const { data: response } = await axios.post(`${API_BASE}/ncrs/${id}/start-investigation`, data);
    return response;
  },

  approveNCR: async (id: number, data: {
    disposition: string;
    cost?: number;
  }): Promise<NCR> => {
    const { data: response } = await axios.post(`${API_BASE}/ncrs/${id}/approve`, data);
    return response;
  },

  closeNCR: async (id: number): Promise<NCR> => {
    const { data } = await axios.post(`${API_BASE}/ncrs/${id}/close`);
    return data;
  },

  getOverdueNCRs: async (): Promise<NCR[]> => {
    const { data } = await axios.get(`${API_BASE}/ncrs/overdue`);
    return data;
  },

  // ==================== CAPAs ====================

  getCAPAs: async (filters?: {
    status?: string;
    owner_id?: number;
  }): Promise<CAPA[]> => {
    const { data } = await axios.get(`${API_BASE}/capas/search`, { params: filters });
    return data;
  },

  getCAPA: async (id: number): Promise<CAPA> => {
    const { data } = await axios.get(`${API_BASE}/capas/${id}`);
    return data;
  },

  createCAPA: async (data: {
    title: string;
    description: string;
    root_cause: string;
    owner_id: number;
    ncr_id?: number;
  }): Promise<CAPA> => {
    const { data: response } = await axios.post(`${API_BASE}/capas`, data);
    return response;
  },

  verifyCAPA: async (id: number, data: {
    verification_notes: string;
    is_effective: boolean;
  }): Promise<CAPA> => {
    const { data: response } = await axios.post(`${API_BASE}/capas/${id}/verify`, data);
    return response;
  },

  closeCAPA: async (id: number): Promise<CAPA> => {
    const { data } = await axios.post(`${API_BASE}/capas/${id}/close`);
    return data;
  },

  // ==================== Quality Holds ====================

  getQualityHolds: async (filters?: {
    status?: string;
    mo_id?: number;
  }): Promise<QualityHold[]> => {
    const { data } = await axios.get(`${API_BASE}/holds`, { params: filters });
    return data;
  },

  getActiveHolds: async (): Promise<QualityHold[]> => {
    const { data } = await axios.get(`${API_BASE}/holds/active`);
    return data;
  },

  placeHold: async (data: {
    hold_type: string;
    manufacturing_order_id?: number;
    component_id?: number;
    hold_reason: string;
  }): Promise<QualityHold> => {
    const { data: response } = await axios.post(`${API_BASE}/holds`, data);
    return response;
  },

  releaseHold: async (id: number, releaseNotes: string): Promise<QualityHold> => {
    const { data } = await axios.post(`${API_BASE}/holds/${id}/release`, {
      release_notes: releaseNotes,
    });
    return data;
  },

  // ==================== Analytics ====================

  getDashboard: async (daysBack: number = 30): Promise<QualityDashboard> => {
    const { data } = await axios.get(`${API_BASE}/analytics/dashboard`, {
      params: { days_back: daysBack },
    });
    return data;
  },

  getFirstPassYield: async (daysBack: number = 30): Promise<number> => {
    const { data } = await axios.get(`${API_BASE}/analytics/first-pass-yield`, {
      params: { days_back: daysBack },
    });
    return data;
  },

  // ==================== Quality Summaries ====================

  getOperationQualitySummary: async (operationId: number) => {
    const { data } = await axios.get(`/api/shop-floor/quality/operations/${operationId}/quality-summary`);
    return data;
  },

  getMOQualitySummary: async (moId: number): Promise<QualitySummary> => {
    const { data } = await axios.get(`/api/shop-floor/quality/manufacturing-orders/${moId}/quality-summary`);
    return data;
  },
};
