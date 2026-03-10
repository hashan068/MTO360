/**
 * Contract List Page - Phase 3: Contract Management
 */
import { PlusOutlined, SearchOutlined, CalendarOutlined } from '@ant-design/icons';
import { Card, Table, Typography, Button, Input, Select, Space, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { contractApi } from '../api/procurementApi';
import type { SupplierContract, ContractStatus } from '../types';
import { ProcurementStatusBadge } from '../components/StatusBadge';

const ContractListPage = () => {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<ContractStatus | undefined>(undefined);
  const [searchText, setSearchText] = useState<string>('');

  const {
    data: contracts = [],
    isLoading,
  } = useQuery<SupplierContract[]>({
    queryKey: ['procurement', 'contracts', 'list', statusFilter],
    queryFn: () => contractApi.listContracts({
      status: statusFilter,
      limit: 100,
    }),
  });

  const filteredContracts = contracts.filter(contract =>
    searchText === '' ||
    contract.contract_number.toLowerCase().includes(searchText.toLowerCase()) ||
    contract.supplier_name?.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns: ColumnsType<SupplierContract> = [
    {
      title: 'Contract Number',
      dataIndex: 'contract_number',
      key: 'contract_number',
      width: 160,
      render: (value) => <span style={{ fontWeight: 500 }}>{value}</span>,
    },
    {
      title: 'Supplier',
      dataIndex: 'supplier_name',
      key: 'supplier_name',
      ellipsis: true,
    },
    {
      title: 'Start Date',
      dataIndex: 'start_date',
      key: 'start_date',
      width: 120,
      render: (value) => dayjs(value).format('MMM D, YYYY'),
    },
    {
      title: 'End Date',
      dataIndex: 'end_date',
      key: 'end_date',
      width: 140,
      render: (value, record) => {
        const endDate = dayjs(value);
        const daysUntilExpiry = endDate.diff(dayjs(), 'day');
        const isExpiringSoon = daysUntilExpiry > 0 && daysUntilExpiry <= 90;

        return (
          <Space direction="vertical" size={0}>
            <span style={{ color: isExpiringSoon ? '#faad14' : undefined }}>
              {endDate.format('MMM D, YYYY')}
            </span>
            {isExpiringSoon && (
              <Tag color="warning" style={{ margin: 0 }}>
                <CalendarOutlined /> {daysUntilExpiry} days left
              </Tag>
            )}
          </Space>
        );
      },
    },
    {
      title: 'Payment Terms',
      dataIndex: 'payment_terms',
      key: 'payment_terms',
      width: 120,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (value: ContractStatus) => <ProcurementStatusBadge status={value} type="contract" />,
    },
    {
      title: 'Auto-Renew',
      dataIndex: 'auto_renew',
      key: 'auto_renew',
      width: 100,
      render: (value) => value ? <Tag color="green">Yes</Tag> : <Tag>No</Tag>,
    },
  ];

  const handleRowClick = (record: SupplierContract) => {
    navigate(`/procurement/contracts/${record.id}`);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            Supplier Contracts
          </Typography.Title>
          <Typography.Text type="secondary">
            Manage supplier agreements, pricing, and volume discounts.
          </Typography.Text>
        </div>
        <Space>
          <Button
            icon={<CalendarOutlined />}
            onClick={() => navigate('/procurement/contracts/expiring')}
          >
            Expiring Contracts
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/procurement/contracts/create')}
          >
            Create Contract
          </Button>
        </Space>
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
                { label: 'Active', value: 'active' },
                { label: 'Expired', value: 'expired' },
                { label: 'Cancelled', value: 'cancelled' },
              ]}
            />
            <Input
              placeholder="Search by contract number or supplier"
              prefix={<SearchOutlined />}
              allowClear
              style={{ width: 350 }}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </Space>

          <Table<SupplierContract>
            rowKey="id"
            columns={columns}
            dataSource={filteredContracts || []}
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

export default ContractListPage;
