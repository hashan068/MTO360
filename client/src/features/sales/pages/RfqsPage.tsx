import { PlusOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  Drawer,
  Form,
  Input,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { rfqsApi } from '@/features/sales/api';
import type { RFQ, RFQCreatePayload } from '@/features/sales/types';

const statusColor: Record<RFQ['status'], string> = {
  DRAFT: 'default',
  OPEN: 'blue',
  REVIEW: 'purple',
  APPROVED: 'green',
  REJECTED: 'red',
  CLOSED: 'default',
};

const RfqsPage = () => {
  const { message } = AntdApp.useApp();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<RFQCreatePayload>();

  const {
    data: rfqs = [],
    isLoading,
    refetch,
  } = useQuery<RFQ[]>({
    queryKey: ['sales', 'rfqs', 'list'],
    queryFn: () => rfqsApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: RFQCreatePayload) => rfqsApi.create(values),
    onSuccess: () => {
      message.success('RFQ created');
      setDrawerOpen(false);
      form.resetFields();
      refetch();
    },
    onError: () => message.error('Unable to create RFQ'),
  });

  const columns: ColumnsType<RFQ> = [
    { title: 'RFQ #', dataIndex: 'id', key: 'id', width: 80 },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (value: RFQ['status']) => <Tag color={statusColor[value]}>{value}</Tag> },
    { title: 'Due Date', dataIndex: 'due_date', key: 'due_date' },
    { title: 'Description', dataIndex: 'description', key: 'description' },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at' },
  ];

  const handleCreate = (values: RFQCreatePayload) => {
    createMutation.mutate({ ...values, items: values.items ?? [] });
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Space align="center" style={{ justifyContent: 'space-between', width: '100%' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0 }}>
            RFQs
          </Typography.Title>
          <Typography.Text type="secondary">
            Track requests for quotes throughout the sales pipeline.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setDrawerOpen(true)}>
          New RFQ
        </Button>
      </Space>
      <Card>
        <Table<RFQ> rowKey="id" columns={columns} dataSource={rfqs} loading={isLoading} pagination={{ pageSize: 10 }} />
      </Card>

      <Drawer
        width={480}
        title="Create RFQ"
        destroyOnClose
        onClose={() => setDrawerOpen(false)}
        open={isDrawerOpen}
      >
        <Form<RFQCreatePayload> layout="vertical" form={form} onFinish={handleCreate} initialValues={{ status: 'DRAFT' }}>
          <Form.Item name="status" label="Status">
            <Select
              options={[
                { label: 'Draft', value: 'DRAFT' },
                { label: 'Open', value: 'OPEN' },
                { label: 'Review', value: 'REVIEW' },
              ]}
            />
          </Form.Item>
          <Form.Item name="due_date" label="Due Date">
            <Input placeholder="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={4} placeholder="Describe the request" />
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

export default RfqsPage;
