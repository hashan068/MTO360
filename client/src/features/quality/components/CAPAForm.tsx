import { Modal, Form, Input, Button, message } from 'antd';
import { useCreateCAPA } from '../hooks/useCAPAs';

interface CAPAFormProps {
  visible: boolean;
  onClose: () => void;
  ncrId?: number;
}

export const CAPAForm = ({ visible, onClose, ncrId }: CAPAFormProps) => {
  const [form] = Form.useForm();
  const createCAPA = useCreateCAPA();

  const handleSubmit = async (values: any) => {
    try {
      await createCAPA.mutateAsync({
        ...values,
        ncr_id: ncrId,
        owner_id: 1, // TODO: Get from auth context
      });
      message.success('CAPA created successfully');
      form.resetFields();
      onClose();
    } catch (error) {
      message.error('Failed to create CAPA');
    }
  };

  return (
    <Modal
      title="Create Corrective Action (CAPA)"
      open={visible}
      onCancel={onClose}
      footer={null}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Form.Item
          name="title"
          label="Title"
          rules={[{ required: true, message: 'Please enter title' }]}
        >
          <Input placeholder="e.g., Fix calibration process" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description"
          rules={[{ required: true, message: 'Please enter description' }]}
        >
          <Input.TextArea rows={3} placeholder="Describe the issue..." />
        </Form.Item>

        <Form.Item
          name="root_cause"
          label="Root Cause"
          rules={[{ required: true, message: 'Please enter root cause' }]}
        >
          <Input.TextArea rows={3} placeholder="Root cause analysis..." />
        </Form.Item>

        <div className="flex justify-end gap-2 mt-4">
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" htmlType="submit" loading={createCAPA.isPending}>
            Create CAPA
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

