import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { qualityApi } from '../api/qualityApi';
import type { CreateDefectRequest } from '../types';

export const useDefects = (filters?: {
  severity?: string;
  status?: string;
  search?: string;
  mo_id?: number;
}) => {
  return useQuery({
    queryKey: ['defects', filters],
    queryFn: () => qualityApi.getDefects(filters),
  });
};

export const useDefect = (id: number) => {
  return useQuery({
    queryKey: ['defects', id],
    queryFn: () => qualityApi.getDefect(id),
    enabled: !!id,
  });
};

export const useCreateDefect = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateDefectRequest) => qualityApi.createDefect(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['defects'] });
    },
  });
};

export const useCloseDefect = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, resolution }: { id: number; resolution: string }) =>
      qualityApi.closeDefect(id, resolution),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['defects'] });
    },
  });
};

export const useReportShopFloorDefect = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      moOperationId: number;
      defectType: string;
      severity: string;
      quantityAffected: number;
      description: string;
      createNcr?: boolean;
    }) =>
      qualityApi.reportShopFloorDefect(
        data.moOperationId,
        data.defectType,
        data.severity,
        data.quantityAffected,
        data.description,
        data.createNcr
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['defects'] });
      queryClient.invalidateQueries({ queryKey: ['ncrs'] });
    },
  });
};
