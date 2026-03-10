import { useState } from 'react';
import { Table, Button, Typography, Input } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { useNCRs } from '../hooks/useNCRs';
import { QualityStatusBadge } from '../components/QualityStatusBadge';
import { NCRForm } from '../components/NCRForm';
import type { NCR } from '../types';
import dayjs from 'dayjs';

const NCRManagementPage = () => {
  const { data: ncrs, isLoading } = useNCRs();
  const [isModalVisible, setIsModalVisible] = useState(false);

  const columns = [
    {
      title: 'NCR #',
      dataIndex: 'ncr_number',
      key: 'ncr_number',
      render: (text: string, record: NCR) => (
        <Link to={`/quality/ncrs/${record.id}`} className="font-medium hover:underline">
          {text}
        </Link>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <QualityStatusBadge type="ncr" value={status} />
      ),
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: string) => (
        <span className={`capitalize ${priority === 'critical' ? 'text-red-600 font-bold' : ''}`}>
          {priority}
        </span>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('MMM D, YYYY'),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: NCR) => (
        <Link to={`/quality/ncrs/${record.id}`}>
          <Button size="small">Manage</Button>
        </Link>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Typography.Title level={2} style={{ margin: 0 }}>
            NCR Management
          </Typography.Title>
          <Typography.Text type="secondary">
            Non-Conformance Reports and workflows
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalVisible(true)}>
          Create NCR
        </Button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <div className="mb-4 flex gap-4">
          <Input
            prefix={<SearchOutlined />}
            placeholder="Search NCRs..."
            className="max-w-md"
          />
        </div>

        <Table
          columns={columns}
          dataSource={ncrs || []}
          rowKey="id"
          loading={isLoading}
        />
      </div>

      <NCRForm
        visible={isModalVisible}
        onClose={() => setIsModalVisible(false)}
      />
    </div>
  );
};

export default NCRManagementPage;

