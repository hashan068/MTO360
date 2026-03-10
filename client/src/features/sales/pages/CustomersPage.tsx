import { EditOutlined, PlusOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  Drawer,
  Form,
  Input,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { customersApi } from '@/features/sales/api';
import type { Customer, CustomerCreatePayload, CustomerUpdatePayload } from '@/features/sales/types';

interface CustomerFormValues extends CustomerCreatePayload {}

type Mode = 'create' | 'edit';

const CustomersPage = () => {
  const { message } = AntdApp.useApp();
  const [drawerMode, setDrawerMode] = useState<Mode>('create');
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<CustomerFormValues>();

  const {
    data: customers = [],
    isLoading,
    refetch,
  } = useQuery<Customer[]>({
    queryKey: ['sales', 'customers', 'list'],
    queryFn: () => customersApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: CustomerCreatePayload) => customersApi.create(values),
    onSuccess: () => {
      message.success('Customer created');
      refetch();
    },
    onError: () => message.error('Unable to create customer'),
  });

  const updateMutation = useMutation({
    mutationFn: (values: CustomerUpdatePayload) =>
      editingCustomer ? customersApi.update(editingCustomer.id, values) : Promise.resolve(editingCustomer),
    onSuccess: () => {
      message.success('Customer updated');
      refetch();
    },
    onError: () => message.error('Unable to update customer'),
  });

  const openCreateDrawer = () => {
    setDrawerMode('create');
    setEditingCustomer(null);
    form.resetFields();
    setDrawerOpen(true);
  };

  const openEditDrawer = (customer: Customer) => {
    setDrawerMode('edit');
    setEditingCustomer(customer);
    form.setFieldsValue({
      name: customer.name,
      email: customer.email,
      phone: customer.phone,
      street_address: customer.street_address,
      city: customer.city,
      is_active: customer.is_active,
      notes: customer.notes ?? '',
    });
    setDrawerOpen(true);
  };

  const handleSubmit = (values: CustomerFormValues) => {
    const payload = { ...values, notes: values.notes ?? '' };
    if (drawerMode === 'create') {
      createMutation.mutate(payload, {
        onSuccess: () => {
          form.resetFields();
          setEditingCustomer(null);
          setDrawerOpen(false);
        },
      });
    } else if (editingCustomer) {
      updateMutation.mutate(payload, {
        onSuccess: () => {
          setEditingCustomer(null);
          setDrawerOpen(false);
        },
      });
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  const columns: ColumnsType<Customer> = useMemo(
    () => [
      { title: 'Customer', dataIndex: 'name', key: 'name' },
      { title: 'Email', dataIndex: 'email', key: 'email' },
      { title: 'Phone', dataIndex: 'phone', key: 'phone' },
      { title: 'City', dataIndex: 'city', key: 'city' },
      {
        title: 'Status',
        dataIndex: 'is_active',
        key: 'is_active',
        render: (isActive: boolean) => <Tag color={isActive ? 'green' : 'red'}>{isActive ? 'Active' : 'Inactive'}</Tag>,
      },
      {
        key: 'actions',
        width: 110,
        render: (_, record) => (
          <Button type="link" icon={<EditOutlined />} onClick={() => openEditDrawer(record)}>
            Edit
          </Button>
        ),
      },
    ],
    []
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            Customers
          </Typography.Title>
          <Typography.Text type="secondary">
            Manage customer contact details and account status.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreateDrawer}>
          Add Customer
        </Button>
      </div>
      <Card>
        <Table<Customer>
          rowKey="id"
          columns={columns}
          dataSource={customers || []}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title={drawerMode === 'create' ? 'Add Customer' : `Edit ${editingCustomer?.name}`}
        width={520}
        destroyOnHidden
        open={isDrawerOpen}
        onClose={() => {
          setEditingCustomer(null);
          setDrawerMode('create');
          form.resetFields();
          setDrawerOpen(false);
        }}
      >
        <Form<CustomerFormValues> layout="vertical" form={form} initialValues={{ is_active: true }} onFinish={handleSubmit}>
          <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Enter customer name' }]}> 
            <Input placeholder="Customer name" />
          </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}> 
            <Input placeholder="customer@example.com" />
          </Form.Item>
          <Form.Item name="phone" label="Phone" rules={[{ required: true }]}> 
            <Input placeholder="Phone number" />
          </Form.Item>
          <Form.Item name="street_address" label="Street Address" rules={[{ required: true }]}> 
            <Input placeholder="Street address" />
          </Form.Item>
          <Form.Item name="city" label="City" rules={[{ required: true }]}> 
            <Input placeholder="City" />
          </Form.Item>
          <Form.Item name="notes" label="Notes">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="is_active" label="Active" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={isSubmitting}>
                {drawerMode === 'create' ? 'Create Customer' : 'Save Changes'}
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

export default CustomersPage;


