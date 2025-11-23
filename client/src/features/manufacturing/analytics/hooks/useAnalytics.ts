/**
 * Analytics React Query Hooks
 * Custom hooks for analytics data fetching
 */
import { useQuery } from '@tanstack/react-query';
import { manufacturingApi } from '../../api/manufacturingApi';

export const analyticsKeys = {
  utilization: (params: any) => ['analytics', 'utilization', params] as const,
  bottlenecks: (limit: number) => ['analytics', 'bottlenecks', limit] as const,
  performance: (params: any) => ['analytics', 'performance', params] as const,
  cycleTimes: (params: any) => ['analytics', 'cycleTimes', params] as const,
};

/**
 * Fetch capacity utilization data
 */
export const useUtilization = (params: {
  start_date: string;
  end_date: string;
  work_center_id?: number;
}) => {
  return useQuery({
    queryKey: analyticsKeys.utilization(params),
    queryFn: () => manufacturingApi.analytics.getUtilization(params),
    enabled: !!params.start_date && !!params.end_date,
  });
};

/**
 * Fetch bottleneck analysis
 */
export const useBottlenecks = (limit = 10) => {
  return useQuery({
    queryKey: analyticsKeys.bottlenecks(limit),
    queryFn: () => manufacturingApi.analytics.getBottlenecks(limit),
  });
};

/**
 * Fetch operation performance metrics
 */
export const useOperationPerformance = (params: {
  work_center_id?: number;
  product_id?: number;
  start_date?: string;
  end_date?: string;
}) => {
  return useQuery({
    queryKey: analyticsKeys.performance(params),
    queryFn: () => manufacturingApi.analytics.getOperationPerformance(params),
  });
};

/**
 * Fetch cycle time analysis
 */
export const useCycleTimes = (params: {
  product_id?: number;
  start_date?: string;
  end_date?: string;
}) => {
  return useQuery({
    queryKey: analyticsKeys.cycleTimes(params),
    queryFn: () => manufacturingApi.analytics.getCycleTimes(params),
  });
};
