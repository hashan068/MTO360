import { Card, Button, List, Typography, Empty } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import type { InspectionPoint } from '../types';

interface InspectionQueueCardProps {
  pendingInspections: any[]; // TODO: Define PendingInspection type
  onInspect: (id: number) => void;
  loading?: boolean;
}

export const InspectionQueueCard = ({ pendingInspections, onInspect, loading }: InspectionQueueCardProps) => {
  return (
    <Card
      title="Pending Inspections"
      className="h-full"
      extra={<span className="text-gray-400">{pendingInspections?.length || 0} pending</span>}
    >
      <List
        loading={loading}
        dataSource={pendingInspections || []}
        locale={{ emptyText: <Empty description="No pending inspections" /> }}
        renderItem={(item) => (
          <List.Item
            actions={[
              <Button
                type="primary"
                size="small"
                icon={<PlayCircleOutlined />}
                onClick={() => onInspect(item.id)}
              >
                Inspect
              </Button>
            ]}
          >
            <List.Item.Meta
              title={`MO #${item.mo_id} - Op ${item.op_sequence}`}
              description={item.inspection_point_name}
            />
          </List.Item>
        )}
      />
    </Card>
  );
};

