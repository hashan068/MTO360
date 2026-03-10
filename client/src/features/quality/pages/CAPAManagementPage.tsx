import { useState } from 'react';
import { Table, Button, Typography, Input } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { useCAPAs } from '../hooks/useCAPAs';
import { QualityStatusBadge } from '../components/QualityStatusBadge';
import { CAPAForm } from '../components/CAPAForm';
import type { CAPA } from '../types';
import dayjs from 'dayjs';

const CAPAManagementPage = () => {
  const { data: capas, isLoading } = useCAPAs();
  const [isModalVisible, setIsModalVisible] = useState(false);

  const columns = [
    {
      title: 'CAPA #',
      dataIndex: 'capa_number',
      key: 'capa_number',
      render: (text: string, record: CAPA) => (
        <Link to={`/quality/capas/${record.id}`} className="font-medium hover:underline">
          {text}
        </Link>
      ),
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <QualityStatusBadge type="capa" value={status} />
      ),
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
      render: (_: any, record: CAPA) => (
        <Link to={`/quality/capas/${record.id}`}>
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
            CAPA Management
          </Typography.Title>
          <Typography.Text type="secondary">
            Corrective and Preventive Actions
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalVisible(true)}>
          Create CAPA
        </Button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <div className="mb-4 flex gap-4">
          <Input
            prefix={<SearchOutlined />}
            placeholder="Search CAPAs..."
            className="max-w-md"
          />
        </div>

        <Table
          columns={columns}
          dataSource={capas || []}
          rowKey="id"
          loading={isLoading}
        />
      </div>

      <CAPAForm
        visible={isModalVisible}
        onClose={() => setIsModalVisible(false)}
      />
    </div>
  );
};

export default CAPAManagementPage;

