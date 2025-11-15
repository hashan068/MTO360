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
import { suppliersApi } from '@/features/inventory/api';
import type { Supplier, SupplierCreatePayload, SupplierUpdatePayload } from '@/features/inventory/types';

interface SupplierFormValues extends SupplierCreatePayload {}

type Mode = 'create' | 'edit';

const SuppliersPage = () => {
  const { message } = AntdApp.useApp();
  const [drawerMode, setDrawerMode] = useState<Mode>('create');
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null);
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<SupplierFormValues>();

  const {
    data: suppliers = [],
    isLoading,
    refetch,
  } = useQuery<Supplier[]>({
    queryKey: ['inventory', 'suppliers', 'list'],
    queryFn: () => suppliersApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: SupplierCreatePayload) => suppliersApi.create(values),
    onSuccess: () => {
      message.success('Supplier added');
      refetch();
    },
    onError: () => message.error('Unable to add supplier'),
  });

  const updateMutation = useMutation({
    mutationFn: (values: SupplierUpdatePayload) =>
      editingSupplier ? suppliersApi.update(editingSupplier.id, values) : Promise.resolve(editingSupplier),
    onSuccess: () => {
      message.success('Supplier updated');
      refetch();
    },
    onError: () => message.error('Unable to update supplier'),
  });

  const openCreateDrawer = () => {
    setDrawerMode('create');
    setEditingSupplier(null);
    form.resetFields();
    setDrawerOpen(true);
  };

  const openEditDrawer = (supplier: Supplier) => {
    setDrawerMode('edit');
    setEditingSupplier(supplier);
    form.setFieldsValue({
      name: supplier.name,
      email: supplier.email ?? '',
      address: supplier.address ?? '',
      website: supplier.website ?? '',
      is_active: supplier.is_active,
      notes: supplier.notes ?? '',
    });
    setDrawerOpen(true);
  };

  const handleSubmit = (values: SupplierFormValues) => {
    const payload = { ...values, notes: values.notes ?? '', address: values.address ?? '', website: values.website ?? '' };
    if (drawerMode === 'create') {
      createMutation.mutate(payload, {
        onSuccess: () => {
          form.resetFields();
          setEditingSupplier(null);
          setDrawerOpen(false);
        },
      });
    } else if (editingSupplier) {
      updateMutation.mutate(payload, {
        onSuccess: () => {
          setEditingSupplier(null);
          setDrawerOpen(false);
        },
      });
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  const columns: ColumnsType<Supplier> = useMemo(
    () => [
      { title: 'Supplier', dataIndex: 'name', key: 'name' },
      { title: 'Email', dataIndex: 'email', key: 'email' },
      { title: 'Website', dataIndex: 'website', key: 'website' },
      {
        title: 'Status',
        dataIndex: 'is_active',
        key: 'is_active',
        render: (isActive: boolean) => <Tag color={isActive ? 'green' : 'red'}>{isActive ? 'Active' : 'Inactive'}</Tag>,
      },
      { title: 'Notes', dataIndex: 'notes', key: 'notes' },
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
            Suppliers
          </Typography.Title>
          <Typography.Text type="secondary">
            Maintain partner details and track supplier performance.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreateDrawer}>
          Add Supplier
        </Button>
      </div>
      <Card>
        <Table<Supplier>
          rowKey="id"
          dataSource={suppliers}
          columns={columns}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title={drawerMode === 'create' ? 'Add Supplier' : `Edit ${editingSupplier?.name}`}
        width={480}
        destroyOnClose
        open={isDrawerOpen}
        onClose={() => {
          setEditingSupplier(null);
          setDrawerMode('create');
          form.resetFields();
          setDrawerOpen(false);
        }}
      >
        <Form<SupplierFormValues> layout="vertical" form={form} onFinish={handleSubmit} initialValues={{ is_active: true }}>
          <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Enter supplier name' }]}> 
            <Input placeholder="Supplier name" />
          </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ type: 'email', message: 'Enter valid email' }]}> 
            <Input placeholder="contact@example.com" />
          </Form.Item>
          <Form.Item name="address" label="Address">
            <Input placeholder="Address" />
          </Form.Item>
          <Form.Item name="website" label="Website">
            <Input placeholder="https://" />
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
                {drawerMode === 'create' ? 'Create Supplier' : 'Save Changes'}
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

export default SuppliersPage;
