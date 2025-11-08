import { PlusOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  Drawer,
  Form,
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
import { customersApi, productsApi, salesOrdersApi } from '@/features/sales/api';
import type {
  Customer,
  Product,
  SalesOrder,
  SalesOrderCreatePayload,
  SalesOrderItemCreatePayload,
} from '@/features/sales/types';
import { formatCurrency } from '@/shared/utils/format';

type SalesOrderFormValues = SalesOrderCreatePayload;

const statusColor: Record<SalesOrder['status'], string> = {
  PENDING: 'gold',
  PROCESSING: 'blue',
  FULFILLED: 'green',
  CANCELLED: 'red',
};

const SalesOrderItemFields = ({
  name,
  remove,
  products,
}: {
  name: number;
  remove: (index: number | number[]) => void;
  products: Product[];
}) => (
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
        options={products.map((product) => ({ label: product.product_name ?? product.description, value: product.id }))}
        style={{ minWidth: 200 }}
      />
    </Form.Item>
    <Form.Item name={[name, 'quantity']} label="Qty" rules={[{ required: true }]}>
      <InputNumber min={1} />
    </Form.Item>
    <Form.Item name={[name, 'price']} label="Price" rules={[{ required: true }]}>
      <InputNumber min={0} step={0.01} />
    </Form.Item>
    <Button type="link" danger onClick={() => remove(name)}>
      Remove
    </Button>
  </Space>
);

const SalesOrdersPage = () => {
  const { message } = AntdApp.useApp();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<SalesOrderFormValues>();

  const { data: customers = [] } = useQuery<Customer[]>({
    queryKey: ['sales', 'customers', 'options-orders'],
    queryFn: () => customersApi.list({ limit: 200 }),
  });

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['sales', 'products', 'options-orders'],
    queryFn: () => productsApi.list({ limit: 200 }),
  });

  const {
    data: salesOrders = [],
    isLoading,
    refetch,
  } = useQuery<SalesOrder[]>({
    queryKey: ['sales', 'orders', 'list'],
    queryFn: () => salesOrdersApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: SalesOrderCreatePayload) => salesOrdersApi.create(values),
    onSuccess: () => {
      message.success('Sales order created');
      setDrawerOpen(false);
      form.resetFields();
      refetch();
    },
    onError: () => message.error('Unable to create sales order'),
  });

  const columns: ColumnsType<SalesOrder> = [
    { title: 'Order', dataIndex: 'id', key: 'id', width: 100 },
    { title: 'Customer', dataIndex: 'customer_name', key: 'customer_name' },
    { title: 'Total', dataIndex: 'total_amount', key: 'total_amount', render: (value) => formatCurrency(value) },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 140,
      render: (value: SalesOrder['status']) => <Tag color={statusColor[value]}>{value}</Tag>,
    },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at' },
  ];

  const handleCreate = (values: SalesOrderFormValues) => {
    const items = values.order_items?.length ? values.order_items : [];
    if (items.length === 0) {
      message.error('Add at least one order line');
      return;
    }
    createMutation.mutate({ customer_id: values.customer_id, order_items: items });
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Space align="center" style={{ justifyContent: 'space-between', width: '100%' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Sales Orders
          </Typography.Title>
          <Typography.Text type="secondary">Convert quotations into orders and track fulfillment.</Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setDrawerOpen(true)}>
          New Sales Order
        </Button>
      </Space>
      <Card>
        <Table<SalesOrder>
          rowKey="id"
          columns={columns}
          dataSource={salesOrders}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title="Create Sales Order"
        width={640}
        destroyOnClose
        open={isDrawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Form<SalesOrderFormValues> layout="vertical" form={form} onFinish={handleCreate}>
          <Form.Item name="customer_id" label="Customer" rules={[{ required: true }]}> 
            <Select
              showSearch
              placeholder="Customer"
              optionFilterProp="label"
              options={customers.map((customer) => ({ label: customer.name, value: customer.id }))}
            />
          </Form.Item>

          <Form.List name="order_items">
            {(fields, { add, remove }) => (
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Typography.Title level={5}>Line Items</Typography.Title>
                {fields.map((field) => (
                  <SalesOrderItemFields key={field.key} name={field.name} remove={remove} products={products} />
                ))}
                <Button type="dashed" onClick={() => add({ quantity: 1 } as SalesOrderItemCreatePayload)} block>
                  Add Item
                </Button>
              </Space>
            )}
          </Form.List>

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
    </Space>
  );
};

export default SalesOrdersPage;
