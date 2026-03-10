import { useState, useEffect } from 'react';
import { Form, Input, DatePicker, Button, Space, Card, Typography, App as AntdApp } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import type { RFQ, RFQCreatePayload, RFQUpdatePayload, Product } from '@/features/sales/types';
import { LineItemsTable } from './LineItemsTable';

interface RfqFormProps {
  initialValues?: RFQ;
  products: Product[];
  onSubmit: (values: RFQCreatePayload | RFQUpdatePayload) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
  mode?: 'create' | 'edit';
}

interface LineItem {
  id?: number;
  product_id: number;
  product_name?: string | null;
  quantity: number;
  unit_price: string | number;
}

export const RfqForm = ({
  initialValues,
  products,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: RfqFormProps) => {
  const { message } = AntdApp.useApp();
  const [form] = Form.useForm();
  const [lineItems, setLineItems] = useState<LineItem[]>([]);

  useEffect(() => {
    if (initialValues?.items) {
      setLineItems(initialValues.items.map(item => ({
        id: item.id,
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.unit_price,
      })));
    }
  }, [initialValues]);

  const handleAddLineItem = () => {
    setLineItems([
      ...lineItems,
      { product_id: 0, quantity: 1, unit_price: '0' },
    ]);
  };

  const handleItemChange = (index: number, field: keyof LineItem, value: any) => {
    const newItems = [...lineItems];
    newItems[index] = { ...newItems[index], [field]: value };
    setLineItems(newItems);
  };

  const handleItemRemove = (index: number) => {
    setLineItems(lineItems.filter((_, i) => i !== index));
  };

  const handleFinish = async (values: any) => {
    // Validate at least one line item exists
    if (lineItems.length === 0) {
      message.error('At least one line item is required');
      return;
    }

    // Validate all line items have valid product, quantity, and price
    const invalidItems = lineItems.filter(
      item => !item.product_id || item.quantity <= 0 || parseFloat(item.unit_price.toString()) <= 0
    );

    if (invalidItems.length > 0) {
      message.error('All line items must have a valid product, positive quantity, and positive price');
      return;
    }

    const payload = {
      due_date: values.due_date ? dayjs(values.due_date).format('YYYY-MM-DD') : null,
      description: values.description || null,
      items: lineItems.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.unit_price.toString(),
      })),
    };

    try {
      await onSubmit(payload);
    } catch (error) {
      message.error('Failed to save RFQ');
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleFinish}
      initialValues={{
        due_date: initialValues?.due_date ? dayjs(initialValues.due_date) : undefined,
        description: initialValues?.description || '',
      }}
    >
      <Form.Item
        name="due_date"
        label="Due Date"
      >
        <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
      </Form.Item>

      <Form.Item
        name="description"
        label="Description"
      >
        <Input.TextArea rows={3} placeholder="Enter RFQ description" />
      </Form.Item>

      <Card
        title="Line Items"
        size="small"
        extra={
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={handleAddLineItem}
            size="small"
          >
            Add Item
          </Button>
        }
        style={{ marginBottom: 24 }}
      >
        {lineItems.length === 0 ? (
          <Typography.Text type="secondary">No line items added yet. Click "Add Item" to get started.</Typography.Text>
        ) : (
          <LineItemsTable
            items={lineItems}
            products={products}
            editable={true}
            onItemChange={handleItemChange}
            onItemRemove={handleItemRemove}
            showTotal={false}
          />
        )}
      </Card>

      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit" loading={isLoading}>
            {mode === 'create' ? 'Create RFQ' : 'Update RFQ'}
          </Button>
          {onCancel && (
            <Button onClick={onCancel}>
              Cancel
            </Button>
          )}
        </Space>
      </Form.Item>
    </Form>
  );
};

