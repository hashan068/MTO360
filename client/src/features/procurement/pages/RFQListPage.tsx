/**
 * RFQ List Page - Phase 2: RFQ & Competitive Bidding
 */
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { Card, Table, Typography, Button, Input, Select, Space } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { rfqApi } from '../api/procurementApi';
import type { ProcurementRFQ, RFQStatus } from '../types';
import { ProcurementStatusBadge } from '../components/StatusBadge';

const RFQListPage = () => {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<RFQStatus | undefined>(undefined);
  const [searchText, setSearchText] = useState<string>('');

  const {
    data: rfqs = [],
    isLoading,
  } = useQuery<ProcurementRFQ[]>({
    queryKey: ['procurement', 'rfqs', 'list', statusFilter, searchText],
    queryFn: () => rfqApi.listRFQs({
      status: statusFilter,
      limit: 100,
    }),
  });

  const filteredRFQs = rfqs.filter(rfq =>
    searchText === '' ||
    rfq.rfq_number.toLowerCase().includes(searchText.toLowerCase()) ||
    rfq.component_name?.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns: ColumnsType<ProcurementRFQ> = [
    {
      title: 'RFQ Number',
      dataIndex: 'rfq_number',
      key: 'rfq_number',
      width: 140,
      render: (value) => <span style={{ fontWeight: 500 }}>{value}</span>,
    },
    {
      title: 'Component',
      dataIndex: 'component_name',
      key: 'component_name',
      ellipsis: true,
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      render: (value) => value.toLocaleString(),
    },
    {
      title: 'Required By',
      dataIndex: 'required_by_date',
      key: 'required_by_date',
      width: 140,
      render: (value) => dayjs(value).format('MMM D, YYYY'),
    },
    {
      title: 'Closing Date',
      dataIndex: 'closing_datetime',
      key: 'closing_datetime',
      width: 160,
      render: (value) => {
        const closingDate = dayjs(value);
        const isClosingSoon = closingDate.diff(dayjs(), 'hour') < 24 && closingDate.isAfter(dayjs());
        return (
          <span style={{ color: isClosingSoon ? '#faad14' : undefined }}>
            {closingDate.format('MMM D, YYYY HH:mm')}
          </span>
        );
      },
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 140,
      render: (value: RFQStatus) => <ProcurementStatusBadge status={value} type="rfq" />,
    },
    {
      title: 'Quotes',
      dataIndex: 'quotes_count',
      key: 'quotes_count',
      width: 80,
      render: (value) => value || 0,
    },
  ];

  const handleRowClick = (record: ProcurementRFQ) => {
    navigate(`/procurement/rfqs/${record.id}`);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            Request for Quotations (RFQs)
          </Typography.Title>
          <Typography.Text type="secondary">
            Manage competitive bidding and supplier quotes.
          </Typography.Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/procurement/rfqs/create')}
        >
          Create RFQ
        </Button>
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
                { label: 'Draft', value: 'draft' },
                { label: 'Sent', value: 'sent' },
                { label: 'Quotes Received', value: 'quotes_received' },
                { label: 'Awarded', value: 'awarded' },
                { label: 'Cancelled', value: 'cancelled' },
              ]}
            />
            <Input
              placeholder="Search by RFQ number or component"
              prefix={<SearchOutlined />}
              allowClear
              style={{ width: 300 }}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </Space>

          <Table<ProcurementRFQ>
            rowKey="id"
            columns={columns}
            dataSource={filteredRFQs || []}
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

export default RFQListPage;
