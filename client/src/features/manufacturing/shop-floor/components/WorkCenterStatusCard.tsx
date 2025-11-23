/**
 * Work Center Status Card Component
 * Shows status and queue for a single work center
 */
import { Card, Tag, Progress, Space } from 'antd';
import { useWorkCenterQueue } from '../hooks/useShopFloor';
import type { WorkCenter } from '@/types/manufacturing';

interface WorkCenterStatusCardProps {
  workCenter: WorkCenter;
}

export const WorkCenterStatusCard = ({ workCenter }: WorkCenterStatusCardProps) => {
  const { data: queue } = useWorkCenterQueue(workCenter.id);

  const inProgressCount = queue?.filter((op) => op.status === 'in_progress').length || 0;
  const pendingCount = queue?.filter((op) => op.status === 'pending' || op.status === 'scheduled').length || 0;
  const blockedCount = queue?.filter((op) => op.status === 'blocked').length || 0;

  const currentOperation = queue?.find((op) => op.status === 'in_progress');

  const getStatusInfo = () => {
    if (blockedCount > 0) {
      return { status: 'Blocked', color: 'error', desc: `${blockedCount} blocked` };
    }
    if (inProgressCount > 0) {
      return { status: 'Busy', color: 'processing', desc: currentOperation?.operation_name || 'In progress' };
    }
    if (pendingCount > 0) {
      return { status: 'Idle', color: 'default', desc: `${pendingCount} queued` };
    }
    return { status: 'Idle', color: 'default', desc: 'No operations' };
  };

  const statusInfo = getStatusInfo();

  // Calculate utilization (simplified mock)
  const utilization = inProgressCount > 0 ? 75 : pendingCount > 0 ? 45 : 0;

  return (
    <Card
      size="small"
      title={
        <div className="flex items-center justify-between">
          <span className="font-medium truncate">{workCenter.name}</span>
          <Tag color={statusInfo.color}>{statusInfo.status}</Tag>
        </div>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        <div>
          <div className="text-xs text-gray-500 mb-1">Current Operation</div>
          <div className="text-sm truncate">{statusInfo.desc}</div>
        </div>

        <div>
          <div className="text-xs text-gray-500 mb-1">Queue</div>
          <Space size="small">
            {inProgressCount > 0 && (
              <Tag color="green">{inProgressCount} active</Tag>
            )}
            {pendingCount > 0 && (
              <Tag color="blue">{pendingCount} pending</Tag>
            )}
            {blockedCount > 0 && (
              <Tag color="red">{blockedCount} blocked</Tag>
            )}
            {!inProgressCount && !pendingCount && !blockedCount && (
              <Tag>Empty</Tag>
            )}
          </Space>
        </div>

        <div>
          <div className="text-xs text-gray-500 mb-1">Utilization</div>
          <Progress
            percent={utilization}
            size="small"
            status={utilization > 80 ? 'exception' : utilization > 50 ? 'active' : 'normal'}
          />
        </div>
      </Space>
    </Card>
  );
};
