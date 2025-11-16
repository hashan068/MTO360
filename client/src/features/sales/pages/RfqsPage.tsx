import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import {
  Button,
  Card,
  Input,
  Select,
  Space,
  Table,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { rfqsApi } from '@/features/sales/api';
import type { RFQ, RFQStatus } from '@/features/sales/types';
import { StatusBadge } from '@/features/sales/components/StatusBadge';
import { formatDate } from '@/shared/utils/format';

const RfqsPage = () => {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<RFQStatus | undefined>(undefined);
  const [searchText, setSearchText] = useState<string>('');

  const {
    data: rfqs = [],
    isLoading,
  } = useQuery<RFQ[]>({
    queryKey: ['sales', 'rfqs', 'list', statusFilter, searchText],
    queryFn: () => rfqsApi.list({ 
      status: statusFilter, 
      search: searchText || undefined,
      limit: 200 
    }),
  });

  const columns: ColumnsType<RFQ> = [
    { 
      title: 'RFQ #', 
      dataIndex: 'id', 
      key: 'id', 
      width: 100,
      sorter: (a, b) => a.id - b.id,
    },
    { 
      title: 'Creator', 
      dataIndex: 'creator_name', 
      key: 'creator_name',
      render: (name: string | null, record: RFQ) => name || `User #${record.creator_id}`,
    },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      width: 140,
      render: (status: RFQStatus) => <StatusBadge status={status} />,
    },
    { 
      title: 'Due Date', 
      dataIndex: 'due_date', 
      key: 'due_date',
      width: 140,
      render: (date: string | null) => date ? formatDate(date) : '—',
      sorter: (a, b) => {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
      },
    },
    { 
      title: 'Created Date', 
      dataIndex: 'created_at', 
      key: 'created_at',
      width: 140,
      render: (date: string) => formatDate(date),
      sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    },
    { 
      title: 'Description', 
      dataIndex: 'description', 
      key: 'description',
      ellipsis: true,
      render: (text: string | null) => text || '—',
    },
  ];

  const handleRowClick = (record: RFQ) => {
    navigate(`/sales/rfqs/${record.id}`);
  };

  const handleCreateRFQ = () => {
    navigate('/sales/rfqs/new');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            RFQs
          </Typography.Title>
          <Typography.Text type="secondary">
            Track requests for quotes throughout the sales pipeline.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateRFQ}>
          Create RFQ
        </Button>
      </div>

      <Card>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Space size="middle" style={{ width: '100%' }}>
            <Select
              placeholder="Filter by status"
              allowClear
              style={{ width: 200 }}
              value={statusFilter}
              onChange={setStatusFilter}
              options={[
                { label: 'Draft', value: 'draft' },
                { label: 'Sent', value: 'sent' },
                { label: 'Completed', value: 'completed' },
                { label: 'Cancelled', value: 'cancelled' },
              ]}
            />
            <Input
              placeholder="Search RFQ number, description..."
              prefix={<SearchOutlined />}
              allowClear
              style={{ width: 300 }}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </Space>

          <Table<RFQ> 
            rowKey="id" 
            columns={columns} 
            dataSource={rfqs} 
            loading={isLoading} 
            pagination={{ pageSize: 10, showSizeChanger: true, showTotal: (total) => `Total ${total} RFQs` }}
            onRow={(record) => ({
              onClick: () => handleRowClick(record),
              style: { cursor: 'pointer' },
            })}
          />
        </Space>
      </Card>
    </div>
  );
};

export default RfqsPage;
