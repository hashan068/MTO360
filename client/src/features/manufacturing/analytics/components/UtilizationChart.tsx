/**
 * Utilization Chart Component
 * Visualizes work center capacity utilization over time
 */
import { Card, Empty, Spin } from 'antd';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { CapacityData } from '@/types/manufacturing';

interface UtilizationChartProps {
  data?: CapacityData[];
  isLoading?: boolean;
}

export const UtilizationChart = ({ data, isLoading }: UtilizationChartProps) => {
  if (isLoading) {
    return (
      <Card title="Capacity Utilization">
        <div className="flex items-center justify-center h-64">
          <Spin />
        </div>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card title="Capacity Utilization">
        <Empty description="No utilization data available" />
      </Card>
    );
  }

  // Transform data for chart
  const chartData = data.map((item) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    utilization: item.utilization_pct,
    capacity: 100,
    workCenter: item.work_center_name,
  }));

  return (
    <Card title="Capacity Utilization" className="h-full">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis label={{ value: 'Utilization %', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value: number) => `${value.toFixed(1)}%`}
            labelStyle={{ color: '#000' }}
          />
          <Legend />
          <ReferenceLine y={80} stroke="red" strokeDasharray="3 3" label="Target 80%" />
          <ReferenceLine y={50} stroke="orange" strokeDasharray="3 3" label="Min 50%" />
          <Bar dataKey="utilization" fill="#1890ff" name="Utilization %" />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 text-xs text-gray-600">
        <p>• Target utilization: 50-80%</p>
        <p>• Green zone: 50-80% (optimal)</p>
        <p>• Red zone: &gt;80% (overallocated) or &lt;50% (underutilized)</p>
      </div>
    </Card>
  );
};
