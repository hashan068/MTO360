import { Modal, Form, Input, Select, Button, message } from 'antd';
import { useCreateNCR } from '../hooks/useNCRs';

interface NCRFormProps {
  visible: boolean;
  onClose: () => void;
  defectId?: number;
  manufacturingOrderId?: number;
}

export const NCRForm = ({
  visible,
  onClose,
  defectId,
  manufacturingOrderId,
}: NCRFormProps) => {
  const [form] = Form.useForm();
  const createNCR = useCreateNCR();

  const handleSubmit = async (values: any) => {
    try {
      await createNCR.mutateAsync({
        ...values,
        defect_id: defectId,
        manufacturing_order_id: manufacturingOrderId,
        owner_id: 1, // TODO: Get from auth context
      });
      message.success('NCR created successfully');
      form.resetFields();
      onClose();
    } catch (error) {
      message.error('Failed to create NCR');
    }
  };

  return (
    <Modal
      title="Create Non-Conformance Report"
      open={visible}
      onCancel={onClose}
      footer={null}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          priority: 'medium',
        }}
      >
        <Form.Item
          name="priority"
          label="Priority"
          rules={[{ required: true, message: 'Please select priority' }]}
        >
          <Select
            options={[
              { label: 'Critical', value: 'critical' },
              { label: 'High', value: 'high' },
              { label: 'Medium', value: 'medium' },
              { label: 'Low', value: 'low' },
            ]}
          />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description"
          rules={[{ required: true, message: 'Please enter description' }]}
        >
          <Input.TextArea rows={4} placeholder="Describe the non-conformance..." />
        </Form.Item>

        <div className="flex justify-end gap-2 mt-4">
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" htmlType="submit" loading={createNCR.isPending}>
            Create NCR
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

