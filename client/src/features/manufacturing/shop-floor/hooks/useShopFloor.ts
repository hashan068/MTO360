/**
 * Shop Floor React Query Hooks
 * Custom hooks for shop floor operations and dashboard data
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import { manufacturingApi } from '../../api/manufacturingApi';

export const shopFloorKeys = {
  dashboard: (workCenterId?: number) => ['shopFloor', 'dashboard', workCenterId] as const,
  queue: (workCenterId: number, status?: string) => ['shopFloor', 'queue', workCenterId, status] as const,
  myAssignments: ['shopFloor', 'myAssignments'] as const,
};

/**
 * Fetch dashboard metrics
 */
export const useDashboardMetrics = (workCenterId?: number, autoRefresh = true) => {
  return useQuery({
    queryKey: shopFloorKeys.dashboard(workCenterId),
    queryFn: () => manufacturingApi.shopFloor.getDashboard(workCenterId),
    refetchInterval: autoRefresh ? 30000 : false, // Refresh every 30 seconds
    refetchOnWindowFocus: true,
  });
};

/**
 * Fetch work center queue
 */
export const useWorkCenterQueue = (workCenterId: number, status?: string) => {
  return useQuery({
    queryKey: shopFloorKeys.queue(workCenterId, status),
    queryFn: () => manufacturingApi.shopFloor.getWorkCenterQueue(workCenterId, status),
    enabled: !!workCenterId,
    refetchInterval: 15000, // Refresh every 15 seconds for queue
  });
};

/**
 * Fetch my assigned operations
 */
export const useMyAssignments = () => {
  return useQuery({
    queryKey: shopFloorKeys.myAssignments,
    queryFn: () => manufacturingApi.shopFloor.getMyAssignments(),
    refetchInterval: 15000,
  });
};

/**
 * Start operation
 */
export const useStartOperation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ operationId, operatorId }: { operationId: number; operatorId?: number }) =>
      manufacturingApi.shopFloor.startOperation(operationId, operatorId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopFloor'] });
      queryClient.invalidateQueries({ queryKey: ['scheduler'] });
      message.success('Operation started successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to start operation');
    },
  });
};

/**
 * Complete operation
 */
export const useCompleteOperation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (operationId: number) =>
      manufacturingApi.shopFloor.completeOperation(operationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopFloor'] });
      queryClient.invalidateQueries({ queryKey: ['scheduler'] });
      message.success('Operation completed successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to complete operation');
    },
  });
};

/**
 * Pause operation
 */
export const usePauseOperation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ operationId, reason }: { operationId: number; reason: string }) =>
      manufacturingApi.shopFloor.pauseOperation(operationId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopFloor'] });
      message.success('Operation paused');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to pause operation');
    },
  });
};

/**
 * Block operation
 */
export const useBlockOperation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ operationId, reason }: { operationId: number; reason: string }) =>
      manufacturingApi.shopFloor.blockOperation(operationId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopFloor'] });
      message.error('Operation blocked - requires attention');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to block operation');
    },
  });
};

/**
 * Unblock operation
 */
export const useUnblockOperation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (operationId: number) =>
      manufacturingApi.shopFloor.unblockOperation(operationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shopFloor'] });
      message.success('Operation unblocked');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to unblock operation');
    },
  });
};
