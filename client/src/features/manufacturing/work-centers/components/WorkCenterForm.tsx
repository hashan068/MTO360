/**
 * Work Center Form Component
 * Modal form for creating/editing work centers
 */
import { useEffect } from 'react';
import { Modal, Form, Input, InputNumber, Switch } from 'antd';
import { useCreateWorkCenter, useUpdateWorkCenter, useWorkCenter } from '../hooks/useWorkCenters';
import type { WorkCenterCreate } from '@/types/manufacturing';

interface WorkCenterFormProps {
  open: boolean;
  editingId?: number;
  onClose: () => void;
}

export const WorkCenterForm = ({ open, editingId, onClose }: WorkCenterFormProps) => {
  const [form] = Form.useForm<WorkCenterCreate>();
  const isEditing = !!editingId;

  const { data: workCenter } = useWorkCenter(editingId!);
  const createMutation = useCreateWorkCenter();
  const updateMutation = useUpdateWorkCenter();

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  // Load work center data when editing
  useEffect(() => {
    if (isEditing && workCenter) {
      form.setFieldsValue({
        code: workCenter.code,
        name: workCenter.name,
        description: workCenter.description,
        capacity_hours_per_day: workCenter.capacity_hours_per_day,
        location: workCenter.location,
        is_active: workCenter.is_active,
      });
    } else {
      form.resetFields();
    }
  }, [workCenter, isEditing, form]);

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
      // Validation error or mutation error already handled by hooks
      console.error('Form submission error:', error);
    }
  };

  const handleCancel = () => {
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title={isEditing ? 'Edit Work Center' : 'Create Work Center'}
      open={open}
      onOk={handleSubmit}
      onCancel={handleCancel}
      confirmLoading={isSubmitting}
      okText={isEditing ? 'Update' : 'Create'}
      width={600}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          capacity_hours_per_day: 8,
          is_active: true,
        }}
      >
        <Form.Item
          name="code"
          label="Work Center Code"
          rules={[
            { required: true, message: 'Please enter work center code' },
            { max: 50, message: 'Code must be less than 50 characters' },
            { pattern: /^[A-Z0-9-_]+$/, message: 'Code must contain only uppercase letters, numbers, hyphens, and underscores' },
          ]}
        >
          <Input placeholder="e.g., WC-ASSY-01" />
        </Form.Item>

        <Form.Item
          name="name"
          label="Name"
          rules={[
            { required: true, message: 'Please enter work center name' },
            { max: 200, message: 'Name must be less than 200 characters' },
          ]}
        >
          <Input placeholder="e.g., Assembly Station 1" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description"
        >
          <Input.TextArea
            rows={3}
            placeholder="Optional description..."
            maxLength={500}
            showCount
          />
        </Form.Item>

        <Form.Item
          name="capacity_hours_per_day"
          label="Capacity (hours per day)"
          rules={[
            { required: true, message: 'Please enter capacity' },
            { type: 'number', min: 0.1, max: 24, message: 'Capacity must be between 0.1 and 24 hours' },
          ]}
        >
          <InputNumber
            style={{ width: '100%' }}
            min={0.1}
            max={24}
            step={0.5}
            precision={1}
            addonAfter="hours/day"
          />
        </Form.Item>

        <Form.Item
          name="location"
          label="Location"
        >
          <Input placeholder="e.g., Building A, Floor 2" />
        </Form.Item>

        <Form.Item
          name="is_active"
          label="Status"
          valuePropName="checked"
        >
          <Switch checkedChildren="Active" unCheckedChildren="Inactive" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

