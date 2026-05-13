/**
 * Work Center React Query Hooks
 * Custom hooks for work center data fetching and mutations
 */
import { useQuery, useMutation, useQueryClient, type UseQueryResult } from '@tanstack/react-query';
import { message } from 'antd';
import { manufacturingApi } from '../../api/manufacturingApi';
import type { WorkCenter, WorkCenterCreate, WorkCenterUpdate } from '@/types/manufacturing';

// Query Keys
export const workCenterKeys = {
  all: ['workCenters'] as const,
  detail: (id: number) => ['workCenters', id] as const,
};

/**
 * Fetch all work centers
 */
export const useWorkCenters = (): UseQueryResult<WorkCenter[], Error> => {
  return useQuery({
    queryKey: workCenterKeys.all,
    queryFn: () => manufacturingApi.workCenters.getAll(),
  });
};

/**
 * Fetch single work center by ID
 */
export const useWorkCenter = (id: number): UseQueryResult<WorkCenter, Error> => {
  return useQuery({
    queryKey: workCenterKeys.detail(id),
    queryFn: () => manufacturingApi.workCenters.getById(id),
    enabled: !!id,
  });
};

/**
 * Create new work center
 */
export const useCreateWorkCenter = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: WorkCenterCreate) => manufacturingApi.workCenters.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workCenterKeys.all });
      message.success('Work center created successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to create work center');
    },
  });
};

/**
 * Update existing work center
 */
export const useUpdateWorkCenter = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: WorkCenterUpdate }) =>
      manufacturingApi.workCenters.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: workCenterKeys.all });
      queryClient.invalidateQueries({ queryKey: workCenterKeys.detail(variables.id) });
      message.success('Work center updated successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to update work center');
    },
  });
};

/**
 * Delete work center
 */
export const useDeleteWorkCenter = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => manufacturingApi.workCenters.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: workCenterKeys.all });
      message.success('Work center deleted successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to delete work center');
    },
  });
};
