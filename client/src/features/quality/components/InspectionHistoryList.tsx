import { List, Typography } from 'antd';
import { QualityStatusBadge } from './QualityStatusBadge';
import type { InspectionResultType } from '../types';
import dayjs from 'dayjs';

interface InspectionHistoryListProps {
  inspections: InspectionResultType[];
  loading?: boolean;
}

export const InspectionHistoryList = ({ inspections, loading }: InspectionHistoryListProps) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
      <Typography.Title level={5} className="mb-4">
        Recent History
      </Typography.Title>

      <List
        loading={loading}
        dataSource={inspections || []}
        renderItem={(item) => (
          <List.Item>
            <List.Item.Meta
              title={
                <div className="flex justify-between">
                  <span>Inspection #{item.id}</span>
                  <QualityStatusBadge type="inspection" value={item.result} />
                </div>
              }
              description={
                <div className="text-xs text-gray-500 mt-1">
                  {dayjs(item.inspection_date).format('MMM D, HH:mm')}
                  {item.notes && <div className="mt-1 text-gray-600">{item.notes}</div>}
                </div>
              }
            />
          </List.Item>
        )}
      />
    </div>
  );
};

