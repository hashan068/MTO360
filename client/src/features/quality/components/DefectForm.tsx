import { Modal, Form, Input, Select, InputNumber, Button, message } from 'antd';
import { useCreateDefect } from '../hooks/useDefects';
import type { DefectSeverity } from '../types';

interface DefectFormProps {
  visible: boolean;
  onClose: () => void;
  moOperationId?: number;
  manufacturingOrderId?: number;
}

export const DefectForm = ({
  visible,
  onClose,
  moOperationId,
  manufacturingOrderId,
}: DefectFormProps) => {
  const [form] = Form.useForm();
  const createDefect = useCreateDefect();

  const handleSubmit = async (values: any) => {
    try {
      await createDefect.mutateAsync({
        ...values,
        mo_operation_id: moOperationId,
        manufacturing_order_id: manufacturingOrderId,
      });
      message.success('Defect reported successfully');
      form.resetFields();
      onClose();
    } catch (error) {
      message.error('Failed to report defect');
    }
  };

  return (
    <Modal
      title="Report Defect"
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
          severity: 'minor',
          quantity_affected: 1,
        }}
      >
        <Form.Item
          name="defect_type"
          label="Defect Type"
          rules={[{ required: true, message: 'Please select defect type' }]}
        >
          <Select
            placeholder="Select defect type"
            options={[
              { label: 'Dimensional', value: 'dimensional' },
              { label: 'Visual', value: 'visual' },
              { label: 'Material', value: 'material' },
              { label: 'Functionality', value: 'functionality' },
              { label: 'Documentation', value: 'documentation' },
            ]}
          />
        </Form.Item>

        <Form.Item
          name="severity"
          label="Severity"
          rules={[{ required: true, message: 'Please select severity' }]}
        >
          <Select
            options={[
              { label: 'Critical', value: 'critical' },
              { label: 'Major', value: 'major' },
              { label: 'Minor', value: 'minor' },
            ]}
          />
        </Form.Item>

        <Form.Item
          name="quantity_affected"
          label="Quantity Affected"
          rules={[{ required: true, message: 'Please enter quantity' }]}
        >
          <InputNumber min={1} className="w-full" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description"
          rules={[{ required: true, message: 'Please enter description' }]}
        >
          <Input.TextArea rows={4} placeholder="Describe the defect..." />
        </Form.Item>

        <div className="flex justify-end gap-2 mt-4">
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" htmlType="submit" loading={createDefect.isPending}>
            Report Defect
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

