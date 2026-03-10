import { Modal, Form, Input, Select, Button, message, Space } from 'antd';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { useQueryClient, useMutation } from '@tanstack/react-query';
import axios from 'axios';

interface InspectionPointFormProps {
  visible: boolean;
  onClose: () => void;
  initialValues?: any;
}

export const InspectionPointForm = ({
  visible,
  onClose,
  initialValues,
}: InspectionPointFormProps) => {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  // Temporary direct mutation until hook is created
  const createMutation = useMutation({
    mutationFn: (data: any) => axios.post('/api/quality/inspections/points', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inspection-points'] });
      message.success('Inspection point created');
      onClose();
      form.resetFields();
    },
  });

  const handleSubmit = (values: any) => {
    createMutation.mutate(values);
  };

  return (
    <Modal
      title={initialValues ? "Edit Inspection Point" : "Create Inspection Point"}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={700}
      destroyOnHidden
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={initialValues || { inspection_type: 'in_process' }}
      >
        <Form.Item
          name="name"
          label="Name"
          rules={[{ required: true, message: 'Please enter name' }]}
        >
          <Input placeholder="e.g., Final Assembly Check" />
        </Form.Item>

        <Form.Item
          name="inspection_type"
          label="Type"
          rules={[{ required: true }]}
        >
          <Select
            options={[
              { label: 'Receiving', value: 'receiving' },
              { label: 'In Process', value: 'in_process' },
              { label: 'Final', value: 'final' },
              { label: 'Patrol', value: 'patrol' },
            ]}
          />
        </Form.Item>

        <Form.Item name="description" label="Description">
          <Input.TextArea rows={2} />
        </Form.Item>

        <div className="bg-gray-50 p-4 rounded-md mb-4">
          <Form.List name="checklist">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                    <Form.Item
                      {...restField}
                      name={[name, 'item']}
                      rules={[{ required: true, message: 'Missing item' }]}
                      className="mb-0 w-64"
                    >
                      <Input placeholder="Checklist item" />
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, 'specification']}
                      className="mb-0 w-48"
                    >
                      <Input placeholder="Spec (optional)" />
                    </Form.Item>
                    <MinusCircleOutlined onClick={() => remove(name)} />
                  </Space>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                    Add Checklist Item
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>
        </div>

        <div className="flex justify-end gap-2">
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" htmlType="submit" loading={createMutation.isPending}>
            Save Inspection Point
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

