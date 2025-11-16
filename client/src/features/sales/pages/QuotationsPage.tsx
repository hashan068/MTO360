import { MailOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons';
import {
  App as AntdApp,
  Button,
  Card,
  Input,
  Select,
  Space,
  Table,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { quotationsApi, sendQuotationEmail } from '@/features/sales/api';
import type {
  Quotation,
  QuotationStatus,
} from '@/features/sales/types';
import { formatCurrency } from '@/shared/utils/format';
import { StatusBadge } from '@/features/sales/components/StatusBadge';

const QuotationsPage = () => {
  const { message } = AntdApp.useApp();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<QuotationStatus | undefined>(undefined);
  const [searchText, setSearchText] = useState<string>('');

  const { data: quotations = [], isLoading } = useQuery<Quotation[]>({
    queryKey: ['sales', 'quotations', 'list', statusFilter, searchText],
    queryFn: () => quotationsApi.list({ 
      status: statusFilter, 
      search: searchText || undefined,
      limit: 200 
    }),
  });



  const emailMutation = useMutation({
    mutationFn: (id: number) => sendQuotationEmail(id),
    onSuccess: () => {
      message.success('Quotation email sent successfully');
      // Invalidate queries to refresh the list
      queryClient.invalidateQueries({ queryKey: ['sales', 'quotations'] });
    },
    onError: () => message.error('Unable to send quotation email'),
  });

  // Check if quotation is expired
  const isQuotationExpired = (quotation: Quotation): boolean => {
    const today = dayjs().startOf('day');
    const expirationDate = dayjs(quotation.expiration_date).startOf('day');
    return expirationDate.isBefore(today) && 
           (quotation.status === 'quotation' || quotation.status === 'quotation_sent');
  };

  const columns: ColumnsType<Quotation> = [
    { 
      title: 'ID', 
      dataIndex: 'id', 
      key: 'id', 
      width: 80,
      render: (id: number) => `#${id}`,
    },
    { 
      title: 'Customer', 
      dataIndex: 'customer_name', 
      key: 'customer_name',
      ellipsis: true,
    },
    { 
      title: 'Date', 
      dataIndex: 'date', 
      key: 'date',
      width: 120,
    },
    { 
      title: 'Expiration', 
      dataIndex: 'expiration_date', 
      key: 'expiration_date',
      width: 120,
      render: (date: string, record: Quotation) => {
        const expired = isQuotationExpired(record);
        return (
          <span style={{ color: expired ? '#ff4d4f' : 'inherit' }}>
            {date}
            {expired && ' ⚠️'}
          </span>
        );
      },
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
      width: 150,
      render: (status: QuotationStatus, record: Quotation) => (
        <StatusBadge status={status} isExpired={isQuotationExpired(record)} />
      ),
    },
    {
      title: 'Email Status',
      key: 'email_status',
      width: 150,
      render: (_, record: Quotation) => {
        if (record.email_sent_count > 0) {
          return (
            <Space direction="vertical" size={0}>
              <Typography.Text style={{ fontSize: 12 }}>
                Sent {record.email_sent_count}x
              </Typography.Text>
              {record.email_sent_at && (
                <Typography.Text type="secondary" style={{ fontSize: 11 }}>
                  {dayjs(record.email_sent_at).format('MMM D, h:mm A')}
                </Typography.Text>
              )}
            </Space>
          );
        }
        return <Typography.Text type="secondary" style={{ fontSize: 12 }}>Not sent</Typography.Text>;
      },
    },
    {
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Button
          type="link"
          icon={<MailOutlined />}
          loading={emailMutation.isPending && emailMutation.variables === record.id}
          onClick={(e) => {
            e.stopPropagation();
            emailMutation.mutate(record.id);
          }}
        >
          {record.email_sent_count > 0 ? 'Resend' : 'Send Email'}
        </Button>
      ),
    },
  ];



  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            Quotations
          </Typography.Title>
          <Typography.Text type="secondary">
            Generate quotations and share offers with prospects.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/sales/quotations/new')}>
          Create Quotation
        </Button>
      </div>
      
      <Card>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          {/* Filters */}
          <Space wrap>
            <Select
              placeholder="Filter by status"
              allowClear
              style={{ width: 200 }}
              value={statusFilter}
              onChange={setStatusFilter}
              options={[
                { label: 'Quotation', value: 'quotation' },
                { label: 'Quotation Sent', value: 'quotation_sent' },
                { label: 'Accepted', value: 'accepted' },
                { label: 'Rejected', value: 'rejected' },
                { label: 'Cancelled', value: 'cancelled' },
                { label: 'Expired', value: 'expired' },
              ]}
            />
            <Input
              placeholder="Search quotation number or customer..."
              prefix={<SearchOutlined />}
              allowClear
              style={{ width: 300 }}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </Space>

          {/* Table */}
          <Table<Quotation>
            rowKey="id"
            columns={columns}
            dataSource={quotations}
            loading={isLoading}
            pagination={{ pageSize: 10 }}
            onRow={(record) => ({
              onClick: () => navigate(`/sales/quotations/${record.id}`),
              style: { cursor: 'pointer' },
            })}
          />
        </Space>
      </Card>
    </div>
  );
};

export default QuotationsPage;
