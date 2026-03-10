/**
 * Cost Analysis Dashboard - Phase 5: Cost Analysis & Reporting
 */
import { DollarOutlined, LineChartOutlined, PieChartOutlined } from '@ant-design/icons';
import { Card, Typography, Row, Col, Statistic, DatePicker, Select, Space, Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import dayjs from 'dayjs';
import { costAnalysisApi } from '../api/procurementApi';
import type { SpendAnalysis, SpendAnalysisItem } from '../types';
import { formatCurrency } from '@/shared/utils/format';

const { RangePicker } = DatePicker;

const CostAnalysisPage = () => {
  const [dateRange, setDateRange] = useState<[string, string]>([
    dayjs().subtract(1, 'year').format('YYYY-MM-DD'),
    dayjs().format('YYYY-MM-DD'),
  ]);
  const [groupBy, setGroupBy] = useState<'supplier' | 'category' | 'month'>('supplier');

  const {
    data: spendAnalysis,
    isLoading,
  } = useQuery<SpendAnalysis>({
    queryKey: ['procurement', 'cost-analysis', 'spend', dateRange, groupBy],
    queryFn: () => costAnalysisApi.analyzeSpend(dateRange[0], dateRange[1], groupBy),
    enabled: !!dateRange,
  });

  const columns: ColumnsType<SpendAnalysisItem> = [
    {
      title: groupBy === 'supplier' ? 'Supplier' : groupBy === 'category' ? 'Category' : 'Month',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: 'Total Spend',
      dataIndex: 'spend',
      key: 'spend',
      width: 150,
      render: (value) => formatCurrency(value),
      sorter: (a, b) => a.spend - b.spend,
    },
    {
      title: 'Percentage',
      dataIndex: 'percentage',
      key: 'percentage',
      width: 120,
      render: (value) => `${value.toFixed(1)}%`,
      sorter: (a, b) => a.percentage - b.percentage,
    },
    {
      title: 'Orders',
      dataIndex: 'order_count',
      key: 'order_count',
      width: 100,
      render: (value) => value.toLocaleString(),
      sorter: (a, b) => a.order_count - b.order_count,
    },
    {
      title: 'Avg Order Value',
      dataIndex: 'avg_order_value',
      key: 'avg_order_value',
      width: 150,
      render: (value) => formatCurrency(value),
      sorter: (a, b) => a.avg_order_value - b.avg_order_value,
    },
  ];

  const handleDateRangeChange = (dates: any) => {
    if (dates && dates[0] && dates[1]) {
      setDateRange([
        dates[0].format('YYYY-MM-DD'),
        dates[1].format('YYYY-MM-DD'),
      ]);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            <DollarOutlined /> Cost Analysis & Reporting
          </Typography.Title>
          <Typography.Text type="secondary">
            Procurement spend analysis and budget tracking.
          </Typography.Text>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <Space wrap>
          <RangePicker
            value={[dayjs(dateRange[0]), dayjs(dateRange[1])]}
            onChange={handleDateRangeChange}
            style={{ width: 280 }}
          />
          <Select
            value={groupBy}
            onChange={setGroupBy}
            style={{ width: 150 }}
            options={[
              { label: 'By Supplier', value: 'supplier' },
              { label: 'By Category', value: 'category' },
              { label: 'By Month', value: 'month' },
            ]}
          />
        </Space>
      </Card>

      {/* Summary Cards */}
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Total Spend"
              value={spendAnalysis?.total_spend || 0}
              prefix="$"
              precision={2}
              valueStyle={{ color: '#3f8600' }}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {dayjs(dateRange[0]).format('MMM D, YYYY')} - {dayjs(dateRange[1]).format('MMM D, YYYY')}
            </Typography.Text>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Top 3 Supplier Concentration"
              value={spendAnalysis?.concentration.top_3_pct || 0}
              suffix="%"
              precision={1}
              prefix={<PieChartOutlined />}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              Spend concentrated in top 3 suppliers
            </Typography.Text>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Top 10 Supplier Concentration"
              value={spendAnalysis?.concentration.top_10_pct || 0}
              suffix="%"
              precision={1}
              prefix={<LineChartOutlined />}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              Spend concentrated in top 10 suppliers
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      {/* Spend Breakdown Table */}
      <Card title="Spend Breakdown">
        <Table<SpendAnalysisItem>
          rowKey="name"
          columns={columns}
          dataSource={spendAnalysis?.breakdown || []}
          loading={isLoading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Top 10 Suppliers */}
      {groupBy === 'supplier' && spendAnalysis?.top_10_suppliers && (
        <Card title="Top 10 Suppliers">
          <Table<SpendAnalysisItem>
            rowKey="name"
            columns={columns}
            dataSource={spendAnalysis.top_10_suppliers}
            pagination={false}
          />
        </Card>
      )}
    </div>
  );
};

export default CostAnalysisPage;
