/**
 * Operation Route List Component
 * Displays table of all operation routes with CRUD actions
 */
import { useState } from 'react';
import { Table, Button, Space, Tag, Input, Card, Modal } from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CopyOutlined,
  SearchOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useOperationRoutes,
  useDeleteOperationRoute,
  useCopyOperationRoute,
  useUpdateOperationRoute,
} from '../hooks/useOperationRoutes';
import { OperationRouteForm } from './OperationRouteForm';
import type { OperationRoute } from '@/types/manufacturing';
import { useNavigate } from 'react-router-dom';

const { Search } = Input;
const { confirm } = Modal;

export const OperationRouteList = () => {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | undefined>();

  const { data: routes, isLoading } = useOperationRoutes();
  const deleteRoute = useDeleteOperationRoute();
  const copyRoute = useCopyOperationRoute();
  const updateRoute = useUpdateOperationRoute();

  const handleCreate = () => {
    setEditingId(undefined);
    setIsFormOpen(true);
  };

  const handleEdit = (id: number) => {
    // Navigate to route detail page for full editing
    navigate(`/manufacturing/operation-routes/${id}`);
  };

  const handleCopy = (record: OperationRoute) => {
    Modal.confirm({
      title: 'Copy Operation Route',
      content: (
        <div>
          <p>Enter name for the copied route:</p>
          <Input
            id="copy-route-name"
            placeholder={`${record.name} (Copy)`}
            defaultValue={`${record.name} (Copy)`}
          />
        </div>
      ),
      onOk: () => {
        const input = document.getElementById('copy-route-name') as HTMLInputElement;
        const newName = input?.value || `${record.name} (Copy)`;
        copyRoute.mutate({ id: record.id, name: newName });
      },
    });
  };

  const handleDelete = (record: OperationRoute) => {
    confirm({
      title: `Delete operation route "${record.name}"?`,
      icon: <ExclamationCircleOutlined />,
      content: 'This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      onOk: () => {
        deleteRoute.mutate(record.id);
      },
    });
  };

  const handleToggleActive = (record: OperationRoute) => {
    updateRoute.mutate({
      id: record.id,
      data: { is_active: !record.is_active },
    });
  };

  const handleFormClose = () => {
    setIsFormOpen(false);
    setEditingId(undefined);
  };

  // Filter data
  const filteredData = routes?.filter((route) =>
    Object.values(route).some((value) =>
      String(value).toLowerCase().includes(searchText.toLowerCase())
    )
  );

  const columns: ColumnsType<OperationRoute> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: 'Product ID',
      dataIndex: 'product_id',
      key: 'product_id',
      width: 120,
      render: (value) => value || '-',
    },
    {
      title: 'BOM ID',
      dataIndex: 'bom_id',
      key: 'bom_id',
      width: 120,
      render: (value) => value || '-',
    },
    {
      title: 'Operations',
      key: 'operations_count',
      width: 120,
      align: 'center',
      render: (_, record) => record.operations?.length || 0,
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'status',
      width: 100,
      align: 'center',
      render: (isActive: boolean, record) => (
        <Tag
          color={isActive ? 'success' : 'default'}
          style={{ cursor: 'pointer' }}
          onClick={() => handleToggleActive(record)}
        >
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
      width: 160,
      align: 'center',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record.id)}
            size="small"
            title="Edit route"
          />
          <Button
            type="link"
            icon={<CopyOutlined />}
            onClick={() => handleCopy(record)}
            size="small"
            title="Copy route"
          />
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
            size="small"
            title="Delete route"
          />
        </Space>
      ),
    },
  ];

  return (
    <Card
      title="Operation Routes"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Create Route
        </Button>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Search
          placeholder="Search operation routes..."
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
            showTotal: (total) => `Total ${total} routes`,
            defaultPageSize: 20,
          }}
          onRow={(record) => ({
            onDoubleClick: () => handleEdit(record.id),
          })}
        />
      </Space>

      <OperationRouteForm
        open={isFormOpen}
        editingId={editingId}
        onClose={handleFormClose}
      />
    </Card>
  );
};
