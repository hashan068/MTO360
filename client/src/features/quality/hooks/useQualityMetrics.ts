import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { qualityApi } from '../api/qualityApi';

export const useQualityDashboard = (daysBack: number = 30) => {
  return useQuery({
    queryKey: ['quality', 'dashboard', daysBack],
    queryFn: () => qualityApi.getDashboard(daysBack),
  });
};

export const useFirstPassYield = (daysBack: number = 30) => {
  return useQuery({
    queryKey: ['quality', 'fpy', daysBack],
    queryFn: () => qualityApi.getFirstPassYield(daysBack),
  });
};

export const useActiveHolds = () => {
  return useQuery({
    queryKey: ['quality', 'holds', 'active'],
    queryFn: qualityApi.getActiveHolds,
  });
};

export const useQualityHolds = (filters?: { status?: string; mo_id?: number }) => {
  return useQuery({
    queryKey: ['quality', 'holds', filters],
    queryFn: () => qualityApi.getQualityHolds(filters),
  });
};

export const usePlaceHold = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      hold_type: string;
      manufacturing_order_id?: number;
      component_id?: number;
      hold_reason: string;
    }) => qualityApi.placeHold(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quality', 'holds'] });
      queryClient.invalidateQueries({ queryKey: ['quality', 'dashboard'] });
    },
  });
};

export const useReleaseHold = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, releaseNotes }: { id: number; releaseNotes: string }) =>
      qualityApi.releaseHold(id, releaseNotes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quality', 'holds'] });
      queryClient.invalidateQueries({ queryKey: ['quality', 'dashboard'] });
    },
  });
};
