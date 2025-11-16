import { PlusOutlined } from '@ant-design/icons';
import {
  Button,
  DatePicker,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Typography,
  Divider,
} from 'antd';
import type { FormInstance } from 'antd';
import dayjs, { Dayjs } from 'dayjs';
import { useEffect } from 'react';
import type {
  Customer,
  Product,
  QuotationItemCreatePayload,
  RFQ,
} from '@/features/sales/types';
import { formatCurrency } from '@/shared/utils/format';

export interface QuotationFormValues {
  customer_id: number;
  date: Dayjs;
  expiration_date: Dayjs;
  invoicing_and_shipping_address: string;
  quotation_items: QuotationItemCreatePayload[];
}

interface QuotationFormProps {
  form: FormInstance<QuotationFormValues>;
  customers: Customer[];
  products: Product[];
  onSubmit: (values: QuotationFormValues) => void;
  loading?: boolean;
  mode?: 'create' | 'rfq-conversion';
  sourceRfq?: RFQ | null;
}

const QuotationItemFields = ({
  name,
  remove,
  products,
}: {
  name: number;
  remove: (index: number | number[]) => void;
  products: Product[];
}) => (
  <Space align="baseline" wrap style={{ width: '100%' }}>
    <Form.Item
      name={[name, 'product_id']}
      label="Product"
      rules={[{ required: true, message: 'Select product' }]}
    >
      <Select
        showSearch
        placeholder="Product"
        optionFilterProp="label"
        options={products.map((product) => ({
          label: product.product_name ?? product.name ?? product.description,
          value: product.id,
        }))}
        style={{ minWidth: 200 }}
      />
    </Form.Item>
    <Form.Item
      name={[name, 'quantity']}
      label="Qty"
      rules={[
        { required: true, message: 'Enter quantity' },
        { type: 'number', min: 1, message: 'Quantity must be positive' },
      ]}
    >
      <InputNumber min={1} />
    </Form.Item>
    <Form.Item
      name={[name, 'unit_price']}
      label="Unit Price"
      rules={[
        { required: true, message: 'Enter price' },
        { type: 'number', min: 0.01, message: 'Price must be positive' },
      ]}
    >
      <InputNumber min={0.01} step={0.01} precision={2} />
    </Form.Item>
    <Button type="link" danger onClick={() => remove(name)}>
      Remove
    </Button>
  </Space>
);

export const QuotationForm = ({
  form,
  customers,
  products,
  onSubmit,
  loading = false,
  mode = 'create',
  sourceRfq = null,
}: QuotationFormProps) => {
  // Pre-populate form when converting from RFQ
  useEffect(() => {
    if (mode === 'rfq-conversion' && sourceRfq) {
      // Pre-populate line items from RFQ
      const rfqItems = sourceRfq.items.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
        unit_price: item.unit_price,
      }));
      
      form.setFieldsValue({
        quotation_items: rfqItems,
      });
    }
  }, [mode, sourceRfq, form]);

  // Calculate total amount
  const calculateTotal = (): number => {
    const items = form.getFieldValue('quotation_items') || [];
    return items.reduce((sum: number, item: QuotationItemCreatePayload) => {
      const unitPrice = typeof item.unit_price === 'string' 
        ? parseFloat(item.unit_price) 
        : item.unit_price || 0;
      return sum + (item.quantity || 0) * unitPrice;
    }, 0);
  };

  // Watch for changes to recalculate total
  const handleValuesChange = () => {
    // Trigger re-render to update total display
    form.validateFields(['quotation_items']);
  };

  // Validate expiration date is after quotation date
  const validateExpirationDate = (_: any, value: Dayjs) => {
    const quotationDate = form.getFieldValue('date');
    if (value && quotationDate && value.isBefore(quotationDate, 'day')) {
      return Promise.reject(new Error('Expiration date must be after quotation date'));
    }
    return Promise.resolve();
  };

  return (
    <Form<QuotationFormValues>
      layout="vertical"
      form={form}
      onFinish={onSubmit}
      onValuesChange={handleValuesChange}
      initialValues={{
        date: dayjs(),
        expiration_date: dayjs().add(14, 'day'),
        quotation_items: [],
      }}
    >
      {/* Show source RFQ info if in conversion mode */}
      {mode === 'rfq-conversion' && sourceRfq && (
        <>
          <Typography.Text type="secondary">
            Creating quotation from RFQ #{sourceRfq.id}
          </Typography.Text>
          <Divider />
        </>
      )}

      <Form.Item
        name="customer_id"
        label="Customer"
        rules={[{ required: true, message: 'Select customer' }]}
      >
        <Select
          showSearch
          placeholder="Select customer"
          optionFilterProp="label"
          options={customers.map((customer) => ({
            label: customer.name,
            value: customer.id,
            disabled: !customer.is_active,
          }))}
        />
      </Form.Item>

      <Space size="large" wrap>
        <Form.Item
          name="date"
          label="Quotation Date"
          rules={[{ required: true, message: 'Select date' }]}
        >
          <DatePicker format="YYYY-MM-DD" />
        </Form.Item>
        <Form.Item
          name="expiration_date"
          label="Expiration Date"
          rules={[
            { required: true, message: 'Select expiration date' },
            { validator: validateExpirationDate },
          ]}
        >
          <DatePicker format="YYYY-MM-DD" />
        </Form.Item>
      </Space>

      <Form.Item
        name="invoicing_and_shipping_address"
        label="Billing & Shipping Address"
        rules={[{ required: true, message: 'Enter address' }]}
      >
        <Input.TextArea rows={3} placeholder="Enter full shipping address" />
      </Form.Item>

      <Divider />

      <Form.List
        name="quotation_items"
        rules={[
          {
            validator: async (_, items) => {
              if (!items || items.length === 0) {
                return Promise.reject(new Error('Add at least one line item'));
              }
            },
          },
        ]}
      >
        {(fields, { add, remove }, { errors }) => (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography.Title level={5} style={{ margin: 0 }}>
                Line Items
              </Typography.Title>
              <Button
                type="dashed"
                onClick={() => add({ quantity: 1, unit_price: 0 })}
                icon={<PlusOutlined />}
              >
                Add Item
              </Button>
            </div>

            {fields.map((field) => (
              <QuotationItemFields
                key={field.key}
                name={field.name}
                remove={remove}
                products={products}
              />
            ))}

            {fields.length === 0 && (
              <Typography.Text type="secondary">
                No line items added. Click "Add Item" to add products.
              </Typography.Text>
            )}

            <Form.ErrorList errors={errors} />
          </Space>
        )}
      </Form.List>

      <Divider />

      {/* Total Amount Display */}
      <div style={{ textAlign: 'right', marginBottom: 24 }}>
        <Typography.Text strong style={{ fontSize: 18 }}>
          Total: {formatCurrency(calculateTotal())}
        </Typography.Text>
      </div>

      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit" loading={loading}>
            {mode === 'rfq-conversion' ? 'Create Quotation from RFQ' : 'Create Quotation'}
          </Button>
          <Button htmlType="button" onClick={() => form.resetFields()}>
            Reset
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};
