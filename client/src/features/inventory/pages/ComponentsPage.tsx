import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  Drawer,
  Input,
  Modal,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { componentsApi } from '@/features/inventory/api';
import type { Component } from '@/features/inventory/types';
import { useDebouncedValue } from '@/shared/hooks/useDebouncedValue';
import { useApiMutation } from '@/shared/hooks/useApiMutation';
import { formatCurrency } from '@/shared/utils/format';

const ComponentsPage = () => {
  const { message } = AntdApp.useApp();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedComponent, setSelectedComponent] = useState<Component | null>(null);
  const debouncedSearch = useDebouncedValue(searchTerm, 300);

  const { data: components = [], isLoading, refetch } = useQuery<Component[]>({
    queryKey: ['inventory', 'components', debouncedSearch],
    queryFn: () => componentsApi.list({ search: debouncedSearch || undefined, limit: 200 }),
  });

  const deleteMutation = useApiMutation<void, number>({
    mutationFn: (id) => componentsApi.remove(id),
    onSuccess: () => {
      message.success('Component removed successfully');
      refetch();
    },
  });

  const lowStockIds = useMemo(
    () => new Set(components.filter((component) => component.quantity <= component.reorder_level).map((c) => c.id)),
    [components]
  );

  const columns: ColumnsType<Component> = [
    {
      title: 'Component',
      dataIndex: 'name',
      key: 'name',
      render: (value, record) => (
        <Typography.Link onClick={() => setSelectedComponent(record)}>{value}</Typography.Link>
      ),
    },
    { title: 'Quantity', dataIndex: 'quantity', key: 'quantity', width: 120 },
    { title: 'Unit', dataIndex: 'unit_of_measure', key: 'unit_of_measure', width: 100 },
    {
      title: 'Reorder Level',
      dataIndex: 'reorder_level',
      key: 'reorder_level',
      width: 140,
      render: (value, record) => (
        <Tag color={record.quantity <= value ? 'red' : 'default'}>{value}</Tag>
      ),
    },
    {
      title: 'Supplier',
      dataIndex: 'supplier_id',
      key: 'supplier_id',
      width: 140,
      render: (value: number | undefined | null) => value ?? '—',
    },
    {
      key: 'actions',
      width: 160,
      render: (_, record) => (
        <Space>
          <Button
            icon={<EditOutlined />}
            type="link"
            onClick={() => navigate(`/inventory/components/${record.id}`)}
          >
            Edit
          </Button>
          <Button
            danger
            type="link"
            icon={<DeleteOutlined />}
            loading={deleteMutation.isPending && deleteMutation.variables === record.id}
            onClick={() =>
              Modal.confirm({
                title: `Delete ${record.name}?`,
                content: 'This action cannot be undone.',
                okText: 'Delete',
                okButtonProps: { danger: true },
                onOk: () => deleteMutation.mutate(record.id),
              })
            }
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Space align="center" style={{ justifyContent: 'space-between', width: '100%' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Components
          </Typography.Title>
          <Typography.Text type="secondary">
            Track component levels and identify low stock items.
          </Typography.Text>
        </div>
        <Space>
          <Input.Search
            allowClear
            placeholder="Search components"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            onSearch={setSearchTerm}
            style={{ width: 260 }}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/inventory/components/new')}>
            New Component
          </Button>
        </Space>
      </Space>
      <Card>
        <Table<Component>
          rowKey="id"
          loading={isLoading}
          columns={columns}
          dataSource={components}
          pagination={{ pageSize: 10 }}
          rowClassName={(record) => (lowStockIds.has(record.id) ? 'bg-red-50/60' : '')}
        />
      </Card>

      <Drawer
        width={420}
        title={selectedComponent?.name}
        destroyOnClose
        onClose={() => setSelectedComponent(null)}
        open={Boolean(selectedComponent)}
      >
        {selectedComponent && (
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Typography.Paragraph>
              <Typography.Text strong>Description:</Typography.Text>{' '}
              {selectedComponent.description ?? '—'}
            </Typography.Paragraph>
            <Typography.Paragraph>
              <Typography.Text strong>Quantity:</Typography.Text>{' '}
              {selectedComponent.quantity} {selectedComponent.unit_of_measure}
            </Typography.Paragraph>
            <Typography.Paragraph>
              <Typography.Text strong>Reorder level:</Typography.Text>{' '}
              {selectedComponent.reorder_level}
            </Typography.Paragraph>
            <Typography.Paragraph>
              <Typography.Text strong>Cost:</Typography.Text>{' '}
              {formatCurrency(selectedComponent.cost)}
            </Typography.Paragraph>
            <Typography.Paragraph>
              <Typography.Text strong>Supplier:</Typography.Text>{' '}
              {selectedComponent.supplier_id ?? '—'}
            </Typography.Paragraph>
            <Button type="primary" onClick={() => navigate(`/inventory/components/${selectedComponent.id}`)}>
              Edit component
            </Button>
          </Space>
        )}
      </Drawer>
    </Space>
  );
};

export default ComponentsPage;
