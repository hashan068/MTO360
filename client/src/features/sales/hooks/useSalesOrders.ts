import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { App as AntdApp } from 'antd';
import type { AxiosError } from 'axios';
import { salesOrdersApi } from '@/features/sales/api';
import type {
  SalesOrder,
  SalesOrderCreatePayload,
  SalesOrderUpdatePayload,
  SalesOrderStatus,
  SalesOrderStatusUpdatePayload,
} from '@/features/sales/types';

/**
 * Query key factory for Sales Orders
 */
export const salesOrderKeys = {
  all: ['sales', 'orders'] as const,
  lists: () => [...salesOrderKeys.all, 'list'] as const,
  list: (filters?: {
    status?: SalesOrderStatus;
    date_from?: string;
    date_to?: string;
    search?: string;
  }) => [...salesOrderKeys.lists(), filters] as const,
  details: () => [...salesOrderKeys.all, 'detail'] as const,
  detail: (id: number) => [...salesOrderKeys.details(), id] as const,
};

/**
 * Hook to fetch a list of sales orders with optional filtering and search
 */
export const useSalesOrders = (params?: {
  status?: SalesOrderStatus;
  date_from?: string;
  date_to?: string;
  search?: string;
  skip?: number;
  limit?: number;
}) => {
  return useQuery<SalesOrder[], AxiosError>({
    queryKey: salesOrderKeys.list(params),
    queryFn: () => salesOrdersApi.list(params),
  });
};

/**
 * Hook to fetch a single sales order with items and references
 */
export const useSalesOrder = (
  id: number,
  options?: Omit<UseQueryOptions<SalesOrder, AxiosError>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<SalesOrder, AxiosError>({
    queryKey: salesOrderKeys.detail(id),
    queryFn: () => salesOrdersApi.retrieve(id),
    enabled: id > 0,
    ...options,
  });
};

/**
 * Hook to create a new sales order
 */
export const useCreateSalesOrder = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<SalesOrder, AxiosError, SalesOrderCreatePayload>({
    mutationFn: (payload) => salesOrdersApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesOrderKeys.lists() });
      message.success('Sales order created successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to create sales order');
    },
  });
};

/**
 * Hook to update an existing sales order
 */
export const useUpdateSalesOrder = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<SalesOrder, AxiosError, { id: number; payload: SalesOrderUpdatePayload }>({
    mutationFn: ({ id, payload }) => salesOrdersApi.update(id, payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: salesOrderKeys.lists() });
      queryClient.invalidateQueries({ queryKey: salesOrderKeys.detail(data.id) });
      message.success('Sales order updated successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to update sales order');
    },
  });
};

/**
 * Hook to update sales order status with optimistic updates
 */
export const useUpdateSalesOrderStatus = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<
    SalesOrder,
    AxiosError,
    { id: number; payload: SalesOrderStatusUpdatePayload },
    { previousSalesOrder?: SalesOrder }
  >({
    mutationFn: ({ id, payload }) => salesOrdersApi.updateStatus(id, payload),
    // Optimistic update
    onMutate: async ({ id, payload }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: salesOrderKeys.detail(id) });

      // Snapshot the previous value
      const previousSalesOrder = queryClient.getQueryData<SalesOrder>(salesOrderKeys.detail(id));

      // Optimistically update to the new value
      if (previousSalesOrder) {
        queryClient.setQueryData<SalesOrder>(salesOrderKeys.detail(id), {
          ...previousSalesOrder,
          status: payload.status,
        });
      }

      return { previousSalesOrder };
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: salesOrderKeys.lists() });
      queryClient.setQueryData(salesOrderKeys.detail(data.id), data);
      message.success('Sales order status updated successfully');
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousSalesOrder) {
        queryClient.setQueryData(salesOrderKeys.detail(variables.id), context.previousSalesOrder);
      }
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to update sales order status');
    },
  });
};

/**
 * Hook to delete a sales order
 */
export const useDeleteSalesOrder = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<void, AxiosError, number>({
    mutationFn: (id) => salesOrdersApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesOrderKeys.lists() });
      message.success('Sales order deleted successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to delete sales order');
    },
  });
};
