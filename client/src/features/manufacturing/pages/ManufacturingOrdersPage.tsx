import { CheckOutlined, PlayCircleOutlined, PlusOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  Drawer,
  Form,
  InputNumber,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { completeManufacturing, manufacturingOrdersApi, startManufacturing } from '@/features/manufacturing/api';
import { productsApi } from '@/features/sales/api';
import type { ManufacturingOrder, ManufacturingOrderCreatePayload } from '@/features/manufacturing/types';
import type { Product } from '@/features/sales/types';
import ProtectedAction from '@/components/ProtectedAction';
import MaterialStatusCell from '@/features/manufacturing/components/MaterialStatusCell';

const statusColor: Record<ManufacturingOrder['status'], string> = {
  PENDING: 'gold',
  PLANNED: 'blue',
  IN_PROGRESS: 'purple',
  COMPLETED: 'green',
  CANCELLED: 'red',
};

const ManufacturingOrdersPage = () => {
  const { message } = AntdApp.useApp();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<ManufacturingOrderCreatePayload>();

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['sales', 'products', 'manufacturing-options'],
    queryFn: () => productsApi.list({ limit: 200 }),
  });

  const {
    data: orders = [],
    isLoading,
    refetch,
  } = useQuery<ManufacturingOrder[]>({
    queryKey: ['manufacturing', 'orders', 'list'],
    queryFn: () => manufacturingOrdersApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (payload: ManufacturingOrderCreatePayload) => manufacturingOrdersApi.create(payload),
    onSuccess: () => {
      message.success('Manufacturing order created');
      setDrawerOpen(false);
      form.resetFields();
      refetch();
    },
    onError: () => message.error('Unable to create manufacturing order'),
  });

  const startMutation = useMutation({
    mutationFn: (id: number) => startManufacturing(id),
    onSuccess: () => {
      message.success('Production started');
      refetch();
    },
    onError: () => message.error('Unable to start production'),
  });

  const completeMutation = useMutation({
    mutationFn: (id: number) => completeManufacturing(id),
    onSuccess: () => {
      message.success('Production completed');
      refetch();
    },
    onError: () => message.error('Unable to complete production'),
  });

  const handleStart = (order: ManufacturingOrder) => {
    Modal.confirm({
      title: `Start manufacturing order #${order.id}?`,
      okText: 'Start',
      onOk: () => startMutation.mutate(order.id),
    });
  };

  const handleComplete = (order: ManufacturingOrder) => {
    Modal.confirm({
      title: `Complete manufacturing order #${order.id}?`,
      okText: 'Complete',
      onOk: () => completeMutation.mutate(order.id),
    });
  };

  const columns: ColumnsType<ManufacturingOrder> = [
    { title: 'Order', dataIndex: 'id', key: 'id', width: 90 },
    { title: 'Product', dataIndex: 'product_name', key: 'product_name' },
    { title: 'Quantity', dataIndex: 'quantity', key: 'quantity', width: 110 },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (value: ManufacturingOrder['status']) => <Tag color={statusColor[value]}>{value}</Tag>,
    },
    {
      title: 'Materials',
      key: 'materials',
      render: (_, record) => <MaterialStatusCell moId={record.id} />,
    },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at' },
    {
      key: 'actions',
      width: 220,
      render: (_, record) => (
        <Space>
          <ProtectedAction permission="production.operation.start">
            <Button
              icon={<PlayCircleOutlined />}
              type="link"
              disabled={record.status !== 'PLANNED' && record.status !== 'PENDING'}
              loading={startMutation.isPending && startMutation.variables === record.id}
              onClick={() => handleStart(record)}
            >
              Start
            </Button>
          </ProtectedAction>
          <ProtectedAction permission="production.operation.complete">
            <Button
              icon={<CheckOutlined />}
              type="link"
              disabled={record.status !== 'IN_PROGRESS'}
              loading={completeMutation.isPending && completeMutation.variables === record.id}
              onClick={() => handleComplete(record)}
            >
              Complete
            </Button>
          </ProtectedAction>
        </Space>
      ),
    },
  ];

  const handleCreate = (values: ManufacturingOrderCreatePayload) => {
    createMutation.mutate({
      ...values,
      product_id: values.product_id ?? null,
      sales_order_item_id: values.sales_order_item_id ?? null,
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            Manufacturing Orders
          </Typography.Title>
          <Typography.Text type="secondary">
            Coordinate production runs and monitor progress through completion.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setDrawerOpen(true)}>
          New Manufacturing Order
        </Button>
      </div>
      <Card>
        <Table<ManufacturingOrder>
          rowKey="id"
          columns={columns}
          dataSource={orders}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title="Create Manufacturing Order"
        width={520}
        destroyOnClose
        open={isDrawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Form<ManufacturingOrderCreatePayload> layout="vertical" form={form} onFinish={handleCreate}>
          <Form.Item name="product_id" label="Product" rules={[{ required: true }]}>
            <Select
              showSearch
              placeholder="Select product"
              optionFilterProp="label"
              options={products.map((product) => ({
                label: product.product_name ?? product.description,
                value: product.id,
              }))}
            />
          </Form.Item>
          <Form.Item name="quantity" label="Quantity" rules={[{ required: true }]}>
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="sales_order_item_id" label="Sales Order Item">
            <InputNumber min={0} style={{ width: '100%' }} placeholder="Optional reference" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={createMutation.isPending}>
                Create Order
              </Button>
              <Button htmlType="button" onClick={() => form.resetFields()}>
                Reset
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Drawer>
    </div>
  );
};

export default ManufacturingOrdersPage;
