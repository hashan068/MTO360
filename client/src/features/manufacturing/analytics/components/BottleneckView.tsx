/**
 * Bottleneck View Component
 * Displays bottleneck analysis with ranking
 */
import { Card, Table, Tag, Empty, Spin, Progress } from 'antd';
import { WarningOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { BottleneckInfo } from '@/types/manufacturing';

interface BottleneckViewProps {
  data?: BottleneckInfo[];
  isLoading?: boolean;
}

export const BottleneckView = ({ data, isLoading }: BottleneckViewProps) => {
  if (isLoading) {
    return (
      <Card title="Bottleneck Analysis">
        <div className="flex items-center justify-center h-64">
          <Spin />
        </div>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card title="Bottleneck Analysis">
        <Empty description="No bottleneck data available" />
      </Card>
    );
  }

  const columns: ColumnsType<BottleneckInfo> = [
    {
      title: 'Rank',
      dataIndex: 'rank',
      key: 'rank',
      width: 60,
      align: 'center',
      render: (rank: number) => (
        <Tag color={rank === 1 ? 'red' : rank <= 3 ? 'orange' : 'default'}>
          #{rank}
        </Tag>
      ),
    },
    {
      title: 'Work Center',
      dataIndex: 'work_center_name',
      key: 'work_center',
      ellipsis: true,
    },
    {
      title: 'Utilization',
      dataIndex: 'avg_utilization_pct',
      key: 'utilization',
      width: 180,
      render: (pct: number) => (
        <Progress
          percent={pct}
          size="small"
          strokeColor={pct > 85 ? '#ff4d4f' : pct > 70 ? '#faad14' : '#52c41a'}
        />
      ),
      sorter: (a, b) => a.avg_utilization_pct - b.avg_utilization_pct,
    },
    {
      title: 'Pending Ops',
      dataIndex: 'pending_operations_count',
      key: 'pending',
      width: 100,
      align: 'right',
      render: (count: number) => (
        <span className={count > 10 ? 'text-red-500 font-semibold' : ''}>
          {count}
        </span>
      ),
      sorter: (a, b) => a.pending_operations_count - b.pending_operations_count,
    },
    {
      title: 'Avg Wait Time',
      dataIndex: 'avg_wait_time_hours',
      key: 'wait_time',
      width: 120,
      align: 'right',
      render: (hours: number) => `${hours.toFixed(1)}h`,
      sorter: (a, b) => a.avg_wait_time_hours - b.avg_wait_time_hours,
    },
    {
      title: 'Bottleneck Score',
      dataIndex: 'bottleneck_score',
      key: 'score',
      width: 120,
      align: 'right',
      render: (score: number) => (
        <span className={score > 75 ? 'text-red-500 font-semibold' : score > 50 ? 'text-orange-500' : ''}>
          {score.toFixed(1)}
        </span>
      ),
      sorter: (a, b) => a.bottleneck_score - b.bottleneck_score,
      defaultSortOrder: 'descend',
    },
  ];

  // Top 3 bottlenecks summary
  const top3 = data.slice(0, 3);

  return (
    <Card
      title={
        <div className="flex items-center gap-2">
          <WarningOutlined style={{ color: '#ff4d4f' }} />
          <span>Bottleneck Analysis</span>
        </div>
      }
      className="h-full"
    >
      {/* Alert for top bottlenecks */}
      {top3.length > 0 && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
          <div className="text-sm font-semibold text-red-800 mb-2">
            Top Bottlenecks Requiring Attention:
          </div>
          <ul className="text-sm text-red-700 space-y-1">
            {top3.map((item) => (
              <li key={item.work_center_id}>
                <strong>{item.work_center_name}</strong>: {item.pending_operations_count} pending ops,
                {' '}{item.avg_utilization_pct.toFixed(0)}% utilization
              </li>
            ))}
          </ul>
        </div>
      )}

      <Table
        columns={columns}
        dataSource={data || []}
        rowKey="work_center_id"
        pagination={{ pageSize: 10 }}
        size="small"
      />

      <div className="mt-4 text-xs text-gray-600">
        <p><strong>Bottleneck Score</strong> = (Utilization × 0.4) + (Pending Ops × 0.3) + (Wait Time × 0.3)</p>
        <p>• Score &gt; 75: Critical bottleneck</p>
        <p>• Score 50-75: Moderate bottleneck</p>
        <p>• Score &lt; 50: Normal operation</p>
      </div>
    </Card>
  );
};


