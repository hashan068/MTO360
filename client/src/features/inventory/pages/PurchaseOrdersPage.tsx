import { PlusOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  Drawer,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { purchaseOrdersApi, purchaseRequisitionsApi } from '@/features/inventory/api';
import type {
  PurchaseOrder,
  PurchaseOrderCreatePayload,
  PurchaseRequisition,
} from '@/features/inventory/types';

const statusColor: Record<PurchaseOrder['status'], string> = {
  DRAFT: 'default',
  PENDING_APPROVAL: 'gold',
  APPROVED: 'green',
  REJECTED: 'red',
  SENT: 'blue',
  RECEIVED: 'success',
  CANCELLED: 'default',
};

const PurchaseOrdersPage = () => {
  const { message } = AntdApp.useApp();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<PurchaseOrderCreatePayload>();

  const { data: requisitions = [] } = useQuery<PurchaseRequisition[]>({
    queryKey: ['inventory', 'purchase-requisitions', 'options'],
    queryFn: () => purchaseRequisitionsApi.list({ limit: 200 }),
  });

  const {
    data: purchaseOrders = [],
    isLoading,
    refetch,
  } = useQuery<PurchaseOrder[]>({
    queryKey: ['inventory', 'purchase-orders', 'list'],
    queryFn: () => purchaseOrdersApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: PurchaseOrderCreatePayload) => purchaseOrdersApi.create(values),
    onSuccess: () => {
      message.success('Purchase order created');
      setDrawerOpen(false);
      form.resetFields();
      refetch();
    },
    onError: () => message.error('Unable to create purchase order'),
  });

  const columns: ColumnsType<PurchaseOrder> = [
    { title: 'PO #', dataIndex: 'id', key: 'id', width: 80 },
    { title: 'Requisition', dataIndex: 'purchase_requisition_id', key: 'purchase_requisition_id', width: 130 },
    { title: 'Supplier', dataIndex: 'supplier_id', key: 'supplier_id', width: 120, render: (value) => value ?? '—' },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 140,
      render: (value: PurchaseOrder['status']) => <Tag color={statusColor[value]}>{value}</Tag>,
    },
    { title: 'Unit Price', dataIndex: 'price_per_unit', key: 'price_per_unit' },
    { title: 'Total Price', dataIndex: 'total_price', key: 'total_price' },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at' },
  ];

  const handleCreate = (values: PurchaseOrderCreatePayload) => {
    createMutation.mutate({
      ...values,
      supplier_id: values.supplier_id ?? null,
      notes: values.notes ?? null,
      price_per_unit: values.price_per_unit ?? null,
      total_price: values.total_price ?? null,
    });
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Space align="center" style={{ justifyContent: 'space-between', width: '100%' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Purchase Orders
          </Typography.Title>
          <Typography.Text type="secondary">
            Convert approved requisitions into orders and track supplier fulfillment.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setDrawerOpen(true)}>
          New Purchase Order
        </Button>
      </Space>
      <Card>
        <Table<PurchaseOrder>
          rowKey="id"
          columns={columns}
          dataSource={purchaseOrders}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title="Create Purchase Order"
        width={520}
        destroyOnClose
        onClose={() => setDrawerOpen(false)}
        open={isDrawerOpen}
      >
        <Form<PurchaseOrderCreatePayload> layout="vertical" form={form} onFinish={handleCreate}>
          <Form.Item
            name="purchase_requisition_id"
            label="Linked Requisition"
            rules={[{ required: true, message: 'Select a requisition' }]}
          >
            <Select
              placeholder="Select requisition"
              options={requisitions.map((req) => ({
                label: `PR-${req.id} • ${req.component_name ?? 'Component'} • Qty ${req.quantity}`,
                value: req.id,
              }))}
            />
          </Form.Item>
          <Form.Item name="supplier_id" label="Supplier ID">
            <InputNumber min={0} style={{ width: '100%' }} placeholder="Supplier reference" />
          </Form.Item>
          <Form.Item name="price_per_unit" label="Unit Price">
            <Input placeholder="0.00" />
          </Form.Item>
          <Form.Item name="total_price" label="Total Price">
            <Input placeholder="0.00" />
          </Form.Item>
          <Form.Item name="status" label="Status" initialValue="DRAFT">
            <Select
              options={[
                { label: 'Draft', value: 'DRAFT' },
                { label: 'Pending Approval', value: 'PENDING_APPROVAL' },
                { label: 'Approved', value: 'APPROVED' },
                { label: 'Rejected', value: 'REJECTED' },
                { label: 'Sent', value: 'SENT' },
                { label: 'Received', value: 'RECEIVED' },
                { label: 'Cancelled', value: 'CANCELLED' },
              ]}
            />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={createMutation.isPending}>
                Create
              </Button>
              <Button htmlType="button" onClick={() => form.resetFields()}>
                Reset
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Drawer>
    </Space>
  );
};

export default PurchaseOrdersPage;
