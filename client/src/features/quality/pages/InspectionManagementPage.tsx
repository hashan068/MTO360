import { useState } from 'react';
import { Table, Button, Typography, Tag } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import { useInspectionPoints } from '../hooks/useInspections';
import { InspectionPointForm } from '../components/InspectionPointForm';
import type { InspectionPoint } from '../types';

const InspectionManagementPage = () => {
  const { data: points, isLoading } = useInspectionPoints();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingPoint, setEditingPoint] = useState<InspectionPoint | undefined>(undefined);

  const handleCreate = () => {
    setEditingPoint(undefined);
    setIsModalVisible(true);
  };

  const handleEdit = (point: InspectionPoint) => {
    setEditingPoint(point);
    setIsModalVisible(true);
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <span className="font-medium">{text}</span>,
    },
    {
      title: 'Type',
      dataIndex: 'inspection_type',
      key: 'inspection_type',
      render: (text: string) => <Tag>{text.replace('_', ' ').toUpperCase()}</Tag>,
    },
    {
      title: 'Checklist Items',
      dataIndex: 'checklist',
      key: 'checklist',
      render: (checklist: any[]) => checklist?.length || 0,
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: InspectionPoint) => (
        <Button size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
          Edit
        </Button>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Typography.Title level={2} style={{ margin: 0 }}>
            Inspection Points
          </Typography.Title>
          <Typography.Text type="secondary">
            Manage inspection definitions and checklists
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Create Point
        </Button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <Table
          columns={columns}
          dataSource={points || []}
          rowKey="id"
          loading={isLoading}
        />
      </div>

      <InspectionPointForm
        visible={isModalVisible}
        onClose={() => setIsModalVisible(false)}
        initialValues={editingPoint}
      />
    </div>
  );
};

export default InspectionManagementPage;
