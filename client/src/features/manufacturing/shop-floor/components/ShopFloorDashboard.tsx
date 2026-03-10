/**
 * Shop Floor Dashboard Component
 * Real-time dashboard for shop floor monitoring
 */
import { useState } from 'react';
import { Card, Row, Col, Statistic, Select, Alert, Spin } from 'antd';
import {
  PlayCircleOutlined,
  CheckCircleOutlined,
  StopOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useDashboardMetrics } from '../hooks/useShopFloor';
import { useWorkCenters } from '../../work-centers/hooks/useWorkCenters';
import { WorkCenterStatusCard } from './WorkCenterStatusCard';
import { OperationQueueList } from './OperationQueueList';

export const ShopFloorDashboard = () => {
  const [selectedWorkCenter, setSelectedWorkCenter] = useState<number | undefined>();

  const { data: workCenters, isLoading: loadingWorkCenters } = useWorkCenters();
  const { data: metrics, isLoading: loadingMetrics } = useDashboardMetrics(selectedWorkCenter);

  if (loadingWorkCenters || loadingMetrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <Card>
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold">Shop Floor Dashboard</h2>
          <Select
            style={{ width: 250 }}
            placeholder="All work centers"
            allowClear
            value={selectedWorkCenter}
            onChange={setSelectedWorkCenter}
          >
            {workCenters?.map((wc) => (
              <Select.Option key={wc.id} value={wc.id}>
                {wc.name}
              </Select.Option>
            ))}
          </Select>
        </div>
      </Card>

      {/* Metrics Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="In Progress"
              value={metrics?.active_operations || 0}
              prefix={<PlayCircleOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Pending"
              value={metrics?.pending_operations || 0}
              prefix={<ClockCircleOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Completed Today"
              value={metrics?.completed_today || 0}
              prefix={<CheckCircleOutlined style={{ color: '#8c8c8c' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Blocked"
              value={metrics?.blocked_operations || 0}
              prefix={<StopOutlined style={{ color: '#ff4d4f' }} />}
              valueStyle={{ color: metrics?.blocked_operations ? '#ff4d4f' : undefined }}
            />
          </Card>
        </Col>
      </Row>

      {/* Blocked Operations Alert */}
      {metrics?.blocked_operations && metrics.blocked_operations > 0 && (
        <Alert
          message="Blocked Operations Require Attention"
          description={`There are ${metrics.blocked_operations} blocked operations that need resolution.`}
          type="error"
          showIcon
          closable
        />
      )}

      {/* Work Center Status Grid */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Work Center Status</h3>
        <Row gutter={[16, 16]}>
          {workCenters
            ?.filter((wc) => !selectedWorkCenter || wc.id === selectedWorkCenter)
            .map((wc) => (
              <Col xs={24} md={12} lg={8} key={wc.id}>
                <WorkCenterStatusCard workCenter={wc} />
              </Col>
            ))}
        </Row>
      </div>

      {/* Operation Queue */}
      {selectedWorkCenter && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Operation Queue</h3>
          <OperationQueueList workCenterId={selectedWorkCenter} />
        </div>
      )}

      {/* Auto-refresh indicator */}
      <div className="text-xs text-gray-500 text-center">
        Auto-refreshing every 30 seconds • Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

