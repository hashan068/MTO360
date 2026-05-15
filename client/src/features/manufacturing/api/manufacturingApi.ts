/**
 * Manufacturing API Client
 * HTTP client for manufacturing module endpoints
 */
import axios from 'axios';
import type {
  WorkCenter,
  WorkCenterCreate,
  WorkCenterUpdate,
  OperationRoute,
  OperationRouteCreate,
  RouteOperation,
  RouteOperationCreate,
  ManufacturingOrderOperation,
  CapacityData,
  WorkCenterQueueItem,
  DashboardMetrics,
  BottleneckInfo,
  OperationPerformance,
  CycleTimeMetrics,
} from '@/types/manufacturing';

const API_BASE = import.meta.env.VITE_API_URL || '';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const manufacturingApi = {
  // Work Centers
  workCenters: {
    getAll: async (): Promise<WorkCenter[]> => {
      const { data } = await apiClient.get('/api/manufacturing/work-centers');
      return data;
    },

    getById: async (id: number): Promise<WorkCenter> => {
      const { data } = await apiClient.get(`/api/manufacturing/work-centers/${id}`);
      return data;
    },

    create: async (workCenter: WorkCenterCreate): Promise<WorkCenter> => {
      const { data } = await apiClient.post('/api/manufacturing/work-centers', workCenter);
      return data;
    },

    update: async (id: number, workCenter: WorkCenterUpdate): Promise<WorkCenter> => {
      const { data } = await apiClient.put(`/api/manufacturing/work-centers/${id}`, workCenter);
      return data;
    },

    delete: async (id: number): Promise<void> => {
      await apiClient.delete(`/api/manufacturing/work-centers/${id}`);
    },
  },

  // Operation Routes
  operationRoutes: {
    getAll: async (): Promise<OperationRoute[]> => {
      const { data } = await apiClient.get('/api/manufacturing/operation-routes');
      return data;
    },

    getById: async (id: number): Promise<OperationRoute> => {
      const { data } = await apiClient.get(`/api/manufacturing/operation-routes/${id}`);
      return data;
    },

    create: async (route: OperationRouteCreate): Promise<OperationRoute> => {
      const { data } = await apiClient.post('/api/manufacturing/operation-routes', route);
      return data;
    },

    update: async (id: number, route: Partial<OperationRouteCreate>): Promise<OperationRoute> => {
      const { data } = await apiClient.put(`/api/manufacturing/operation-routes/${id}`, route);
      return data;
    },

    delete: async (id: number): Promise<void> => {
      await apiClient.delete(`/api/manufacturing/operation-routes/${id}`);
    },

    copy: async (id: number, name: string): Promise<OperationRoute> => {
      const { data } = await apiClient.post(`/api/manufacturing/operation-routes/${id}/copy`, { name });
      return data;
    },

    // Route Operations
    getOperations: async (routeId: number): Promise<RouteOperation[]> => {
      const { data } = await apiClient.get(`/api/manufacturing/operation-routes/${routeId}/operations`);
      return data;
    },

    addOperation: async (routeId: number, operation: RouteOperationCreate): Promise<RouteOperation> => {
      const { data } = await apiClient.post(
        `/api/manufacturing/operation-routes/${routeId}/operations`,
        operation
      );
      return data;
    },

    updateOperation: async (
      routeId: number,
      operationId: number,
      operation: Partial<RouteOperationCreate>
    ): Promise<RouteOperation> => {
      const { data } = await apiClient.put(
        `/api/manufacturing/operation-routes/${routeId}/operations/${operationId}`,
        operation
      );
      return data;
    },

    deleteOperation: async (routeId: number, operationId: number): Promise<void> => {
      await apiClient.delete(`/api/manufacturing/operation-routes/${routeId}/operations/${operationId}`);
    },
  },

  // Scheduling
  scheduling: {
    getOperations: async (params: {
      start_date?: string;
      end_date?: string;
      work_center_id?: number;
      status?: string;
    }): Promise<ManufacturingOrderOperation[]> => {
      const { data } = await apiClient.get('/api/manufacturing/schedule/operations', { params });
      return data;
    },

    generateOperations: async (moId: number): Promise<ManufacturingOrderOperation[]> => {
      const { data } = await apiClient.post(`/api/manufacturing/schedule/generate-operations/${moId}`);
      return data;
    },

    autoSchedule: async (moId: number) => {
      const { data } = await apiClient.post('/api/manufacturing/schedule/auto-schedule', { mo_id: moId });
      return data;
    },

    reschedule: async (operationId: number, newStartDatetime: string) => {
      const { data } = await apiClient.post('/api/manufacturing/schedule/reschedule', {
        operation_id: operationId,
        new_start_datetime: newStartDatetime,
      });
      return data;
    },

    getCapacity: async (params: {
      work_center_id?: number;
      start_date: string;
      end_date: string;
    }): Promise<CapacityData[]> => {
      const { data } = await apiClient.get('/api/manufacturing/schedule/capacity', { params });
      return data;
    },

    getConflicts: async (params: {
      work_center_id: number;
      start_datetime: string;
      end_datetime: string;
    }) => {
      const { data } = await apiClient.get('/api/manufacturing/schedule/conflicts', { params });
      return data;
    },
  },

  // Shop Floor
  shopFloor: {
    startOperation: async (operationId: number, operatorId?: number) => {
      const { data } = await apiClient.post(`/api/manufacturing/shop-floor/operations/${operationId}/start`, {
        operator_id: operatorId,
      });
      return data;
    },

    completeOperation: async (operationId: number) => {
      const { data } = await apiClient.post(`/api/manufacturing/shop-floor/operations/${operationId}/complete`);
      return data;
    },

    pauseOperation: async (operationId: number, reason: string) => {
      const { data } = await apiClient.post(`/api/manufacturing/shop-floor/operations/${operationId}/pause`, {
        reason,
      });
      return data;
    },

    blockOperation: async (operationId: number, blockingReason: string) => {
      const { data } = await apiClient.post(`/api/manufacturing/shop-floor/operations/${operationId}/block`, {
        blocking_reason: blockingReason,
      });
      return data;
    },

    unblockOperation: async (operationId: number) => {
      const { data } = await apiClient.post(`/api/manufacturing/shop-floor/operations/${operationId}/unblock`);
      return data;
    },

    getWorkCenterQueue: async (workCenterId: number, status?: string): Promise<WorkCenterQueueItem[]> => {
      const { data } = await apiClient.get(`/api/manufacturing/shop-floor/work-centers/${workCenterId}/queue`, {
        params: { status },
      });
      return data;
    },

    getMyAssignments: async (): Promise<ManufacturingOrderOperation[]> => {
      const { data } = await apiClient.get('/api/manufacturing/shop-floor/operations/my-assignments');
      return data;
    },

    getDashboard: async (workCenterId?: number): Promise<DashboardMetrics> => {
      const { data } = await apiClient.get('/api/manufacturing/shop-floor/dashboard', {
        params: { work_center_id: workCenterId },
      });
      return data;
    },
  },

  // Analytics
  analytics: {
    getUtilization: async (params: {
      start_date: string;
      end_date: string;
      work_center_id?: number;
    }): Promise<CapacityData[]> => {
      const { data } = await apiClient.get('/api/manufacturing/analytics/capacity-utilization', { params });
      return data;
    },

    getBottlenecks: async (limit = 10): Promise<BottleneckInfo[]> => {
      const { data } = await apiClient.get('/api/manufacturing/analytics/bottlenecks', {
        params: { limit },
      });
      return data;
    },

    getOperationPerformance: async (params: {
      work_center_id?: number;
      product_id?: number;
      start_date?: string;
      end_date?: string;
    }): Promise<OperationPerformance[]> => {
      const { data } = await apiClient.get('/api/manufacturing/analytics/operation-performance', { params });
      return data;
    },

    getCycleTimes: async (params: {
      product_id?: number;
      start_date?: string;
      end_date?: string;
    }): Promise<CycleTimeMetrics[]> => {
      const { data } = await apiClient.get('/api/manufacturing/analytics/cycle-times', { params });
      return data;
    },
  },
};

export default manufacturingApi;
