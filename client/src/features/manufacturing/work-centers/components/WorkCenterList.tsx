/**
 * Work Center List Component
 * Displays table of all work centers with CRUD actions
 */
import { useState } from 'react';
import { Table, Button, Space, Tag, Input, Card, Modal } from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useWorkCenters, useDeleteWorkCenter } from '../hooks/useWorkCenters';
import { WorkCenterForm } from './WorkCenterForm';
import type { WorkCenter } from '@/types/manufacturing';

const { Search } = Input;
const { confirm } = Modal;

export const WorkCenterList = () => {
  const [searchText, setSearchText] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | undefined>();

  const { data: workCenters, isLoading } = useWorkCenters();
  const deleteWorkCenter = useDeleteWorkCenter();

  const handleCreate = () => {
    setEditingId(undefined);
    setIsFormOpen(true);
  };

  const handleEdit = (id: number) => {
    setEditingId(id);
    setIsFormOpen(true);
  };

  const handleDelete = (record: WorkCenter) => {
    confirm({
      title: `Delete work center "${record.name}"?`,
      icon: <ExclamationCircleOutlined />,
      content: 'This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      onOk: () => {
        deleteWorkCenter.mutate(record.id);
      },
    });
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingId(undefined);
  };

  // Filter data
  const filteredData = workCenters?.filter((wc) =>
    Object.values(wc).some((value) =>
      String(value).toLowerCase().includes(searchText.toLowerCase())
    )
  );

  const columns: ColumnsType<WorkCenter> = [
    {
      title: 'Code',
      dataIndex: 'code',
      key: 'code',
      width: 120,
      sorter: (a, b) => a.code.localeCompare(b.code),
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Capacity (hrs/day)',
      dataIndex: 'capacity_hours_per_day',
      key: 'capacity',
      width: 150,
      align: 'right',
      render: (value: number) => value.toFixed(1),
      sorter: (a, b) => a.capacity_hours_per_day - b.capacity_hours_per_day,
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
      width: 150,
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'status',
      width: 100,
      align: 'center',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? 'Active' : 'Inactive'}
        </Tag>
      ),
      filters: [
        { text: 'Active', value: true },
        { text: 'Inactive', value: false },
      ],
      onFilter: (value, record) => record.is_active === value,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 120,
      align: 'center',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record.id)}
            size="small"
          />
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
            size="small"
          />
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="Work Centers"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Create Work Center
        </Button>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Search
          placeholder="Search work centers..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ maxWidth: 400 }}
          allowClear
        />

        <Table
          columns={columns}
          dataSource={filteredData}
          rowKey="id"
          loading={isLoading}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} work centers`,
            defaultPageSize: 20,
          }}
        />
      </Space>

      <WorkCenterForm
        open={isFormOpen}
        editingId={editingId}
        onClose={handleFormClose}
      />
    </Card>
  );
};
