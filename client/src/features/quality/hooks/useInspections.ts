import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { qualityApi } from '../api/qualityApi';
import type { RecordInspectionRequest } from '../types';

export const useInspectionPoints = () => {
  return useQuery({
    queryKey: ['inspection-points'],
    queryFn: qualityApi.getInspectionPoints,
  });
};

export const useInspectionPoint = (id: number) => {
  return useQuery({
    queryKey: ['inspection-points', id],
    queryFn: () => qualityApi.getInspectionPoint(id),
    enabled: !!id,
  });
};

export const useMyInspections = () => {
  return useQuery({
    queryKey: ['inspections', 'my-assignments'],
    queryFn: qualityApi.getMyInspections,
  });
};

export const useInspectionResults = (filters?: {
  mo_id?: number;
  operation_id?: number;
  result?: string;
}) => {
  return useQuery({
    queryKey: ['inspections', 'results', filters],
    queryFn: () => qualityApi.getInspectionResults(filters),
  });
};

export const useRecordInspection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: RecordInspectionRequest) => qualityApi.recordInspection(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inspections'] });
      queryClient.invalidateQueries({ queryKey: ['inspection-points'] });
    },
  });
};
