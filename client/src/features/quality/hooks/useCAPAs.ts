import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { qualityApi } from '../api/qualityApi';
import type { CAPA } from '../types';

export const useCAPAs = (filters?: {
  status?: string;
  owner_id?: number;
}) => {
  return useQuery({
    queryKey: ['capas', filters],
    queryFn: () => qualityApi.getCAPAs(filters),
  });
};

export const useCAPA = (id: number) => {
  return useQuery({
    queryKey: ['capas', id],
    queryFn: () => qualityApi.getCAPA(id),
    enabled: !!id,
  });
};

export const useCreateCAPA = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      title: string;
      description: string;
      root_cause: string;
      owner_id: number;
      ncr_id?: number;
    }) => qualityApi.createCAPA(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['capas'] });
    },
  });
};

export const useVerifyCAPA = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: { verification_notes: string; is_effective: boolean };
    }) => qualityApi.verifyCAPA(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['capas'] });
      queryClient.invalidateQueries({ queryKey: ['capas', variables.id] });
    },
  });
};

export const useCloseCAPA = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => qualityApi.closeCAPA(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['capas'] });
      queryClient.invalidateQueries({ queryKey: ['capas', id] });
    },
  });
};
