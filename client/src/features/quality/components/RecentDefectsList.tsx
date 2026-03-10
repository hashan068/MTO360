import { List, Typography, Empty, Button } from 'antd';
import { Link } from 'react-router-dom';
import { QualityStatusBadge } from './QualityStatusBadge';
import type { Defect } from '../types';
import dayjs from 'dayjs';

interface RecentDefectsListProps {
  defects: Defect[];
  loading?: boolean;
}

export const RecentDefectsList = ({ defects, loading }: RecentDefectsListProps) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
      <div className="flex justify-between items-center mb-4">
        <Typography.Title level={5} style={{ margin: 0 }}>
          Recent Defects
        </Typography.Title>
        <Link to="/quality/defects">
          <Button type="link" size="small">View All</Button>
        </Link>
      </div>

      <List
        loading={loading}
        itemLayout="horizontal"
        dataSource={defects || []}
        locale={{ emptyText: <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No recent defects" /> }}
        renderItem={(defect) => (
          <List.Item>
            <List.Item.Meta
              title={
                <div className="flex justify-between items-center">
                  <Link to={`/quality/defects/${defect.id}`} className="font-medium hover:underline">
                    {defect.defect_number}
                  </Link>
                  <span className="text-xs text-gray-400">
                    {dayjs(defect.created_at).format('MMM D, HH:mm')}
                  </span>
                </div>
              }
              description={
                <div className="mt-1">
                  <div className="text-gray-600 text-sm mb-1 line-clamp-1">
                    {defect.description}
                  </div>
                  <div className="flex gap-2">
                    <QualityStatusBadge type="defect-severity" value={defect.severity} />
                    <QualityStatusBadge type="defect-status" value={defect.status} />
                  </div>
                </div>
              }
            />
          </List.Item>
        )}
      />
    </div>
  );
};

