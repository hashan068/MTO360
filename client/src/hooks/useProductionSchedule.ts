import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export interface ManufacturingOrderInfo {
  mo_id: number;
  mo_number: string;
  product_id?: number;
  quantity: number;
  status: string;
  scheduled_start?: string;
  scheduled_end?: string;
  production_start_at?: string;
  end_at?: string;
  total_scheduled_duration_minutes?: number;
}

export interface ProductionSchedule {
  sales_order_id: number;
  has_production: boolean;
  manufacturing_orders: ManufacturingOrderInfo[];
  overall_status: string;
  estimated_delivery_date?: string;
  total_mos: number;
}

export const useProductionSchedule = (salesOrderId?: number) => {
  const [schedule, setSchedule] = useState<ProductionSchedule | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSchedule = useCallback(async () => {
    if (!salesOrderId) return;

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get<ProductionSchedule>(
        `${API_BASE_URL}/api/production-integration/sales-orders/${salesOrderId}/production-schedule`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setSchedule(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch production schedule');
      console.error('Error fetching production schedule:', err);
    } finally {
      setLoading(false);
    }
  }, [salesOrderId]);

  useEffect(() => {
    fetchSchedule();
  }, [fetchSchedule]);

  return {
    schedule,
    loading,
    error,
    refetch: fetchSchedule,
  };
};
