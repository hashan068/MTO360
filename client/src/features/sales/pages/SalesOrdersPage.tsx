import { SearchOutlined } from '@ant-design/icons';
import {
  Card,
  DatePicker,
  Input,
  Select,
  Space,
  Table,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { salesOrdersApi } from '@/features/sales/api';
import type {
  SalesOrder,
  SalesOrderStatus,
} from '@/features/sales/types';
import { formatCurrency } from '@/shared/utils/format';
import { StatusBadge } from '@/features/sales/components/StatusBadge';

const { RangePicker } = DatePicker;

const SalesOrdersPage = () => {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<SalesOrderStatus | undefined>(undefined);
  const [searchText, setSearchText] = useState<string>('');
  const [dateRange, setDateRange] = useState<[string, string] | undefined>(undefined);

  const {
    data: salesOrders = [],
    isLoading,
  } = useQuery<SalesOrder[]>({
    queryKey: ['sales', 'orders', 'list', statusFilter, searchText, dateRange],
    queryFn: () => salesOrdersApi.list({ 
      status: statusFilter,
      search: searchText || undefined,
      date_from: dateRange?.[0],
      date_to: dateRange?.[1],
      limit: 200 
    }),
  });

  const columns: ColumnsType<SalesOrder> = [
    { 
      title: 'ID', 
      dataIndex: 'id', 
      key: 'id', 
      width: 80,
      render: (value) => `SO-${value}`,
    },
    { 
      title: 'Customer', 
      dataIndex: 'customer_name', 
      key: 'customer_name',
      ellipsis: true,
    },
    { 
      title: 'Date', 
      dataIndex: 'created_at_date', 
      key: 'created_at_date',
      width: 120,
      render: (value) => value ? dayjs(value).format('MMM D, YYYY') : '-',
    },
    { 
      title: 'Total', 
      dataIndex: 'total_amount', 
      key: 'total_amount',
      width: 120,
      render: (value) => formatCurrency(value),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 160,
      render: (value: SalesOrderStatus) => <StatusBadge status={value} />,
    },
  ];

  const handleRowClick = (record: SalesOrder) => {
    navigate(`/sales/orders/${record.id}`);
  };

  const handleDateRangeChange = (dates: any) => {
    if (dates && dates[0] && dates[1]) {
      setDateRange([
        dates[0].format('YYYY-MM-DD'),
        dates[1].format('YYYY-MM-DD'),
      ]);
    } else {
      setDateRange(undefined);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            Sales Orders
          </Typography.Title>
          <Typography.Text type="secondary">Track and manage sales order fulfillment.</Typography.Text>
        </div>
      </div>

      <Card>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Space wrap>
            <Select
              placeholder="Filter by status"
              allowClear
              style={{ width: 200 }}
              value={statusFilter}
              onChange={setStatusFilter}
              options={[
                { label: 'Pending', value: 'pending' },
                { label: 'Confirmed', value: 'confirmed' },
                { label: 'Processing', value: 'processing' },
                { label: 'In Production', value: 'in_production' },
                { label: 'Ready for Delivery', value: 'ready_for_delivery' },
                { label: 'Delivered', value: 'delivered' },
                { label: 'Cancelled', value: 'cancelled' },
              ]}
            />
            <RangePicker
              placeholder={['Start date', 'End date']}
              onChange={handleDateRangeChange}
              style={{ width: 280 }}
            />
            <Input
              placeholder="Search by order number or customer"
              prefix={<SearchOutlined />}
              allowClear
              style={{ width: 300 }}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </Space>

          <Table<SalesOrder>
            rowKey="id"
            columns={columns}
            dataSource={salesOrders || []}
            loading={isLoading}
            pagination={{ pageSize: 10 }}
            onRow={(record) => ({
              onClick: () => handleRowClick(record),
              style: { cursor: 'pointer' },
            })}
          />
        </Space>
      </Card>
    </div>
  );
};

export default SalesOrdersPage;


