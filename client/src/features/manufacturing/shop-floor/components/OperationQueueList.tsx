/**
 * Operation Queue List Component
 * Displays list of operations in work center queue
 */
import { useState } from 'react';
import { Table, Tag, Button } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useWorkCenterQueue } from '../hooks/useShopFloor';
import { OperationExecutionModal } from './OperationExecutionModal';
import type { WorkCenterQueueItem } from '@/types/manufacturing';
import dayjs from 'dayjs';

interface OperationQueueListProps {
  workCenterId: number;
}

export const OperationQueueList = ({ workCenterId }: OperationQueueListProps) => {
  const [selectedOperation, setSelectedOperation] = useState<WorkCenterQueueItem | undefined>();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: queue, isLoading } = useWorkCenterQueue(workCenterId);

  const handleOperationClick = (operation: WorkCenterQueueItem) => {
    setSelectedOperation(operation);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setSelectedOperation(undefined);
  };

  const getStatusTag = (status: string) => {
    const config: Record<string, { color: string; text: string }> = {
      pending: { color: 'default', text: 'Pending' },
      scheduled: { color: 'blue', text: 'Scheduled' },
      in_progress: { color: 'green', text: 'In Progress' },
      completed: { color: 'default', text: 'Completed' },
      blocked: { color: 'red', text: 'Blocked' },
    };
    const { color, text } = config[status] || config.pending;
    return <Tag color={color}>{text}</Tag>;
  };

  const columns: ColumnsType<WorkCenterQueueItem> = [
    {
      title: 'Priority',
      dataIndex: 'sequence',
      key: 'sequence',
      width: 80,
      align: 'center',
      sorter: (a, b) => a.sequence - b.sequence,
    },
    {
      title: 'MO',
      dataIndex: 'mo_number',
      key: 'mo',
      width: 100,
      render: (_, record) => record.mo_number || `#${record.mo_id}`,
    },
    {
      title: 'Operation',
      dataIndex: 'operation_name',
      key: 'operation',
      ellipsis: true,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => getStatusTag(status),
      filters: [
        { text: 'Pending', value: 'pending' },
        { text: 'Scheduled', value: 'scheduled' },
        { text: 'In Progress', value: 'in_progress' },
        { text: 'Blocked', value: 'blocked' },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: 'Scheduled',
      dataIndex: 'scheduled_start',
      key: 'scheduled',
      width: 150,
      render: (date) => (date ? dayjs(date).format('MMM DD, HH:mm') : '-'),
    },
    {
      title: 'Duration',
      dataIndex: 'scheduled_duration_minutes',
      key: 'duration',
      width: 100,
      align: 'right',
      render: (minutes) => `${minutes} min`,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      align: 'center',
      render: (_, record) => (
        <Button
          type="primary"
          size="small"
          onClick={() => handleOperationClick(record)}
        >
          Open
        </Button>
      ),
    },
  ];

  return (
    <>
      <Table
        columns={columns}
        dataSource={queue || []}
        rowKey="operation_id"
        loading={isLoading}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} operations`,
        }}
        size="small"
      />

      {selectedOperation && (
        <OperationExecutionModal
          operationId={selectedOperation.operation_id}
          open={isModalOpen}
          onClose={handleModalClose}
        />
      )}
    </>
  );
};


