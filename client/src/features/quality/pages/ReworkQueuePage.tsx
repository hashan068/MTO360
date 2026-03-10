import { Table, Button, Typography, Tag, Space, message } from 'antd';
import { PlayCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useReworkQueue, useStartRework, useCompleteRework } from '../hooks/useRework';
import dayjs from 'dayjs';

const ReworkQueuePage = () => {
  const { data: reworkOps, isLoading } = useReworkQueue();
  const startRework = useStartRework();
  const completeRework = useCompleteRework();

  const handleStart = async (id: number) => {
    try {
      await startRework.mutateAsync(id);
      message.success('Rework started');
    } catch (e) {
      message.error('Failed to start rework');
    }
  };

  const handleComplete = async (id: number) => {
    // In real app, open modal for notes
    try {
      await completeRework.mutateAsync({ id, notes: 'Completed via queue' });
      message.success('Rework completed');
    } catch (e) {
      message.error('Failed to complete rework');
    }
  };

  const columns = [
    {
      title: 'MO #',
      dataIndex: 'manufacturing_order_id',
      key: 'mo_id',
      render: (text: string) => <span className="font-medium">MO-{text}</span>,
    },
    {
      title: 'Operation',
      dataIndex: 'operation_name',
      key: 'operation',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'in_progress' ? 'processing' : 'default'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('MMM D, HH:mm'),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: any) => (
        <Space>
          {record.status === 'scheduled' && (
            <Button
              size="small"
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={() => handleStart(record.id)}
            >
              Start
            </Button>
          )}
          {record.status === 'in_progress' && (
            <Button
              size="small"
              type="primary"
              className="bg-green-600"
              icon={<CheckCircleOutlined />}
              onClick={() => handleComplete(record.id)}
            >
              Complete
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div>
        <Typography.Title level={2} style={{ margin: 0 }}>
          Rework Queue
        </Typography.Title>
        <Typography.Text type="secondary">
          Manage pending rework operations
        </Typography.Text>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <Table
          columns={columns}
          dataSource={reworkOps || []}
          rowKey="id"
          loading={isLoading}
          locale={{ emptyText: 'No rework operations pending' }}
        />
      </div>
    </div>
  );
};

export default ReworkQueuePage;

