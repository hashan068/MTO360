import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { qualityApi } from '../api/qualityApi';
import type { CreateNCRRequest } from '../types';

export const useNCRs = (filters?: {
  status?: string;
  priority?: string;
  owner_id?: number;
}) => {
  return useQuery({
    queryKey: ['ncrs', filters],
    queryFn: () => qualityApi.getNCRs(filters),
  });
};

export const useNCR = (id: number) => {
  return useQuery({
    queryKey: ['ncrs', id],
    queryFn: () => qualityApi.getNCR(id),
    enabled: !!id,
  });
};

export const useOverdueNCRs = () => {
  return useQuery({
    queryKey: ['ncrs', 'overdue'],
    queryFn: qualityApi.getOverdueNCRs,
  });
};

export const useCreateNCR = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateNCRRequest) => qualityApi.createNCR(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ncrs'] });
    },
  });
};

export const useStartInvestigation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: { root_cause_analysis: string; containment_action: string };
    }) => qualityApi.startInvestigation(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ncrs'] });
      queryClient.invalidateQueries({ queryKey: ['ncrs', variables.id] });
    },
  });
};

export const useApproveNCR = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: { disposition: string; cost?: number };
    }) => qualityApi.approveNCR(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ncrs'] });
      queryClient.invalidateQueries({ queryKey: ['ncrs', variables.id] });
    },
  });
};

export const useCloseNCR = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => qualityApi.closeNCR(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['ncrs'] });
      queryClient.invalidateQueries({ queryKey: ['ncrs', id] });
    },
  });
};
