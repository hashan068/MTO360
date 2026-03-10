/**
 * Performance Metrics Component
 * Displays key performance indicators
 */
import { Card, Row, Col, Statistic, Empty, Spin, Progress } from 'antd';
import {
  ClockCircleOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import type { OperationPerformance } from '@/types/manufacturing';

interface PerformanceMetricsProps {
  data?: OperationPerformance[];
  isLoading?: boolean;
}

export const PerformanceMetrics = ({ data, isLoading }: PerformanceMetricsProps) => {
  if (isLoading) {
    return (
      <Card title="Operation Performance">
        <div className="flex items-center justify-center h-64">
          <Spin />
        </div>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card title="Operation Performance">
        <Empty description="No performance data available" />
      </Card>
    );
  }

  // Calculate aggregate metrics
  const totalOperations = data.reduce((sum, op) => sum + op.completed_count, 0);
  const avgAccuracy = data.reduce((sum, op) => sum + op.accuracy_pct * op.completed_count, 0) / totalOperations;
  const onTimeRate = (data.reduce((sum, op) => sum + op.on_time_count, 0) / totalOperations) * 100;
  const lateCount = data.reduce((sum, op) => sum + op.late_count, 0);

  // Top performers and need improvement
  const sortedByAccuracy = [...data].sort((a, b) => b.accuracy_pct - a.accuracy_pct);
  const topPerformers = sortedByAccuracy.slice(0, 3);
  const needImprovement = sortedByAccuracy.slice(-3).reverse();

  return (
    <Card title="Operation Performance" className="h-full">
      {/* Summary Metrics */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} lg={6}>
          <Statistic
            title="Total Operations"
            value={totalOperations}
            prefix={<CheckCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Statistic
            title="Avg Accuracy"
            value={avgAccuracy}
            suffix="%"
            precision={1}
            valueStyle={{ color: avgAccuracy >= 85 ? '#52c41a' : avgAccuracy >= 70 ? '#faad14' : '#ff4d4f' }}
            prefix={<ClockCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Statistic
            title="On-Time Rate"
            value={onTimeRate}
            suffix="%"
            precision={1}
            valueStyle={{ color: onTimeRate >= 90 ? '#52c41a' : '#faad14' }}
            prefix={<RiseOutlined />}
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Statistic
            title="Late Operations"
            value={lateCount}
            valueStyle={{ color: lateCount > 0 ? '#ff4d4f' : '#52c41a' }}
            prefix={<WarningOutlined />}
          />
        </Col>
      </Row>

      {/* Top Performers */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold mb-2">Top Performers</h4>
        <div className="space-y-2">
          {topPerformers.map((op, idx) => (
            <div key={idx} className="flex items-center justify-between">
              <span className="text-sm truncate flex-1">{op.operation_name}</span>
              <Progress
                percent={op.accuracy_pct}
                size="small"
                style={{ width: '120px' }}
                strokeColor="#52c41a"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Need Improvement */}
      <div>
        <h4 className="text-sm font-semibold mb-2">Need Improvement</h4>
        <div className="space-y-2">
          {needImprovement.map((op, idx) => (
            <div key={idx} className="flex items-center justify-between">
              <span className="text-sm truncate flex-1">{op.operation_name}</span>
              <Progress
                percent={op.accuracy_pct}
                size="small"
                style={{ width: '120px' }}
                strokeColor={op.accuracy_pct >= 70 ? '#faad14' : '#ff4d4f'}
              />
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};

