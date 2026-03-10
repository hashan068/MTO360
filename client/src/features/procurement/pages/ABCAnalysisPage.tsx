/**
 * ABC Analysis Page - Phase 4: Inventory Optimization
 */
import { BarChartOutlined, DownloadOutlined } from '@ant-design/icons';
import { Card, Typography, Table, Tag, Row, Col, Statistic, Space, Button } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { inventoryOptimizationApi } from '../api/procurementApi';
import type { ABCAnalysis, ABCAnalysisComponent, ABCClassification } from '../types';
import { formatCurrency } from '@/shared/utils/format';

const ABCAnalysisPage = () => {
  const {
    data: analysis,
    isLoading,
  } = useQuery<ABCAnalysis>({
    queryKey: ['procurement', 'inventory', 'abc-analysis'],
    queryFn: () => inventoryOptimizationApi.performABCAnalysis(),
  });

  const columns: ColumnsType<ABCAnalysisComponent> = [
    {
      title: 'Component',
      dataIndex: 'component_name',
      key: 'component_name',
      ellipsis: true,
      render: (name, record) => (
        <Space direction="vertical" size={0}>
          <span style={{ fontWeight: 500 }}>{name}</span>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            ID: {record.component_id}
          </Typography.Text>
        </Space>
      ),
    },
    {
      title: 'Classification',
      dataIndex: 'classification',
      key: 'classification',
      width: 120,
      render: (value: ABCClassification) => {
        const config = {
          A: { color: 'error', text: 'Class A - Critical' },
          B: { color: 'warning', text: 'Class B - Important' },
          C: { color: 'success', text: 'Class C - Standard' },
        };
        const { color, text } = config[value];
        return <Tag color={color}>{text}</Tag>;
      },
      filters: [
        { text: 'Class A', value: 'A' },
        { text: 'Class B', value: 'B' },
        { text: 'Class C', value: 'C' },
      ],
      onFilter: (value, record) => record.classification === value,
    },
    {
      title: 'Annual Usage',
      dataIndex: 'annual_usage',
      key: 'annual_usage',
      width: 130,
      render: (value) => value.toLocaleString(),
      sorter: (a, b) => a.annual_usage - b.annual_usage,
    },
    {
      title: 'Unit Cost',
      dataIndex: 'unit_cost',
      key: 'unit_cost',
      width: 120,
      render: (value) => formatCurrency(value),
      sorter: (a, b) => a.unit_cost - b.unit_cost,
    },
    {
      title: 'Annual Value',
      dataIndex: 'annual_value',
      key: 'annual_value',
      width: 150,
      render: (value) => <span style={{ fontWeight: 500 }}>{formatCurrency(value)}</span>,
      sorter: (a, b) => a.annual_value - b.annual_value,
    },
    {
      title: 'Cumulative %',
      dataIndex: 'cumulative_percentage',
      key: 'cumulative_percentage',
      width: 130,
      render: (value) => `${value.toFixed(2)}%`,
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            <BarChartOutlined /> ABC Analysis
          </Typography.Title>
          <Typography.Text type="secondary">
            Pareto analysis (80-15-5 rule) for inventory prioritization.
          </Typography.Text>
        </div>
        <Button icon={<DownloadOutlined />}>Export Report</Button>
      </div>

      {/* Summary Cards */}
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Total Components Analyzed"
              value={analysis?.total_components || 0}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              Total Annual Value: {formatCurrency(analysis?.total_value || 0)}
            </Typography.Text>
          </Card>
        </Col>
        <Col span={8}>
          <Card style={{ borderColor: '#ff4d4f', borderWidth: 2 }}>
            <Statistic
              title="Class A (Critical)"
              value={analysis?.classifications.A.count || 0}
              suffix={`items`}
              valueStyle={{ color: '#cf1322' }}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {analysis?.classifications.A.percentage.toFixed(1)}% of total value <br />
              Value: {formatCurrency(analysis?.classifications.A.value || 0)}
            </Typography.Text>
          </Card>
        </Col>
        <Col span={4}>
          <Card style={{ borderColor: '#faad14', borderWidth: 2 }}>
            <Statistic
              title="Class B"
              value={analysis?.classifications.B.count || 0}
              valueStyle={{ color: '#faad14' }}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {analysis?.classifications.B.percentage.toFixed(1)}% value
            </Typography.Text>
          </Card>
        </Col>
        <Col span={4}>
          <Card style={{ borderColor: '#52c41a', borderWidth: 2 }}>
            <Statistic
              title="Class C"
              value={analysis?.classifications.C.count || 0}
              valueStyle={{ color: '#52c41a' }}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {analysis?.classifications.C.percentage.toFixed(1)}% value
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      {/* Explanation Card */}
      <Card title="ABC Classification Guidelines" size="small">
        <Space direction="vertical">
          <div><Tag color="error">Class A</Tag> <strong>High Value Items:</strong> ~80% of total value, ~20% of items. Require tight control and accurate records.</div>
          <div><Tag color="warning">Class B</Tag> <strong>Medium Value Items:</strong> ~15% of total value, ~30% of items. Moderate control required.</div>
          <div><Tag color="success">Class C</Tag> <strong>Low Value Items:</strong> ~5% of total value, ~50% of items. Simple controls and bulk ordering.</div>
        </Space>
      </Card>

      {/* Components Table */}
      <Card>
        <Table<ABCAnalysisComponent>
          rowKey="component_id"
          columns={columns}
          dataSource={analysis?.components || []}
          loading={isLoading}
          pagination={{ pageSize: 50, showSizeChanger: true, showTotal: (total) => `Total ${total} components` }}
        />
      </Card>
    </div>
  );
};

export default ABCAnalysisPage;
