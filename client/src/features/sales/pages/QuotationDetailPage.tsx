import { ArrowLeftOutlined, EditOutlined, PlusOutlined, MailOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  Descriptions,
  Select,
  Space,
  Spin,
  Typography,
  Divider,
  Tag,
  Tooltip,
} from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { quotationsApi, productsApi, sendQuotationEmail } from '@/features/sales/api';
import type { Quotation, QuotationStatus, Product } from '@/features/sales/types';
import { StatusBadge } from '@/features/sales/components/StatusBadge';
import { DocumentLink } from '@/features/sales/components/DocumentLink';
import { LineItemsTable } from '@/features/sales/components/LineItemsTable';
import { DocumentBreadcrumb } from '@/features/sales/components/DocumentBreadcrumb';
import { formatCurrency } from '@/shared/utils/format';
import dayjs from 'dayjs';

const QuotationDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { message } = AntdApp.useApp();
  const queryClient = useQueryClient();

  const quotationId = parseInt(id || '0', 10);

  // Fetch quotation details
  const { data: quotation, isLoading } = useQuery<Quotation>({
    queryKey: ['sales', 'quotations', quotationId],
    queryFn: () => quotationsApi.retrieve(quotationId),
    enabled: !!quotationId,
  });

  // Fetch products for line items display
  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['sales', 'products', 'options'],
    queryFn: () => productsApi.list({ limit: 200 }),
  });

  // Update status mutation
  const updateStatusMutation = useMutation({
    mutationFn: (status: QuotationStatus) =>
      quotationsApi.updateStatus(quotationId, { status }),
    onSuccess: () => {
      message.success('Quotation status updated');
      queryClient.invalidateQueries({ queryKey: ['sales', 'quotations', quotationId] });
      queryClient.invalidateQueries({ queryKey: ['sales', 'quotations', 'list'] });
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || 'Failed to update status');
    },
  });

  // Convert to sales order mutation
  const convertToSalesOrderMutation = useMutation({
    mutationFn: () => quotationsApi.convertToSalesOrder(quotationId),
    onSuccess: (salesOrder) => {
      message.success('Sales order created successfully');
      navigate(`/sales/orders/${salesOrder.id}`);
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || 'Failed to create sales order');
    },
  });

  // Send email mutation
  const sendEmailMutation = useMutation({
    mutationFn: () => sendQuotationEmail(quotationId),
    onSuccess: () => {
      message.success('Quotation email sent successfully');
      queryClient.invalidateQueries({ queryKey: ['sales', 'quotations', quotationId] });
      queryClient.invalidateQueries({ queryKey: ['sales', 'quotations', 'list'] });
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || 'Failed to send email');
    },
  });

  // Check if quotation is expired
  const isExpired = quotation
    ? dayjs(quotation.expiration_date).isBefore(dayjs(), 'day') &&
      (quotation.status === 'quotation' || quotation.status === 'quotation_sent')
    : false;

  // Determine available status transitions
  const getAvailableStatuses = (): QuotationStatus[] => {
    if (!quotation) return [];
    
    const currentStatus = quotation.status;
    const allStatuses: QuotationStatus[] = [
      'quotation',
      'quotation_sent',
      'accepted',
      'rejected',
      'cancelled',
      'expired',
    ];

    // Filter based on business rules
    if (currentStatus === 'accepted') {
      // Cannot change from accepted to rejected or cancelled
      return allStatuses.filter(s => s !== 'rejected' && s !== 'cancelled');
    }

    return allStatuses;
  };

  // Get email history
  const emailHistory = quotation?.email_history || [];

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '48px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!quotation) {
    return (
      <Card>
        <Typography.Text>Quotation not found</Typography.Text>
      </Card>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <DocumentBreadcrumb
        rfq={quotation.rfq_reference}
        quotation={{ 
          id: quotation.id, 
          status: quotation.status, 
          customer_id: quotation.customer_id,
          customer_name: quotation.customer_name,
          date: quotation.date,
          total_amount: quotation.total_amount
        }}
        currentPage="quotation"
      />
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/sales/quotations')}>
            Back
          </Button>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Quotation #{quotation.id}
          </Typography.Title>
          <StatusBadge status={quotation.status} isExpired={isExpired} />
        </Space>
        <Space>
          <Button 
            icon={<EditOutlined />} 
            onClick={() => message.info('Edit functionality coming soon')}
            disabled={!quotation.can_edit}
            title={!quotation.can_edit ? `Cannot edit quotation with status "${quotation.status}"` : undefined}
          >
            Edit
          </Button>
          <Tooltip title={quotation.email_sent_count > 0 ? `Resend email (sent ${quotation.email_sent_count} time${quotation.email_sent_count > 1 ? 's' : ''})` : 'Send email to customer'}>
            <Button
              icon={<MailOutlined />}
              loading={sendEmailMutation.isPending}
              onClick={() => sendEmailMutation.mutate()}
            >
              {quotation.email_sent_count > 0 ? 'Resend Email' : 'Send Email'}
            </Button>
          </Tooltip>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            loading={convertToSalesOrderMutation.isPending}
            onClick={() => convertToSalesOrderMutation.mutate()}
            disabled={quotation.status !== 'accepted'}
            title={quotation.status !== 'accepted' ? 'Quotation must be accepted to create sales order' : undefined}
          >
            Create Sales Order
          </Button>
        </Space>
      </div>

      {/* Quotation Details */}
      <Card title="Quotation Information">
        <Descriptions column={2} bordered>
          <Descriptions.Item label="Quotation ID">#{quotation.id}</Descriptions.Item>
          <Descriptions.Item label="Status">
            <Space>
              <StatusBadge status={quotation.status} isExpired={isExpired} />
              {quotation.can_edit && (
                <Select
                  value={quotation.status}
                  onChange={(value) => updateStatusMutation.mutate(value)}
                  loading={updateStatusMutation.isPending}
                  style={{ width: 180 }}
                  options={getAvailableStatuses().map((status) => ({
                    label: status.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
                    value: status,
                  }))}
                />
              )}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="Customer">{quotation.customer_name}</Descriptions.Item>
          <Descriptions.Item label="Date">{quotation.date}</Descriptions.Item>
          <Descriptions.Item label="Expiration Date">
            <span style={{ color: isExpired ? '#ff4d4f' : 'inherit' }}>
              {quotation.expiration_date}
              {isExpired && ' (Expired)'}
            </span>
          </Descriptions.Item>
          <Descriptions.Item label="Total Amount">
            <Typography.Text strong style={{ fontSize: 16 }}>
              {formatCurrency(quotation.total_amount)}
            </Typography.Text>
          </Descriptions.Item>
          <Descriptions.Item label="Shipping Address" span={2}>
            {quotation.invoicing_and_shipping_address}
          </Descriptions.Item>
          <Descriptions.Item label="Created At">{quotation.created_at}</Descriptions.Item>
          <Descriptions.Item label="Updated At">{quotation.updated_at || 'N/A'}</Descriptions.Item>
          <Descriptions.Item label="Email Status" span={2}>
            {quotation.email_sent_count > 0 ? (
              <Space direction="vertical" size="small">
                <Space>
                  <Tag color="green">Sent {quotation.email_sent_count} time{quotation.email_sent_count > 1 ? 's' : ''}</Tag>
                  {quotation.email_sent_at && (
                    <Typography.Text type="secondary">
                      Last sent: {dayjs(quotation.email_sent_at).format('MMM D, YYYY h:mm A')}
                    </Typography.Text>
                  )}
                </Space>
                {emailHistory.length > 0 && (
                  <div style={{ marginTop: 8 }}>
                    <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                      Email history:
                    </Typography.Text>
                    {emailHistory.map((entry, index) => (
                      <div key={index} style={{ fontSize: 12, color: '#8c8c8c', marginLeft: 8 }}>
                        • {dayjs(entry.sent_at).format('MMM D, YYYY h:mm A')} - Sent by {entry.sent_by_username} to {entry.recipient}
                      </div>
                    ))}
                  </div>
                )}
              </Space>
            ) : (
              <Tag color="default">Not sent</Tag>
            )}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Source RFQ Link */}
      {quotation.rfq_id && quotation.rfq_reference && (
        <Card title="Source Document">
          <Space direction="vertical">
            <Typography.Text type="secondary">This quotation was created from:</Typography.Text>
            <DocumentLink type="rfq" id={quotation.rfq_id} />
          </Space>
        </Card>
      )}

      {/* Line Items */}
      <Card title="Line Items">
        <LineItemsTable
          items={quotation.quotation_items.map((item) => ({
            ...item,
            unit_price: item.unit_price,
          }))}
          products={products}
          editable={false}
          showTotal={true}
        />
      </Card>

      {/* Linked Sales Orders */}
      {quotation.sales_orders && quotation.sales_orders.length > 0 && (
        <Card title="Sales Orders">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Typography.Text type="secondary">
              Sales orders created from this quotation:
            </Typography.Text>
            {quotation.sales_orders.map((order) => (
              <div key={order.id} style={{ padding: '8px 0' }}>
                <Space split={<Divider type="vertical" />}>
                  <DocumentLink type="sales_order" id={order.id} />
                  <StatusBadge status={order.status} />
                  <Typography.Text>{formatCurrency(order.total_amount)}</Typography.Text>
                  <Typography.Text type="secondary">{order.created_at}</Typography.Text>
                </Space>
              </div>
            ))}
          </Space>
        </Card>
      )}
    </div>
  );
};

export default QuotationDetailPage;
