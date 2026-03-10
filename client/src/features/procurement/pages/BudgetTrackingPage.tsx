/**
 * Budget Tracking Page - Phase 5: Cost Analysis
 */
import { DollarOutlined, ReloadOutlined, EditOutlined } from '@ant-design/icons';
import { Card, Table, Typography, Button, Space, Progress, Tag, Statistic, Row, Col } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import dayjs from 'dayjs';
import { costAnalysisApi } from '../api/procurementApi';
import type { BudgetTracking, ProcurementBudget } from '../types';
import { formatCurrency } from '@/shared/utils/format';

const BudgetTrackingPage = () => {
  const queryClient = useQueryClient();
  const [fiscalYear] = useState(dayjs().year());

  const {
    data: budgetTracking,
    isLoading,
  } = useQuery<BudgetTracking>({
    queryKey: ['procurement', 'budgets', fiscalYear],
    queryFn: () => costAnalysisApi.getBudgetTracking(fiscalYear),
  });

  const refreshMutation = useMutation({
    mutationFn: () => costAnalysisApi.refreshBudgetActuals(fiscalYear),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['procurement', 'budgets', fiscalYear] });
    },
  });

  const columns: ColumnsType<ProcurementBudget> = [
    {
      title: 'Category',
      dataIndex: 'category_name',
      key: 'category_name',
      render: (value) => value || 'Overall',
      ellipsis: true,
    },
    {
      title: 'Budgeted Amount',
      dataIndex: 'budgeted_amount',
      key: 'budgeted_amount',
      width: 150,
      render: (value) => formatCurrency(value),
      sorter: (a, b) => a.budgeted_amount - b.actual_spend,
    },
    {
      title: 'Actual Spend',
      dataIndex: 'actual_spend',
      key: 'actual_spend',
      width: 150,
      render: (value) => formatCurrency(value),
      sorter: (a, b) => a.actual_spend - b.actual_spend,
    },
    {
      title: 'Variance',
      dataIndex: 'variance',
      key: 'variance',
      width: 130,
      render: (value) => (
        <span style={{ color: value >= 0 ? '#3f8600' : '#cf1322', fontWeight: 500 }}>
          {value >= 0 ? '+' : ''}{formatCurrency(value)}
        </span>
      ),
      sorter: (a, b) => a.variance - b.variance,
    },
    {
      title: 'Consumed',
      dataIndex: 'consumed_pct',
      key: 'consumed_pct',
      width: 180,
      render: (pct = 0, record) => {
        const status = pct >= 100 ? 'exception' : pct >= 90 ? 'active' : 'normal';
        return (
          <Space direction="vertical" size={0} style={{ width: '100%' }}>
            <Progress
              percent={Math.min(pct, 100)}
              status={status}
              strokeColor={pct >= 100 ? '#ff4d4f' : pct >= 90 ? '#faad14' : '#52c41a'}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {pct.toFixed(1)}%
            </Typography.Text>
          </Space>
        );
      },
      sorter: (a, b) => (a.consumed_pct || 0) - (b.consumed_pct || 0),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status?: string) => {
        const config = {
          on_track: { color: 'success', text: 'On Track' },
          at_risk: { color: 'warning', text: 'At Risk' },
          over_budget: { color: 'error', text: 'Over Budget' },
        };
        const { color, text } = config[status as keyof typeof config] || { color: 'default', text: 'Unknown' };
        return <Tag color={color}>{text}</Tag>;
      },
      filters: [
        { text: 'On Track', value: 'on_track' },
        { text: 'At Risk', value: 'at_risk' },
        { text: 'Over Budget', value: 'over_budget' },
      ],
      onFilter: (value, record) => record.status === value,
    },
  ];

  const getOverallStatus = () => {
    const pct = budgetTracking?.overall_consumed_pct || 0;
    if (pct >= 100) return { color: 'error', text: 'Over Budget' };
    if (pct >= 90) return { color: 'warning', text: 'At Risk' };
    return { color: 'success', text: 'On Track' };
  };

  const overallStatus = getOverallStatus();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            <DollarOutlined /> Budget Tracking - FY {fiscalYear}
          </Typography.Title>
          <Typography.Text type="secondary">
            Procurement budget tracking and variance analysis.
          </Typography.Text>
        </div>
        <Space>
          <Button
            icon={<EditOutlined />}
          >
            Manage Budgets
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => refreshMutation.mutate()}
            loading={refreshMutation.isPending || isLoading}
          >
            Refresh Actuals
          </Button>
        </Space>
      </div>

      {/* Overall Summary */}
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Total Budget"
              value={budgetTracking?.overall_total_budget || 0}
              prefix="$"
              precision={0}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Actual Spend (YTD)"
              value={budgetTracking?.overall_total_actual || 0}
              prefix="$"
              precision={0}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Statistic
                title="Overall Status"
                value={budgetTracking?.overall_consumed_pct.toFixed(1) || 0}
                suffix="%"
                valueStyle={{ color: overallStatus.color === 'error' ? '#cf1322' : overallStatus.color === 'warning' ? '#faad14' : '#3f8600' }}
              />
              <Tag color={overallStatus.color}>{overallStatus.text}</Tag>
              <Progress
                percent={Math.min(budgetTracking?.overall_consumed_pct || 0, 100)}
                status={budgetTracking?.overall_consumed_pct && budgetTracking.overall_consumed_pct >= 100 ? 'exception' : budgetTracking?.overall_consumed_pct && budgetTracking.overall_consumed_pct >= 90 ? 'active' : 'normal'}
              />
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Budget Details Table */}
      <Card>
        <Table<ProcurementBudget>
          rowKey="id"
          columns={columns}
          dataSource={budgetTracking?.budgets || []}
          loading={isLoading}
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </div>
  );
};

export default BudgetTrackingPage;
