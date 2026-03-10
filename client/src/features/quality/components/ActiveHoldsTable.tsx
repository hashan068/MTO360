import { Table, Button, Typography } from 'antd';
import { Link } from 'react-router-dom';
import { QualityStatusBadge } from './QualityStatusBadge';
import { QualityHoldBadge } from './QualityHoldBadge';
import type { QualityHold } from '../types';
import dayjs from 'dayjs';

interface ActiveHoldsTableProps {
  holds: QualityHold[];
  loading?: boolean;
}

export const ActiveHoldsTable = ({ holds, loading }: ActiveHoldsTableProps) => {
  const columns = [
    {
      title: 'Hold #',
      dataIndex: 'hold_number',
      key: 'hold_number',
      render: (text: string, record: QualityHold) => (
        <QualityHoldBadge holdNumber={text} reason={record.hold_reason} showLabel={false} />
      ),
    },
    {
      title: 'Reason',
      dataIndex: 'hold_reason',
      key: 'hold_reason',
      ellipsis: true,
    },
    {
      title: 'Type',
      dataIndex: 'hold_type',
      key: 'hold_type',
      render: (text: string) => <span className="capitalize">{text.replace('_', ' ')}</span>,
    },
    {
      title: 'Placed',
      dataIndex: 'placed_at',
      key: 'placed_at',
      render: (date: string) => dayjs(date).format('MMM D, YYYY'),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: QualityHold) => (
        <Link to={`/quality/holds/${record.id}`}>
          <Button size="small">Details</Button>
        </Link>
      ),
    },
  ];

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
      <div className="flex justify-between items-center mb-4">
        <Typography.Title level={5} style={{ margin: 0 }}>
          Active Quality Holds
        </Typography.Title>
        <Link to="/quality/holds">
          <Button type="link" size="small">View All</Button>
        </Link>
      </div>

      <Table
        columns={columns}
        dataSource={holds || []}
        rowKey="id"
        loading={loading}
        pagination={false}
        size="small"
        locale={{ emptyText: 'No active holds' }}
      />
    </div>
  );
};

