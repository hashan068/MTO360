import { Table, Typography, InputNumber, Select, Button, Space } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { DeleteOutlined } from '@ant-design/icons';
import { formatCurrency } from '@/shared/utils/format';
import type { Product } from '@/features/sales/types';

interface LineItem {
  id?: number;
  product_id: number;
  product_name?: string | null;
  quantity: number;
  unit_price: string | number;
}

interface LineItemsTableProps {
  items: LineItem[];
  products?: Product[];
  editable?: boolean;
  onItemChange?: (index: number, field: keyof LineItem, value: any) => void;
  onItemRemove?: (index: number) => void;
  showTotal?: boolean;
}

export const LineItemsTable = ({
  items,
  products = [],
  editable = false,
  onItemChange,
  onItemRemove,
  showTotal = true,
}: LineItemsTableProps) => {
  // Calculate subtotal for each line item
  const calculateSubtotal = (item: LineItem): number => {
    const unitPrice = typeof item.unit_price === 'string' 
      ? parseFloat(item.unit_price) 
      : item.unit_price;
    return item.quantity * unitPrice;
  };

  // Calculate total amount
  const calculateTotal = (): number => {
    return items.reduce((sum, item) => sum + calculateSubtotal(item), 0);
  };

  // Get product name by ID
  const getProductName = (productId: number): string => {
    const product = products.find((p) => p.id === productId);
    return product?.product_name || product?.name || product?.description || `Product #${productId}`;
  };

  const columns: ColumnsType<LineItem> = [
    {
      title: 'Product',
      dataIndex: 'product_id',
      key: 'product',
      render: (productId: number, record: LineItem, index: number) => {
        if (editable && onItemChange) {
          return (
            <Select
              showSearch
              placeholder="Select product"
              optionFilterProp="label"
              value={productId}
              onChange={(value) => onItemChange(index, 'product_id', value)}
              options={products.map((product) => ({
                label: product.product_name ?? product.name ?? product.description,
                value: product.id,
              }))}
              style={{ width: '100%', minWidth: 200 }}
            />
          );
        }
        return record.product_name || getProductName(productId);
      },
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 120,
      render: (quantity: number, _record: LineItem, index: number) => {
        if (editable && onItemChange) {
          return (
            <InputNumber
              min={1}
              value={quantity}
              onChange={(value) => onItemChange(index, 'quantity', value || 1)}
              style={{ width: '100%' }}
            />
          );
        }
        return quantity;
      },
    },
    {
      title: 'Unit Price',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 150,
      render: (unitPrice: string | number, _record: LineItem, index: number) => {
        if (editable && onItemChange) {
          const numericValue = typeof unitPrice === 'string' ? parseFloat(unitPrice) : unitPrice;
          return (
            <InputNumber
              min={0}
              step={0.01}
              value={numericValue}
              onChange={(value) => onItemChange(index, 'unit_price', value || 0)}
              formatter={(value) => `$ ${value}`}
              parser={(value) => value?.replace(/\$\s?/g, '') as any}
              style={{ width: '100%' }}
            />
          );
        }
        return formatCurrency(unitPrice);
      },
    },
    {
      title: 'Subtotal',
      key: 'subtotal',
      width: 150,
      render: (_, record) => formatCurrency(calculateSubtotal(record)),
    },
  ];

  // Add actions column if editable
  if (editable && onItemRemove) {
    columns.push({
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_: any, _record: LineItem, index: number) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => onItemRemove(index)}
        >
          Remove
        </Button>
      ),
    });
  }

  return (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      <Table<LineItem>
        columns={columns}
        dataSource={items}
        rowKey={(record) => record.id?.toString() || `temp-${record.product_id}-${record.quantity}`}
        pagination={false}
        size="small"
        bordered
      />
      {showTotal && (
        <div style={{ textAlign: 'right', paddingRight: 16 }}>
          <Typography.Text strong style={{ fontSize: 16 }}>
            Total: {formatCurrency(calculateTotal())}
          </Typography.Text>
        </div>
      )}
    </Space>
  );
};
