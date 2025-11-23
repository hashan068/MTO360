/**
 * Operation Route Form Component
 * Modal form for creating operation routes (basic info only)
 */
import { useEffect } from 'react';
import { Modal, Form, Input, InputNumber, Switch } from 'antd';
import { useCreateOperationRoute, useUpdateOperationRoute, useOperationRoute } from '../hooks/useOperationRoutes';
import type { OperationRouteCreate } from '@/types/manufacturing';

interface OperationRouteFormProps {
  open: boolean;
  editingId?: number;
  onClose: () => void;
}

export const OperationRouteForm = ({ open, editingId, onClose }: OperationRouteFormProps) => {
  const [form] = Form.useForm<OperationRouteCreate>();
  const isEditing = !!editingId;

  const { data: route } = useOperationRoute(editingId!);
  const createMutation = useCreateOperationRoute();
  const updateMutation = useUpdateOperationRoute();

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  useEffect(() => {
    if (isEditing && route) {
      form.setFieldsValue({
        name: route.name,
        product_id: route.product_id,
        bom_id: route.bom_id,
        is_active: route.is_active,
      });
    } else {
      form.resetFields();
    }
  }, [route, isEditing, form]);

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      if (isEditing && editingId) {
        await updateMutation.mutateAsync({ id: editingId, data: values });
      } else {
        await createMutation.mutateAsync(values);
      }

      form.resetFields();
      onClose();
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title={isEditing ? 'Edit Operation Route' : 'Create Operation Route'}
      open={open}
      onOk={handleSubmit}
      onCancel={handleCancel}
      confirmLoading={isSubmitting}
      okText={isEditing ? 'Update' : 'Create'}
      width={600}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          is_active: true,
        }}
      >
        <Form.Item
          name="name"
          label="Route Name"
          rules={[
            { required: true, message: 'Please enter route name' },
            { max: 200, message: 'Name must be less than 200 characters' },
          ]}
        >
          <Input placeholder="e.g., Standard Assembly Route" />
        </Form.Item>

        <Form.Item
          name="product_id"
          label="Product ID"
          help="Optional - Link this route to a specific product"
        >
          <InputNumber style={{ width: '100%' }} min={1} placeholder="Enter product ID" />
        </Form.Item>

        <Form.Item
          name="bom_id"
          label="BOM ID"
          help="Optional - Link this route to a specific BOM"
        >
          <InputNumber style={{ width: '100%' }} min={1} placeholder="Enter BOM ID" />
        </Form.Item>

        <Form.Item
          name="is_active"
          label="Status"
          valuePropName="checked"
        >
          <Switch checkedChildren="Active" unCheckedChildren="Inactive" />
        </Form.Item>

        {!isEditing && (
          <div className="text-sm text-gray-500 mt-4">
            <p>Note: After creating the route, you can add operations on the route detail page.</p>
          </div>
        )}
      </Form>
    </Modal>
  );
};
