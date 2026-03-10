import { useState } from 'react';
import { Table, Button, Tag, Space, Typography, Input } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { useDefects } from '../hooks/useDefects';
import { QualityStatusBadge } from '../components/QualityStatusBadge';
import { DefectForm } from '../components/DefectForm';
import type { Defect } from '../types';
import dayjs from 'dayjs';

const DefectManagementPage = () => {
  const { data: defects, isLoading } = useDefects();
  const [isModalVisible, setIsModalVisible] = useState(false);

  const columns = [
    {
      title: 'Defect #',
      dataIndex: 'defect_number',
      key: 'defect_number',
      render: (text: string, record: Defect) => (
        <Link to={`/quality/defects/${record.id}`} className="font-medium hover:underline">
          {text}
        </Link>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'defect_type',
      key: 'defect_type',
      render: (text: string) => <span className="capitalize">{text}</span>,
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity: string) => (
        <QualityStatusBadge type="defect-severity" value={severity} />
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <QualityStatusBadge type="defect-status" value={status} />
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Reported',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('MMM D, YYYY'),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: Defect) => (
        <Link to={`/quality/defects/${record.id}`}>
          <Button size="small">View</Button>
        </Link>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Typography.Title level={2} style={{ margin: 0 }}>
            Defect Management
          </Typography.Title>
          <Typography.Text type="secondary">
            Track and manage product defects
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalVisible(true)}>
          Report Defect
        </Button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <div className="mb-4 flex gap-4">
          <Input
            prefix={<SearchOutlined />}
            placeholder="Search defects..."
            className="max-w-md"
          />
        </div>

        <Table
          columns={columns}
          dataSource={defects || []}
          rowKey="id"
          loading={isLoading}
        />
      </div>

      <DefectForm
        visible={isModalVisible}
        onClose={() => setIsModalVisible(false)}
      />
    </div>
  );
};

export default DefectManagementPage;

