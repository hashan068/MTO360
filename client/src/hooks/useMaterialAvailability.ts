import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface MaterialValidation {
  can_schedule: boolean;
  availability?: {
    all_available: boolean;
    missing_components: Array<{
      component_name: string;
      shortage: number;
      unit: string;
    }>;
  };
  estimated_ready_date?: string;
  blocking_reason?: string;
}

export const useMaterialAvailability = (manufacturingOrderId?: number) => {
  const [validation, setValidation] = useState<MaterialValidation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchValidation = useCallback(async () => {
    if (!manufacturingOrderId) return;

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get<MaterialValidation>(
        `${API_BASE_URL}/api/material-availability/mo/${manufacturingOrderId}/validate`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setValidation(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch material availability');
      console.error('Error fetching material availability:', err);
    } finally {
      setLoading(false);
    }
  }, [manufacturingOrderId]);

  useEffect(() => {
    fetchValidation();
  }, [fetchValidation]);

  return {
    validation,
    loading,
    error,
    refetch: fetchValidation,
  };
};
