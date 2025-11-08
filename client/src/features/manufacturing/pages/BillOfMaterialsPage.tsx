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
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { billOfMaterialsApi } from '@/features/manufacturing/api';
import { componentsApi } from '@/features/inventory/api';
import { productsApi } from '@/features/sales/api';
import type {
  BillOfMaterial,
  BillOfMaterialCreatePayload,
  BillOfMaterialItemCreatePayload,
} from '@/features/manufacturing/types';
import type { Component } from '@/features/inventory/types';
import type { Product } from '@/features/sales/types';

const BillOfMaterialsPage = () => {
  const { message } = AntdApp.useApp();
  const [isDrawerOpen, setDrawerOpen] = useState(false);
  const [form] = Form.useForm<BillOfMaterialCreatePayload>();

  const {
    data: boms = [],
    isLoading,
    refetch,
  } = useQuery<BillOfMaterial[]>({
    queryKey: ['manufacturing', 'boms', 'list'],
    queryFn: () => billOfMaterialsApi.list({ limit: 200 }),
  });

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['sales', 'products', 'bom-options'],
    queryFn: () => productsApi.list({ limit: 200 }),
  });

  const { data: components = [] } = useQuery<Component[]>({
    queryKey: ['inventory', 'components', 'bom-options'],
    queryFn: () => componentsApi.list({ limit: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: BillOfMaterialCreatePayload) => billOfMaterialsApi.create(values),
    onSuccess: () => {
      message.success('BOM created');
      setDrawerOpen(false);
      form.resetFields();
      refetch();
    },
    onError: () => message.error('Unable to create BOM'),
  });

  const columns: ColumnsType<BillOfMaterial> = [
    { title: 'BOM', dataIndex: 'name', key: 'name' },
    { title: 'Product', dataIndex: 'product_name', key: 'product_name' },
    { title: 'Items', dataIndex: 'bom_items', key: 'bom_items', render: (items) => items?.length ?? 0 },
    { title: 'Updated', dataIndex: 'updated_at', key: 'updated_at' },
  ];

  const handleCreate = (values: BillOfMaterialCreatePayload) => {
    if (!values.bom_items?.length) {
      message.error('Add at least one component');
      return;
    }
    createMutation.mutate(values);
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Space align="center" style={{ justifyContent: 'space-between', width: '100%' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Bills of Materials
          </Typography.Title>
          <Typography.Text type="secondary">
            Define component groupings used in manufacturing orders.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setDrawerOpen(true)}>
          New BOM
        </Button>
      </Space>
      <Card>
        <Table<BillOfMaterial>
          rowKey="id"
          dataSource={boms}
          columns={columns}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Drawer
        title="Create Bill of Material"
        width={640}
        destroyOnClose
        open={isDrawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Form<BillOfMaterialCreatePayload>
          layout="vertical"
          form={form}
          onFinish={handleCreate}
        >
          <Form.Item name="name" label="BOM Name" rules={[{ required: true }]}> 
            <Input placeholder="Assembly name" />
          </Form.Item>
          <Form.Item name="product_id" label="Product">
            <Select
              allowClear
              placeholder="Select product"
              options={products.map((product) => ({
                label: product.product_name ?? product.description,
                value: product.id,
              }))}
            />
          </Form.Item>
          <Form.List name="bom_items">
            {(fields, { add, remove }) => (
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Typography.Title level={5}>Components</Typography.Title>
                {fields.map((field) => (
                  <Space key={field.key} align="baseline" wrap style={{ width: '100%' }}>
                    <Form.Item
                      name={[field.name, 'component_id']}
                      label="Component"
                      rules={[{ required: true }]}
                    >
                      <Select
                        showSearch
                        placeholder="Component"
                        optionFilterProp="label"
                        options={components.map((component) => ({ label: component.name, value: component.id }))}
                        style={{ minWidth: 220 }}
                      />
                    </Form.Item>
                    <Form.Item
                      name={[field.name, 'quantity']}
                      label="Quantity"
                      rules={[{ required: true }]}
                    >
                      <InputNumber min={1} />
                    </Form.Item>
                    <Button type="link" danger onClick={() => remove(field.name)}>
                      Remove
                    </Button>
                  </Space>
                ))}
                <Button type="dashed" onClick={() => add({ quantity: 1 } as BillOfMaterialItemCreatePayload)} block>
                  Add Component
                </Button>
              </Space>
            )}
          </Form.List>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={createMutation.isPending}>
                Create BOM
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

export default BillOfMaterialsPage;
