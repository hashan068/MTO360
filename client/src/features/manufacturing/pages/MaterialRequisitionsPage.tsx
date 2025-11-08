import { PlusOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  Drawer,
  Form,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { billOfMaterialsApi, manufacturingOrdersApi, materialRequisitionsApi } from '@/features/manufacturing/api';
import type {
  MaterialRequisition,
  MaterialRequisitionCreatePayload,
  MaterialRequisitionItem,
} from '@/features/manufacturing/types';

const statusColor: Record<MaterialRequisition['status'], string> = {
  PENDING: 'gold',
  APPROVED: 'green',
  REJECTED: 'red',
  FULFILLED: 'blue',
  CANCELLED: 'default',
};

const MaterialRequisitionsPage = () => {
  const { message } = AntdApp.useApp();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<MaterialRequisitionCreatePayload>();
  const [selectedItems, setSelectedItems] = useState<MaterialRequisitionItem[] | null>(null);

  const { data: orders = [] } = useQuery({
    queryKey: ['manufacturing', 'orders', 'options'],
    queryFn: () => manufacturingOrdersApi.list({ limit: 200 }),
  });

  const { data: boms = [] } = useQuery({
    queryKey: ['manufacturing', 'boms', 'options'],
    queryFn: () => billOfMaterialsApi.list({ limit: 200 }),
  });

  const {
    data: requisitions = [],
    isLoading,
    refetch,
  } = useQuery<MaterialRequisition[]>({
    queryKey: ['manufacturing', 'material-requisitions', 'list'],
    queryFn: () => materialRequisitionsApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: MaterialRequisitionCreatePayload) => materialRequisitionsApi.create(values),
    onSuccess: () => {
      message.success('Material requisition created');
      setDrawerOpen(false);
      form.resetFields();
      refetch();
    },
    onError: () => message.error('Unable to create material requisition'),
  });

  const columns: ColumnsType<MaterialRequisition> = useMemo(
    () => [
      { title: 'Requisition', dataIndex: 'id', key: 'id', width: 120 },
      { title: 'Order', dataIndex: 'manufacturing_order_id', key: 'manufacturing_order_id' },
      { title: 'BOM', dataIndex: 'bom_id', key: 'bom_id', render: (value) => value ?? '—' },
      {
        title: 'Status',
        dataIndex: 'status',
        key: 'status',
        render: (value: MaterialRequisition['status']) => <Tag color={statusColor[value]}>{value}</Tag>,
      },
      { title: 'Created', dataIndex: 'created_at', key: 'created_at' },
      {
        key: 'actions',
        width: 140,
        render: (_, record) => (
          <Button type="link" onClick={() => setSelectedItems(record.items ?? [])}>
            View Items
          </Button>
        ),
      },
    ],
    []
  );

  const handleCreate = (values: MaterialRequisitionCreatePayload) => {
    if (!values.manufacturing_order_id) {
      message.error('Select a manufacturing order');
      return;
    }
    createMutation.mutate({
      manufacturing_order_id: values.manufacturing_order_id,
      bom_id: values.bom_id ?? null,
    });
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Space align="center" style={{ justifyContent: 'space-between', width: '100%' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Material Requisitions
          </Typography.Title>
          <Typography.Text type="secondary">
            Request materials for manufacturing orders and monitor fulfillment.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setDrawerOpen(true)}>
          New Requisition
        </Button>
      </Space>
      <Card>
        <Table<MaterialRequisition>
          rowKey="id"
          columns={columns}
          dataSource={requisitions}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title="Create Material Requisition"
        width={500}
        destroyOnClose
        open={isDrawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Form<MaterialRequisitionCreatePayload> layout="vertical" form={form} onFinish={handleCreate}>
          <Form.Item name="manufacturing_order_id" label="Manufacturing Order" rules={[{ required: true }]}> 
            <Select
              showSearch
              placeholder="Select order"
              optionFilterProp="label"
              options={orders.map((order) => ({ label: `MO-${order.id} • ${order.product_name ?? 'Product'}`, value: order.id }))}
            />
          </Form.Item>
          <Form.Item name="bom_id" label="Bill of Materials">
            <Select
              allowClear
              placeholder="Select BOM"
              optionFilterProp="label"
              options={boms.map((bom) => ({ label: bom.name, value: bom.id }))}
            />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={createMutation.isPending}>
                Create Requisition
              </Button>
              <Button htmlType="button" onClick={() => form.resetFields()}>
                Reset
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Drawer>

      <Modal
        title="Requisition Items"
        open={Boolean(selectedItems)}
        footer={null}
        onCancel={() => setSelectedItems(null)}
      >
        {selectedItems && selectedItems.length > 0 ? (
          <Table<MaterialRequisitionItem>
            rowKey="id"
            dataSource={selectedItems}
            pagination={false}
            size="small"
            columns={[
              { title: 'Component', dataIndex: 'component_name', key: 'component_name' },
              { title: 'Quantity', dataIndex: 'quantity', key: 'quantity' },
              { title: 'Status', dataIndex: 'status', key: 'status' },
            ]}
          />
        ) : (
          <Typography.Text type="secondary">No component items recorded.</Typography.Text>
        )}
      </Modal>
    </Space>
  );
};

export default MaterialRequisitionsPage;
