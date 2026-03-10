import { App as AntdApp, Button, Card, Form, Input, InputNumber, Select, Space, Typography } from 'antd';
import { useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { componentsApi, suppliersApi } from '@/features/inventory/api';
import type {
  Component,
  ComponentCreatePayload,
  ComponentUpdatePayload,
  Supplier,
} from '@/features/inventory/types';

interface ComponentFormValues extends ComponentCreatePayload {}

const ComponentFormPage = () => {
  const [form] = Form.useForm<ComponentFormValues>();
  const { message } = AntdApp.useApp();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditMode = Boolean(id);

  const { data: suppliers = [] } = useQuery<Supplier[]>({
    queryKey: ['inventory', 'suppliers', 'options'],
    queryFn: () => suppliersApi.list({ limit: 100 }),
  });

  const { data: component, isLoading } = useQuery<Component | null>({
    queryKey: ['inventory', 'components', id],
    queryFn: () => (id ? componentsApi.retrieve(parseInt(id, 10)) : Promise.resolve(null)),
    enabled: isEditMode,
  });

  useEffect(() => {
    if (component) {
      form.setFieldsValue({
        name: component.name,
        description: component.description ?? '',
        quantity: component.quantity,
        reorder_level: component.reorder_level,
        reorder_quantity: component.reorder_quantity,
        unit_of_measure: component.unit_of_measure,
        supplier_id: component.supplier_id ?? undefined,
        cost: component.cost,
        category_id: component.category_id ?? undefined,
      });
    } else if (!isEditMode) {
      form.resetFields();
      form.setFieldsValue({ unit_of_measure: 'pcs', quantity: 0 });
    }
  }, [component, form, isEditMode]);

  const createMutation = useMutation({
    mutationFn: (values: ComponentCreatePayload) => componentsApi.create(values),
    onSuccess: () => {
      message.success('Component created');
      navigate('/inventory/components');
    },
    onError: () => message.error('Unable to create component'),
  });

  const updateMutation = useMutation({
    mutationFn: (values: ComponentUpdatePayload) => componentsApi.update(parseInt(id ?? '0', 10), values),
    onSuccess: () => {
      message.success('Component updated');
      navigate('/inventory/components');
    },
    onError: () => message.error('Unable to update component'),
  });

  const handleSubmit = (values: ComponentFormValues) => {
    const payload = {
      ...values,
      supplier_id: values.supplier_id ?? null,
      category_id: values.category_id ?? null,
    };

    if (isEditMode) {
      updateMutation.mutate(payload);
    } else {
      createMutation.mutate(payload);
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <Card
      title={isEditMode ? 'Edit Component' : 'New Component'}
      loading={isEditMode && isLoading}
      extra={
        <Button type="link" onClick={() => navigate('/inventory/components')}>
          Back to list
        </Button>
      }
    >
      <Form<ComponentFormValues>
        layout="vertical"
        form={form}
        onFinish={handleSubmit}
        initialValues={{ unit_of_measure: 'pcs', quantity: 0, reorder_level: 0, reorder_quantity: 0, cost: '0.0' }}
      >
        <Typography.Title level={4}>Basic Information</Typography.Title>
        <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Enter a component name' }]}> 
          <Input placeholder="Component name" />
        </Form.Item>
        <Form.Item name="description" label="Description">
          <Input.TextArea rows={4} placeholder="Describe the component" />
        </Form.Item>

        <Space size="large" wrap>
          <Form.Item
            name="quantity"
            label="On-hand Quantity"
            rules={[{ required: true, message: 'Specify a quantity' }]}
          >
            <InputNumber min={0} />
          </Form.Item>
          <Form.Item name="reorder_level" label="Reorder Level" rules={[{ required: true }]}> 
            <InputNumber min={0} />
          </Form.Item>
          <Form.Item name="reorder_quantity" label="Reorder Quantity" rules={[{ required: true }]}> 
            <InputNumber min={0} />
          </Form.Item>
        </Space>

        <Space size="large" wrap>
          <Form.Item name="unit_of_measure" label="Unit of Measure" rules={[{ required: true }]}> 
            <Select
              options={[
                { label: 'Pieces (pcs)', value: 'pcs' },
                { label: 'Kilograms (kg)', value: 'kg' },
                { label: 'Meters (m)', value: 'm' },
              ]}
            />
          </Form.Item>
          <Form.Item name="cost" label="Cost" rules={[{ required: true }]}> 
            <Input placeholder="0.00" />
          </Form.Item>
        </Space>

        <Form.Item name="supplier_id" label="Supplier">
          <Select
            allowClear
            placeholder="Select supplier"
            options={suppliers.map((supplier) => ({
              label: supplier.name,
              value: supplier.id,
            }))}
          />
        </Form.Item>

        <Form.Item name="category_id" label="Category">
          <InputNumber min={0} placeholder="Category ID" style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={isSubmitting}>
              {isEditMode ? 'Update Component' : 'Create Component'}
            </Button>
            <Button htmlType="button" onClick={() => form.resetFields()}>
              Reset
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ComponentFormPage;

