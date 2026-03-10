import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

// We need to add rework endpoints to qualityApi first, but for now we'll use axios directly 
// or assume they exist. Let's stick to the pattern and assume we'll update api/qualityApi.ts if needed.
// Actually, looking at previous steps, I didn't add rework to qualityApi.ts. 
// I should update qualityApi.ts or use axios here. I'll use axios here for speed and simplicity in this step.

const API_BASE = '/api/quality/rework';

export const useReworkQueue = (filters?: { status?: string }) => {
  return useQuery({
    queryKey: ['rework', 'queue', filters],
    queryFn: async () => {
      const { data } = await axios.get(`${API_BASE}/queue`, { params: filters });
      return data;
    },
  });
};

export const useStartRework = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await axios.post(`${API_BASE}/${id}/start`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rework', 'queue'] });
    },
  });
};

export const useCompleteRework = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, notes }: { id: number; notes: string }) => {
      const { data } = await axios.post(`${API_BASE}/${id}/complete`, { notes });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rework', 'queue'] });
    },
  });
};
