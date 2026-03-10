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
import { componentsApi, purchaseRequisitionsApi } from '@/features/inventory/api';
import type { Component, PurchaseRequisition, PurchaseRequisitionCreatePayload } from '@/features/inventory/types';

const statusColor: Record<PurchaseRequisition['status'], string> = {
  PENDING: 'gold',
  APPROVED: 'green',
  REJECTED: 'red',
  COMPLETED: 'blue',
  CANCELLED: 'default',
};

const priorityColor: Record<PurchaseRequisition['priority'], string> = {
  LOW: 'default',
  MEDIUM: 'blue',
  HIGH: 'red',
};

const PurchaseRequisitionsPage = () => {
  const { message } = AntdApp.useApp();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<PurchaseRequisitionCreatePayload>();

  const { data: components = [] } = useQuery<Component[]>({
    queryKey: ['inventory', 'components', 'options'],
    queryFn: () => componentsApi.list({ limit: 200 }),
  });

  const {
    data: requisitions = [],
    isLoading,
    refetch,
  } = useQuery<PurchaseRequisition[]>({
    queryKey: ['inventory', 'purchase-requisitions', 'list'],
    queryFn: () => purchaseRequisitionsApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: PurchaseRequisitionCreatePayload) => purchaseRequisitionsApi.create(values),
    onSuccess: () => {
      message.success('Purchase requisition created');
      setDrawerOpen(false);
      form.resetFields();
      refetch();
    },
    onError: () => message.error('Unable to create purchase requisition'),
  });

  const columns: ColumnsType<PurchaseRequisition> = [
    { title: 'Req #', dataIndex: 'id', key: 'id', width: 80 },
    { title: 'Component', dataIndex: 'component_name', key: 'component_name' },
    { title: 'Quantity', dataIndex: 'quantity', key: 'quantity', width: 110 },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 110,
      render: (value: PurchaseRequisition['priority']) => <Tag color={priorityColor[value]}>{value}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 130,
      render: (value: PurchaseRequisition['status']) => <Tag color={statusColor[value]}>{value}</Tag>,
    },
    { title: 'Needed By', dataIndex: 'expected_delivery_date', key: 'expected_delivery_date' },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at' },
  ];

  const handleCreate = (values: PurchaseRequisitionCreatePayload) => {
    createMutation.mutate(values);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            Purchase Requisitions
          </Typography.Title>
          <Typography.Text type="secondary">
            Track outstanding material requests awaiting approval or fulfillment.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setDrawerOpen(true)}>
          New Requisition
        </Button>
      </div>
      <Card>
        <Table<PurchaseRequisition>
          rowKey="id"
          columns={columns}
          dataSource={requisitions || []}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title="Create Purchase Requisition"
        width={480}
        destroyOnHidden
        onClose={() => setDrawerOpen(false)}
        open={isDrawerOpen}
      >
        <Form<PurchaseRequisitionCreatePayload> layout="vertical" form={form} onFinish={handleCreate}>
          <Form.Item
            name="component_id"
            label="Component"
            rules={[{ required: true, message: 'Select a component' }]}
          >
            <Select
              showSearch
              placeholder="Select component"
              optionFilterProp="label"
              options={components.map((component) => ({
                label: component.name,
                value: component.id,
              }))}
            />
          </Form.Item>
          <Form.Item
            name="quantity"
            label="Quantity"
            rules={[{ required: true, message: 'Enter a quantity' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="priority" label="Priority" initialValue="HIGH">
            <Select
              options={[
                { label: 'High', value: 'HIGH' },
                { label: 'Medium', value: 'MEDIUM' },
                { label: 'Low', value: 'LOW' },
              ]}
            />
          </Form.Item>
          <Form.Item name="expected_delivery_date" label="Expected Delivery">
            <Input placeholder="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={createMutation.isPending}
              >
                Create
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

export default PurchaseRequisitionsPage;


