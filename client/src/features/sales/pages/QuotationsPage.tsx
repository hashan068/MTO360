import { MailOutlined, PlusOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  DatePicker,
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
import dayjs, { Dayjs } from 'dayjs';
import { useState } from 'react';
import { customersApi, productsApi, quotationsApi, sendQuotationEmail } from '@/features/sales/api';
import type {
  Customer,
  Product,
  Quotation,
  QuotationCreatePayload,
  QuotationItemCreatePayload,
} from '@/features/sales/types';
import { formatCurrency } from '@/shared/utils/format';

const statusColor: Record<Quotation['status'], string> = {
  QUOTATION: 'blue',
  NEGOTIATION: 'purple',
  APPROVED: 'green',
  REJECTED: 'red',
  EXPIRED: 'default',
  CONVERTED: 'success',
};

interface QuotationFormValues
  extends Omit<QuotationCreatePayload, 'date' | 'expiration_date' | 'quotation_items'> {
  date: Dayjs;
  expiration_date: Dayjs;
  quotation_items?: QuotationItemCreatePayload[];
}

const QuotationItemFields = ({ name, remove, products }: { name: number; remove: (index: number | number[]) => void; products: Product[] }) => (
  <Space align="baseline" wrap style={{ width: '100%' }}>
    <Form.Item
      name={[name, 'product_id']}
      label="Product"
      rules={[{ required: true, message: 'Select product' }]}
    >
      <Select
        showSearch
        placeholder="Product"
        optionFilterProp="label"
        options={products.map((product) => ({
          label: product.product_name ?? product.description,
          value: product.id,
        }))}
        style={{ minWidth: 200 }}
      />
    </Form.Item>
    <Form.Item
      name={[name, 'quantity']}
      label="Qty"
      rules={[{ required: true, message: 'Enter quantity' }]}
    >
      <InputNumber min={1} />
    </Form.Item>
    <Form.Item
      name={[name, 'unit_price']}
      label="Unit Price"
      rules={[{ required: true, message: 'Enter price' }]}
    >
      <InputNumber min={0} step={0.01} />
    </Form.Item>
    <Button type="link" danger onClick={() => remove(name)}>
      Remove
    </Button>
  </Space>
);

const QuotationsPage = () => {
  const { message } = AntdApp.useApp();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<QuotationFormValues>();

  const { data: quotations = [], isLoading, refetch } = useQuery<Quotation[]>({
    queryKey: ['sales', 'quotations', 'list'],
    queryFn: () => quotationsApi.list({ limit: 200 }),
  });

  const { data: customers = [] } = useQuery<Customer[]>({
    queryKey: ['sales', 'customers', 'options'],
    queryFn: () => customersApi.list({ limit: 200 }),
  });

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['sales', 'products', 'options'],
    queryFn: () => productsApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: QuotationCreatePayload) => quotationsApi.create(values),
    onSuccess: () => {
      message.success('Quotation created');
      setDrawerOpen(false);
      form.resetFields();
      refetch();
    },
    onError: () => message.error('Unable to create quotation'),
  });

  const emailMutation = useMutation({
    mutationFn: (id: number) => sendQuotationEmail(id),
    onSuccess: () => message.success('Quotation email sent'),
    onError: () => message.error('Unable to send quotation email'),
  });

  const columns: ColumnsType<Quotation> = [
    { title: 'Quotation', dataIndex: 'id', key: 'id', width: 100 },
    { title: 'Customer', dataIndex: 'customer_name', key: 'customer_name' },
    { title: 'Total', dataIndex: 'total_amount', key: 'total_amount', render: (value) => formatCurrency(value) },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (value: Quotation['status']) => <Tag color={statusColor[value]}>{value}</Tag>,
    },
    { title: 'Expires', dataIndex: 'expiration_date', key: 'expiration_date' },
    {
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Button
          type="link"
          icon={<MailOutlined />}
          loading={emailMutation.isPending && emailMutation.variables === record.id}
          onClick={() => emailMutation.mutate(record.id)}
        >
          Send Email
        </Button>
      ),
    },
  ];

  const handleCreate = (values: QuotationFormValues) => {
    const items = values.quotation_items?.length ? values.quotation_items : [];
    if (items.length === 0) {
      message.error('Add at least one line item');
      return;
    }
    createMutation.mutate({
      ...values,
      date: values.date.format('YYYY-MM-DD'),
      expiration_date: values.expiration_date.format('YYYY-MM-DD'),
      quotation_items: items,
    });
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Space align="center" style={{ justifyContent: 'space-between', width: '100%' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Quotations
          </Typography.Title>
          <Typography.Text type="secondary">
            Generate quotations and share offers with prospects.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setDrawerOpen(true)}>
          New Quotation
        </Button>
      </Space>
      <Card>
        <Table<Quotation>
          rowKey="id"
          columns={columns}
          dataSource={quotations}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title="Create Quotation"
        width={640}
        destroyOnClose
        open={isDrawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Form<QuotationFormValues>
          layout="vertical"
          form={form}
          onFinish={handleCreate}
          initialValues={{
            status: 'QUOTATION',
            date: dayjs(),
            expiration_date: dayjs().add(14, 'day'),
          }}
        >
          <Form.Item name="customer_id" label="Customer" rules={[{ required: true, message: 'Select customer' }]}> 
            <Select
              showSearch
              placeholder="Customer"
              optionFilterProp="label"
              options={customers.map((customer) => ({ label: customer.name, value: customer.id }))}
            />
          </Form.Item>
          <Space size="large" wrap>
            <Form.Item name="date" label="Date" rules={[{ required: true }]}>
              <DatePicker format="YYYY-MM-DD" />
            </Form.Item>
            <Form.Item name="expiration_date" label="Expiration" rules={[{ required: true }]}>
              <DatePicker format="YYYY-MM-DD" />
            </Form.Item>
          </Space>
          <Form.Item
            name="invoicing_and_shipping_address"
            label="Billing & Shipping Address"
            rules={[{ required: true, message: 'Enter address' }]}
          >
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="status" label="Status">
            <Select
              options={[
                { label: 'Quotation', value: 'QUOTATION' },
                { label: 'Negotiation', value: 'NEGOTIATION' },
                { label: 'Approved', value: 'APPROVED' },
                { label: 'Rejected', value: 'REJECTED' },
              ]}
            />
          </Form.Item>

          <Form.List name="quotation_items">
            {(fields, { add, remove }) => (
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Typography.Title level={5}>Line Items</Typography.Title>
                {fields.map((field) => (
                  <QuotationItemFields key={field.key} name={field.name} remove={remove} products={products} />
                ))}
                <Button type="dashed" onClick={() => add({ quantity: 1 } as QuotationItemCreatePayload)} block>
                  Add Item
                </Button>
              </Space>
            )}
          </Form.List>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={createMutation.isPending}>
                Create Quotation
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

export default QuotationsPage;
