import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { App as AntdApp } from 'antd';
import type { AxiosError } from 'axios';
import { quotationsApi } from '@/features/sales/api';
import type {
  Quotation,
  QuotationCreatePayload,
  QuotationUpdatePayload,
  QuotationStatus,
  QuotationStatusUpdatePayload,
  SalesOrder,
} from '@/features/sales/types';

/**
 * Query key factory for Quotations
 */
export const quotationKeys = {
  all: ['sales', 'quotations'] as const,
  lists: () => [...quotationKeys.all, 'list'] as const,
  list: (filters?: { status?: QuotationStatus; search?: string }) => [...quotationKeys.lists(), filters] as const,
  details: () => [...quotationKeys.all, 'detail'] as const,
  detail: (id: number) => [...quotationKeys.details(), id] as const,
};

/**
 * Hook to fetch a list of quotations with optional filtering and search
 */
export const useQuotations = (params?: {
  status?: QuotationStatus;
  search?: string;
  skip?: number;
  limit?: number;
}) => {
  return useQuery<Quotation[], AxiosError>({
    queryKey: quotationKeys.list(params),
    queryFn: () => quotationsApi.list(params),
  });
};

/**
 * Hook to fetch a single quotation with items and references
 */
export const useQuotation = (
  id: number,
  options?: Omit<UseQueryOptions<Quotation, AxiosError>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<Quotation, AxiosError>({
    queryKey: quotationKeys.detail(id),
    queryFn: () => quotationsApi.retrieve(id),
    enabled: id > 0,
    ...options,
  });
};

/**
 * Hook to create a new quotation
 */
export const useCreateQuotation = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<Quotation, AxiosError, QuotationCreatePayload>({
    mutationFn: (payload) => quotationsApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: quotationKeys.lists() });
      message.success('Quotation created successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to create quotation');
    },
  });
};

/**
 * Hook to update an existing quotation
 */
export const useUpdateQuotation = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<Quotation, AxiosError, { id: number; payload: QuotationUpdatePayload }>({
    mutationFn: ({ id, payload }) => quotationsApi.update(id, payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: quotationKeys.lists() });
      queryClient.invalidateQueries({ queryKey: quotationKeys.detail(data.id) });
      message.success('Quotation updated successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to update quotation');
    },
  });
};

/**
 * Hook to update quotation status with optimistic updates
 */
export const useUpdateQuotationStatus = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<
    Quotation,
    AxiosError,
    { id: number; payload: QuotationStatusUpdatePayload },
    { previousQuotation?: Quotation }
  >({
    mutationFn: ({ id, payload }) => quotationsApi.updateStatus(id, payload),
    // Optimistic update
    onMutate: async ({ id, payload }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: quotationKeys.detail(id) });

      // Snapshot the previous value
      const previousQuotation = queryClient.getQueryData<Quotation>(quotationKeys.detail(id));

      // Optimistically update to the new value
      if (previousQuotation) {
        queryClient.setQueryData<Quotation>(quotationKeys.detail(id), {
          ...previousQuotation,
          status: payload.status,
        });
      }

      return { previousQuotation };
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: quotationKeys.lists() });
      queryClient.setQueryData(quotationKeys.detail(data.id), data);
      message.success('Quotation status updated successfully');
    },
    onError: (error, variables, context) => {
      // Rollback on error
      if (context?.previousQuotation) {
        queryClient.setQueryData(quotationKeys.detail(variables.id), context.previousQuotation);
      }
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to update quotation status');
    },
  });
};

/**
 * Hook to delete a quotation
 */
export const useDeleteQuotation = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<void, AxiosError, number>({
    mutationFn: (id) => quotationsApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: quotationKeys.lists() });
      message.success('Quotation deleted successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to delete quotation');
    },
  });
};

/**
 * Hook to convert a quotation to a sales order
 */
export const useConvertQuotationToSalesOrder = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<SalesOrder, AxiosError, number>({
    mutationFn: (quotationId) => quotationsApi.convertToSalesOrder(quotationId),
    onSuccess: (_, quotationId) => {
      queryClient.invalidateQueries({ queryKey: quotationKeys.detail(quotationId) });
      queryClient.invalidateQueries({ queryKey: ['sales', 'orders', 'list'] });
      message.success('Quotation converted to sales order successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to convert quotation to sales order');
    },
  });
};
