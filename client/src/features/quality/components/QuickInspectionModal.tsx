import { Modal, Form, Select, Radio, Input, Upload, Button, message } from 'antd';
import { UploadOutlined, CameraOutlined } from '@ant-design/icons';
import { useRecordInspection } from '../hooks/useInspections';
import type { InspectionResult } from '../types';

interface QuickInspectionModalProps {
  visible: boolean;
  onClose: () => void;
  inspectionPointId?: number;
  moOperationId?: number;
  manufacturingOrderId?: number;
}

export const QuickInspectionModal = ({
  visible,
  onClose,
  inspectionPointId,
  moOperationId,
  manufacturingOrderId,
}: QuickInspectionModalProps) => {
  const [form] = Form.useForm();
  const recordInspection = useRecordInspection();

  const handleSubmit = async (values: any) => {
    try {
      await recordInspection.mutateAsync({
        inspection_point_id: values.inspection_point_id,
        result: values.result,
        inspector_id: 1, // TODO: Get from auth context
        mo_operation_id: moOperationId,
        manufacturing_order_id: manufacturingOrderId,
        notes: values.notes,
        measurements: values.measurements, // Assuming JSON input or specific fields
      });
      message.success('Inspection recorded successfully');
      form.resetFields();
      onClose();
    } catch (error) {
      message.error('Failed to record inspection');
    }
  };

  return (
    <Modal
      title="Quick Inspection Entry"
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
          inspection_point_id: inspectionPointId,
          result: 'pass',
        }}
      >
        <Form.Item
          name="inspection_point_id"
          label="Inspection Point"
          rules={[{ required: true, message: 'Please select inspection point' }]}
        >
          <Select
            placeholder="Select inspection point"
            options={[
              { label: 'Visual Check', value: 1 },
              { label: 'Dimensional Check', value: 2 },
              // TODO: Load from API
            ]}
            disabled={!!inspectionPointId}
          />
        </Form.Item>

        <Form.Item
          name="result"
          label="Result"
          rules={[{ required: true, message: 'Please select result' }]}
        >
          <Radio.Group buttonStyle="solid" className="w-full flex">
            <Radio.Button value="pass" className="flex-1 text-center !bg-green-50 !text-green-600 !border-green-200 checked:!bg-green-500 checked:!text-white">
              PASS
            </Radio.Button>
            <Radio.Button value="conditional" className="flex-1 text-center !bg-orange-50 !text-orange-600 !border-orange-200 checked:!bg-orange-500 checked:!text-white">
              CONDITIONAL
            </Radio.Button>
            <Radio.Button value="fail" className="flex-1 text-center !bg-red-50 !text-red-600 !border-red-200 checked:!bg-red-500 checked:!text-white">
              FAIL
            </Radio.Button>
          </Radio.Group>
        </Form.Item>

        <Form.Item name="notes" label="Notes">
          <Input.TextArea rows={3} placeholder="Add any observations..." />
        </Form.Item>

        <Form.Item label="Photos">
          <Upload listType="picture-card">
            <div>
              <CameraOutlined />
              <div style={{ marginTop: 8 }}>Take Photo</div>
            </div>
          </Upload>
        </Form.Item>

        <div className="flex justify-end gap-2 mt-4">
          <Button onClick={onClose}>Cancel</Button>
          <Button type="primary" htmlType="submit" loading={recordInspection.isPending}>
            Submit Inspection
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

