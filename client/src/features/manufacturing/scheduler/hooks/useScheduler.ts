/**
 * Scheduler React Query Hooks
 * Custom hooks for scheduler data fetching
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { message } from 'antd';
import { manufacturingApi } from '../../api/manufacturingApi';
import type { ManufacturingOrderOperation, CapacityData } from '@/types/manufacturing';

export const schedulerKeys = {
  operations: (filters?: any) => ['scheduler', 'operations', filters] as const,
  capacity: (params: any) => ['scheduler', 'capacity', params] as const,
};

/**
 * Fetch all scheduled operations
 */
export const useScheduledOperations = (params?: {
  start_date?: string;
  end_date?: string;
  work_center_id?: number;
  status?: string;
}) => {
  return useQuery({
    queryKey: schedulerKeys.operations(params),
    queryFn: async () => {
      const response = await manufacturingApi.scheduling.getOperations(params || {});
      return response;
    },
    enabled: !!params?.start_date && !!params?.end_date,
    refetchInterval: 30000, // Refresh every 30 seconds
  });
};

/**
 * Fetch capacity data for visualization
 */
export const useCapacityData = (params: {
  work_center_id?: number;
  start_date: string;
  end_date: string;
}) => {
  return useQuery({
    queryKey: schedulerKeys.capacity(params),
    queryFn: () => manufacturingApi.scheduling.getCapacity(params),
    enabled: !!params.start_date && !!params.end_date,
  });
};

/**
 * Reschedule operation (drag-and-drop)
 */
export const useRescheduleOperation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ operationId, newStart }: { operationId: number; newStart: string }) =>
      manufacturingApi.scheduling.reschedule(operationId, newStart),
    onMutate: async ({ operationId, newStart }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: schedulerKeys.operations() });

      const previousOperations = queryClient.getQueryData(schedulerKeys.operations());

      queryClient.setQueryData(schedulerKeys.operations(), (old: any) => {
        if (!old) return old;
        return old.map((op: ManufacturingOrderOperation) =>
          op.id === operationId
            ? { ...op, scheduled_start: newStart }
            : op
        );
      });

      return { previousOperations };
    },
    onError: (err, variables, context: any) => {
      // Rollback on error
      queryClient.setQueryData(schedulerKeys.operations(), context.previousOperations);
      message.error('Failed to reschedule operation');
    },
    onSuccess: () => {
      message.success('Operation rescheduled successfully');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: schedulerKeys.operations() });
      queryClient.invalidateQueries({ queryKey: schedulerKeys.capacity({}) });
    },
  });
};
