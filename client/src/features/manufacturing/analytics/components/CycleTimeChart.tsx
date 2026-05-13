/**
 * Cycle Time Chart Component
 * Visualizes cycle time trends over products
 */
import { Card, Empty, Spin } from 'antd';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { CycleTimeMetrics } from '@/types/manufacturing';

interface CycleTimeChartProps {
  data?: CycleTimeMetrics[];
  isLoading?: boolean;
}

export const CycleTimeChart = ({ data, isLoading }: CycleTimeChartProps) => {
  if (isLoading) {
    return (
      <Card title="Cycle Time Analysis">
        <div className="flex items-center justify-center h-64">
          <Spin />
        </div>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card title="Cycle Time Analysis">
        <Empty description="No cycle time data available" />
      </Card>
    );
  }

  // Transform data for chart
  const chartData = data.map((item) => ({
    product: item.product_name || `Product ${item.product_id}`,
    actual: item.avg_cycle_time_hours,
    scheduled: item.avg_scheduled_duration_hours,
    min: item.min_cycle_time_hours,
    max: item.max_cycle_time_hours,
  }));

  return (
    <Card title="Cycle Time Analysis" className="h-full">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="product" />
          <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            formatter={(value: number) => `${value.toFixed(1)}h`}
            labelStyle={{ color: '#000' }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="scheduled"
            stroke="#8884d8"
            strokeDasharray="5 5"
            name="Scheduled"
          />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#82ca9d"
            strokeWidth={2}
            name="Actual Avg"
          />
          <Line
            type="monotone"
            dataKey="min"
            stroke="#ffc658"
            strokeDasharray="3 3"
            name="Best"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="max"
            stroke="#ff7c7c"
            strokeDasharray="3 3"
            name="Worst"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Summary Table */}
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-2 py-1 text-left">Product</th>
              <th className="px-2 py-1 text-right">MOs</th>
              <th className="px-2 py-1 text-right">Avg Cycle</th>
              <th className="px-2 py-1 text-right">On-Time %</th>
              <th className="px-2 py-1 text-center">Trend</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, idx) => (
              <tr key={idx} className="border-t">
                <td className="px-2 py-1">{item.product_name || `Product ${item.product_id}`}</td>
                <td className="px-2 py-1 text-right">{item.mo_count}</td>
                <td className="px-2 py-1 text-right">{item.avg_cycle_time_hours.toFixed(1)}h</td>
                <td className="px-2 py-1 text-right">
                  <span className={item.on_time_completion_rate >= 0.9 ? 'text-green-600' : 'text-orange-600'}>
                    {(item.on_time_completion_rate * 100).toFixed(0)}%
                  </span>
                </td>
                <td className="px-2 py-1 text-center">
                  {item.trend === 'improving' && <span className="text-green-600">↓ Improving</span>}
                  {item.trend === 'degrading' && <span className="text-red-600">↑ Degrading</span>}
                  {item.trend === 'stable' && <span className="text-gray-600">→ Stable</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

