import { ArrowLeftOutlined, EditOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  Descriptions,
  Select,
  Space,
  Spin,
  Typography,
} from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import dayjs from 'dayjs';
import { salesOrdersApi } from '@/features/sales/api';
import type { SalesOrder, SalesOrderStatus } from '@/features/sales/types';
import { formatCurrency } from '@/shared/utils/format';
import { StatusBadge } from '@/features/sales/components/StatusBadge';
import { DocumentLink } from '@/features/sales/components/DocumentLink';
import { LineItemsTable } from '@/features/sales/components/LineItemsTable';
import { DocumentBreadcrumb } from '@/features/sales/components/DocumentBreadcrumb';
import ProductionScheduleCard from '@/components/ProductionScheduleCard';

const { Title, Text } = Typography;

const SalesOrderDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { message } = AntdApp.useApp();
  const queryClient = useQueryClient();

  const {
    data: salesOrder,
    isLoading,
    error,
  } = useQuery<SalesOrder>({
    queryKey: ['sales', 'orders', id],
    queryFn: () => salesOrdersApi.retrieve(Number(id)),
    enabled: !!id,
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ orderId, status }: { orderId: number; status: SalesOrderStatus }) =>
      salesOrdersApi.updateStatus(orderId, { status }),
    onSuccess: () => {
      message.success('Sales order status updated');
      queryClient.invalidateQueries({ queryKey: ['sales', 'orders', id] });
      queryClient.invalidateQueries({ queryKey: ['sales', 'orders', 'list'] });
    },
    onError: (error: any) => {
      const errorMessage = error?.response?.data?.detail || 'Failed to update status';
      message.error(errorMessage);
    },
  });

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '48px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error || !salesOrder) {
    return (
      <Card>
        <Text type="danger">Failed to load sales order details</Text>
      </Card>
    );
  }

  const handleStatusChange = (newStatus: SalesOrderStatus) => {
    updateStatusMutation.mutate({ orderId: salesOrder.id, status: newStatus });
  };

  const getAvailableStatusTransitions = (currentStatus: SalesOrderStatus): SalesOrderStatus[] => {
    const transitions: Record<SalesOrderStatus, SalesOrderStatus[]> = {
      pending: ['confirmed', 'cancelled'],
      confirmed: ['processing', 'cancelled'],
      processing: ['in_production', 'cancelled'],
      in_production: ['ready_for_delivery', 'cancelled'],
      ready_for_delivery: ['delivered', 'cancelled'],
      delivered: [],
      cancelled: [],
    };
    return transitions[currentStatus] || [];
  };

  const availableStatuses = getAvailableStatusTransitions(salesOrder.status);
  const canUpdateStatus = availableStatuses.length > 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <DocumentBreadcrumb
        rfq={salesOrder.rfq_reference}
        quotation={salesOrder.quotation_reference}
        salesOrder={{ id: salesOrder.id, status: salesOrder.status, customer_id: salesOrder.customer_id, total_amount: salesOrder.total_amount }}
        currentPage="sales_order"
      />
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/sales/orders')}>
            Back
          </Button>
          <Title level={3} style={{ margin: 0 }}>
            Sales Order SO-{salesOrder.id}
          </Title>
          <StatusBadge status={salesOrder.status} />
        </Space>
        <Space>
          <Button
            icon={<EditOutlined />}
            disabled={!salesOrder.can_edit}
            title={!salesOrder.can_edit ? `Cannot edit sales order with status "${salesOrder.status}"` : undefined}
            onClick={() => message.info('Edit functionality coming soon')}
          >
            Edit
          </Button>
        </Space>
      </div>

      <Card title="Order Information">
        <Descriptions column={2} bordered>
          <Descriptions.Item label="Order ID">SO-{salesOrder.id}</Descriptions.Item>
          <Descriptions.Item label="Status">
            <Space>
              <StatusBadge status={salesOrder.status} />
              {canUpdateStatus && (
                <Select
                  placeholder="Update status"
                  style={{ width: 200 }}
                  onChange={handleStatusChange}
                  loading={updateStatusMutation.isPending}
                  options={availableStatuses.map((status) => ({
                    label: status.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
                    value: status,
                  }))}
                />
              )}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="Customer">{salesOrder.customer_name || 'N/A'}</Descriptions.Item>
          <Descriptions.Item label="Total Amount">{formatCurrency(salesOrder.total_amount)}</Descriptions.Item>
          <Descriptions.Item label="Order Date">
            {salesOrder.created_at_date ? dayjs(salesOrder.created_at_date).format('MMMM D, YYYY') : 'N/A'}
          </Descriptions.Item>
          <Descriptions.Item label="Delivery Date">
            {salesOrder.delivery_date ? dayjs(salesOrder.delivery_date).format('MMMM D, YYYY h:mm A') : 'Not delivered'}
          </Descriptions.Item>
          <Descriptions.Item label="Source Quotation" span={2}>
            {salesOrder.quotation_reference ? (
              <DocumentLink type="quotation" id={salesOrder.quotation_reference.id} />
            ) : (
              <Text type="secondary">Direct order (no quotation)</Text>
            )}
          </Descriptions.Item>
          {salesOrder.rfq_reference && (
            <Descriptions.Item label="Source RFQ" span={2}>
              <DocumentLink type="rfq" id={salesOrder.rfq_reference.id} />
            </Descriptions.Item>
          )}
          <Descriptions.Item label="Can Edit">
            {salesOrder.can_edit ? (
              <Text type="success">Yes</Text>
            ) : (
              <Text type="secondary">No (locked due to status)</Text>
            )}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="Line Items">
        <LineItemsTable
          items={salesOrder.order_items.map(item => ({
            ...item,
            unit_price: item.price,
          }))}
        />
      </Card>

      <ProductionScheduleCard salesOrderId={salesOrder.id} />
    </div>
  );
};

export default SalesOrderDetailPage;
