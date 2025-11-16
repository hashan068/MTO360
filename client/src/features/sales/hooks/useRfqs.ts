import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { App as AntdApp } from 'antd';
import type { AxiosError } from 'axios';
import { rfqsApi } from '@/features/sales/api';
import type {
  RFQ,
  RFQCreatePayload,
  RFQUpdatePayload,
  RFQStatus,
  ConvertRFQToQuotationRequest,
  Quotation,
  QuotationSummary,
} from '@/features/sales/types';

/**
 * Query key factory for RFQs
 */
export const rfqKeys = {
  all: ['sales', 'rfqs'] as const,
  lists: () => [...rfqKeys.all, 'list'] as const,
  list: (filters?: { status?: RFQStatus; search?: string }) => [...rfqKeys.lists(), filters] as const,
  details: () => [...rfqKeys.all, 'detail'] as const,
  detail: (id: number) => [...rfqKeys.details(), id] as const,
  quotations: (id: number) => [...rfqKeys.detail(id), 'quotations'] as const,
};

/**
 * Hook to fetch a list of RFQs with optional filtering and search
 */
export const useRfqs = (params?: {
  status?: RFQStatus;
  search?: string;
  skip?: number;
  limit?: number;
}) => {
  return useQuery<RFQ[], AxiosError>({
    queryKey: rfqKeys.list(params),
    queryFn: () => rfqsApi.list(params),
  });
};

/**
 * Hook to fetch a single RFQ with items and quotations
 */
export const useRfq = (
  id: number,
  options?: Omit<UseQueryOptions<RFQ, AxiosError>, 'queryKey' | 'queryFn'>
) => {
  return useQuery<RFQ, AxiosError>({
    queryKey: rfqKeys.detail(id),
    queryFn: () => rfqsApi.retrieve(id),
    enabled: id > 0,
    ...options,
  });
};

/**
 * Hook to fetch quotations created from a specific RFQ
 */
export const useRfqQuotations = (rfqId: number) => {
  return useQuery<QuotationSummary[], AxiosError>({
    queryKey: rfqKeys.quotations(rfqId),
    queryFn: () => rfqsApi.getQuotations(rfqId),
    enabled: rfqId > 0,
  });
};

/**
 * Hook to create a new RFQ
 */
export const useCreateRfq = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<RFQ, AxiosError, RFQCreatePayload>({
    mutationFn: (payload) => rfqsApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: rfqKeys.lists() });
      message.success('RFQ created successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to create RFQ');
    },
  });
};

/**
 * Hook to update an existing RFQ
 */
export const useUpdateRfq = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<RFQ, AxiosError, { id: number; payload: RFQUpdatePayload }>({
    mutationFn: ({ id, payload }) => rfqsApi.update(id, payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: rfqKeys.lists() });
      queryClient.invalidateQueries({ queryKey: rfqKeys.detail(data.id) });
      message.success('RFQ updated successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to update RFQ');
    },
  });
};

/**
 * Hook to delete an RFQ
 */
export const useDeleteRfq = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<void, AxiosError, number>({
    mutationFn: (id) => rfqsApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: rfqKeys.lists() });
      message.success('RFQ deleted successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to delete RFQ');
    },
  });
};

/**
 * Hook to convert an RFQ to a Quotation
 */
export const useConvertRfqToQuotation = () => {
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  return useMutation<Quotation, AxiosError, { rfqId: number; payload: ConvertRFQToQuotationRequest }>({
    mutationFn: ({ rfqId, payload }) => rfqsApi.convertToQuotation(rfqId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: rfqKeys.detail(variables.rfqId) });
      queryClient.invalidateQueries({ queryKey: rfqKeys.quotations(variables.rfqId) });
      queryClient.invalidateQueries({ queryKey: ['sales', 'quotations', 'list'] });
      message.success('RFQ converted to quotation successfully');
    },
    onError: (error) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Failed to convert RFQ to quotation');
    },
  });
};
