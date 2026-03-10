/**
 * Create RFQ Page - Phase 2: RFQ & Competitive Bidding
 */
import { SaveOutlined, SendOutlined } from '@ant-design/icons';
import {
  Card,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Select,
  Button,
  Space,
  Typography,
  message,
  Transfer
} from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { rfqApi } from '../api/procurementApi';
import axios from 'axios';

const { TextArea } = Input;

interface Supplier {
  id: number;
  name: string;
  email: string;
}

const CreateRFQPage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form] = Form.useForm();
  const [selectedSuppliers, setSelectedSuppliers] = useState<number[]>([]);

  // Fetch components
  const { data: components = [] } = useQuery({
    queryKey: ['components'],
    queryFn: async () => {
      const { data } = await axios.get('/api/v1/components', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      return data;
    },
  });

  // Fetch suppliers
  const { data: suppliers = [] } = useQuery<Supplier[]>({
    queryKey: ['suppliers'],
    queryFn: async () => {
      const { data } = await axios.get<Supplier[]>('/api/v1/suppliers', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      return data;
    },
  });

  const createRFQMutation = useMutation({
    mutationFn: rfqApi.createRFQ,
    onSuccess: (data) => {
      message.success('RFQ created successfully!');
      queryClient.invalidateQueries({ queryKey: ['procurement', 'rfqs'] });
      navigate(`/procurement/rfqs/${data.id}`);
    },
    onError: () => {
      message.error('Failed to create RFQ');
    },
  });

  const handleSubmit = async (values: any) => {
    await createRFQMutation.mutateAsync({
      component_id: values.component_id,
      quantity: values.quantity,
      required_by_date: values.required_by_date.format('YYYY-MM-DD'),
      closing_datetime: values.closing_datetime.format('YYYY-MM-DDTHH:mm:ss'),
      specifications: values.specifications,
      internal_notes: values.internal_notes,
      supplier_ids: selectedSuppliers,
    });
  };

  const supplierTransferData = suppliers.map(s => ({
    key: s.id.toString(),
    title: s.name,
    description: s.email,
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
          Create Request for Quotation
        </Typography.Title>
        <Typography.Text type="secondary">
          Send RFQ to multiple suppliers for competitive bidding.
        </Typography.Text>
      </div>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            closing_datetime: dayjs().add(7, 'days'),
            required_by_date: dayjs().add(30, 'days'),
          }}
        >
          <Form.Item
            label="Component"
            name="component_id"
            rules={[{ required: true, message: 'Please select a component' }]}
          >
            <Select
              showSearch
              placeholder="Select component"
              optionFilterProp="children"
              filterOption={(input, option) =>
                ((option?.label ?? '') as string).toLowerCase().includes(input.toLowerCase())
              }
              options={components.map((c: any) => ({
                value: c.id,
                label: `${c.name} (${c.part_number})`,
              }))}
            />
          </Form.Item>

          <Form.Item
            label="Quantity"
            name="quantity"
            rules={[{ required: true, message: 'Please enter quantity' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>

          <Space size="large" style={{ width: '100%' }}>
            <Form.Item
              label="Required By Date"
              name="required_by_date"
              rules={[{ required: true }]}
              style={{ flex: 1 }}
            >
              <DatePicker style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              label="Closing Date & Time"
              name="closing_datetime"
              rules={[{ required: true }]}
              style={{ flex: 1 }}
            >
              <DatePicker showTime format="YYYY-MM-DD HH:mm" style={{ width: '100%' }} />
            </Form.Item>
          </Space>

          <Form.Item
            label="Technical Specifications"
            name="specifications"
          >
            <TextArea rows={4} placeholder="Enter technical requirements and specifications..." />
          </Form.Item>

          <Form.Item
            label="Internal Notes"
            name="internal_notes"
            extra="These notes are not shared with suppliers"
          >
            <TextArea rows={3} placeholder="Enter internal notes..." />
          </Form.Item>

          <Form.Item
            label="Select Suppliers"
            required
          >
            <Transfer
              dataSource={supplierTransferData}
              titles={['Available Suppliers', 'Selected Suppliers']}
              targetKeys={selectedSuppliers.map(id => id.toString())}
              onChange={(keys) => setSelectedSuppliers(keys.map(k => parseInt(k)))}
              render={(item) => item.title}
              listStyle={{ width: 300, height: 400 }}
              showSearch
              filterOption={(inputValue, item) =>
                item.title.toLowerCase().indexOf(inputValue.toLowerCase()) !== -1
              }
            />
            {selectedSuppliers.length === 0 && (
              <Typography.Text type="danger" style={{ marginTop: 8, display: 'block' }}>
                Please select at least one supplier
              </Typography.Text>
            )}
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={createRFQMutation.isPending}
                disabled={selectedSuppliers.length === 0}
              >
                Create RFQ
              </Button>
              <Button onClick={() => navigate('/procurement/rfqs')}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default CreateRFQPage;
