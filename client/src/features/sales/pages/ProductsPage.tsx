import { EditOutlined, PlusOutlined } from '@ant-design/icons';
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
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { productsApi } from '@/features/sales/api';
import type { Product, ProductCreatePayload, ProductUpdatePayload } from '@/features/sales/types';

interface ProductFormValues extends ProductCreatePayload {
  name?: string;
  model_number?: string;
}

type Mode = 'create' | 'edit';

const inverterOptions = [
  { label: 'Grid-tied', value: 'GRID_TIED' },
  { label: 'Off-grid', value: 'OFF_GRID' },
  { label: 'Hybrid', value: 'HYBRID' },
  { label: 'Micro', value: 'MICRO' },
  { label: 'String', value: 'STRING' },
];

const ProductsPage = () => {
  const { message } = AntdApp.useApp();
  const [drawerMode, setDrawerMode] = useState<Mode>('create');
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<ProductFormValues>();

  const {
    data: products = [],
    isLoading,
    refetch,
  } = useQuery<Product[]>({
    queryKey: ['sales', 'products', 'list'],
    queryFn: () => productsApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: ProductCreatePayload) => productsApi.create(values),
    onSuccess: () => {
      message.success('Product created');
      refetch();
    },
    onError: () => message.error('Unable to create product'),
  });

  const updateMutation = useMutation({
    mutationFn: (values: ProductUpdatePayload) =>
      editingProduct ? productsApi.update(editingProduct.id, values) : Promise.resolve(editingProduct),
    onSuccess: () => {
      message.success('Product updated');
      refetch();
    },
    onError: () => message.error('Unable to update product'),
  });

  const openCreateDrawer = () => {
    setDrawerMode('create');
    setEditingProduct(null);
    form.resetFields();
    setDrawerOpen(true);
  };

  const openEditDrawer = (product: Product) => {
    setDrawerMode('edit');
    setEditingProduct(product);
    form.setFieldsValue({
      description: product.description,
      price: product.price,
      inverter_type: product.inverter_type,
      power_rating: product.power_rating,
      frequency: product.frequency,
      efficiency: product.efficiency,
      surge_power: product.surge_power,
      warranty_years: product.warranty_years,
      input_voltage: product.input_voltage,
      output_voltage: product.output_voltage,
    });
    setDrawerOpen(true);
  };

  const handleSubmit = (values: ProductFormValues) => {
    if (drawerMode === 'create') {
      createMutation.mutate(values, {
        onSuccess: () => {
          form.resetFields();
          setEditingProduct(null);
          setDrawerOpen(false);
        },
      });
    } else if (editingProduct) {
      updateMutation.mutate(values, {
        onSuccess: () => {
          setEditingProduct(null);
          setDrawerOpen(false);
        },
      });
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  const columns: ColumnsType<Product> = useMemo(
    () => [
      { title: 'Product', dataIndex: 'product_name', key: 'product_name' },
      { title: 'Model', dataIndex: 'model_number', key: 'model_number' },
      { title: 'Price', dataIndex: 'price', key: 'price' },
      { title: 'Power Rating (W)', dataIndex: 'power_rating', key: 'power_rating' },
      { title: 'Efficiency', dataIndex: 'efficiency', key: 'efficiency' },
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
            Products
          </Typography.Title>
          <Typography.Text type="secondary">Manage product catalog and specifications.</Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreateDrawer}>
          Add Product
        </Button>
      </div>
      <Card>
        <Table<Product>
          rowKey="id"
          dataSource={products || []}
          columns={columns}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title={drawerMode === 'create' ? 'Add Product' : `Edit ${editingProduct?.product_name ?? 'Product'}`}
        width={580}
        destroyOnHidden
        open={isDrawerOpen}
        onClose={() => {
          setEditingProduct(null);
          setDrawerMode('create');
          form.resetFields();
          setDrawerOpen(false);
        }}
      >
        <Form<ProductFormValues> layout="vertical" form={form} onFinish={handleSubmit}>
          <Form.Item name="description" label="Description" rules={[{ required: true }]}> 
            <Input placeholder="Product description" />
          </Form.Item>
          <Form.Item name="price" label="Price" rules={[{ required: true }]}> 
            <Input placeholder="0.00" />
          </Form.Item>
          <Form.Item name="inverter_type" label="Inverter Type" rules={[{ required: true }]}> 
            <Select options={inverterOptions} />
          </Form.Item>
          <Space size="large" wrap>
            <Form.Item name="power_rating" label="Power Rating" rules={[{ required: true }]}> 
              <Space.Compact>
                <InputNumber min={0} style={{ width: '100%' }} />
                <Input style={{ width: 50 }} defaultValue="W" disabled />
              </Space.Compact>
            </Form.Item>
            <Form.Item name="surge_power" label="Surge Power" rules={[{ required: true }]}> 
              <Space.Compact>
                <InputNumber min={0} style={{ width: '100%' }} />
                <Input style={{ width: 50 }} defaultValue="W" disabled />
              </Space.Compact>
            </Form.Item>
            <Form.Item name="warranty_years" label="Warranty" rules={[{ required: true }]}> 
              <Space.Compact>
                <InputNumber min={0} style={{ width: '100%' }} />
                <Input style={{ width: 50 }} defaultValue="yrs" disabled />
              </Space.Compact>
            </Form.Item>
          </Space>
          <Space size="large" wrap>
            <Form.Item name="frequency" label="Frequency" rules={[{ required: true }]}> 
              <Space.Compact>
                <Input placeholder="50" />
                <Input style={{ width: 50 }} defaultValue="Hz" disabled />
              </Space.Compact>
            </Form.Item>
            <Form.Item name="efficiency" label="Efficiency" rules={[{ required: true }]}> 
              <Input placeholder="0.92" />
            </Form.Item>
          </Space>
          <Space size="large" wrap>
            <Form.Item name="input_voltage" label="Input Voltage" rules={[{ required: true }]}> 
              <Space.Compact>
                <Input placeholder="220" />
                <Input style={{ width: 50 }} defaultValue="V" disabled />
              </Space.Compact>
            </Form.Item>
            <Form.Item name="output_voltage" label="Output Voltage" rules={[{ required: true }]}> 
              <Space.Compact>
                <Input placeholder="240" />
                <Input style={{ width: 50 }} defaultValue="V" disabled />
              </Space.Compact>
            </Form.Item>
          </Space>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={isSubmitting}>
                {drawerMode === 'create' ? 'Create Product' : 'Save Changes'}
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

export default ProductsPage;


