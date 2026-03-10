/**
 * Inventory Optimization Dashboard - Phase 4: Inventory Optimization
 */
import { AlertOutlined, BarChartOutlined, ReloadOutlined } from '@ant-design/icons';
import { Card, Table, Typography, Button, Space, Tag, Row, Col, Statistic, Progress } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { inventoryOptimizationApi } from '../api/procurementApi';
import type { ComponentBelowROP } from '../types';

const InventoryOptimizationPage = () => {
  const navigate = useNavigate();

  const {
    data: belowROPComponents = [],
    isLoading,
    refetch,
  } = useQuery<ComponentBelowROP[]>({
    queryKey: ['procurement', 'inventory', 'below-rop'],
    queryFn: () => inventoryOptimizationApi.getComponentsBelowROP(),
  });

  const urgentCount = belowROPComponents.filter(c => c.priority === 'high').length;
  const mediumCount = belowROPComponents.filter(c => c.priority === 'medium').length;
  const lowCount = belowROPComponents.filter(c => c.priority === 'low').length;

  const columns: ColumnsType<ComponentBelowROP> = [
    {
      title: 'Component',
      dataIndex: 'component_name',
      key: 'component_name',
      ellipsis: true,
      render: (value, record) => (
        <Space direction="vertical" size={0}>
          <span style={{ fontWeight: 500 }}>{value}</span>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            ID: {record.component_id}
          </Typography.Text>
        </Space>
      ),
    },
    {
      title: 'Current Stock',
      dataIndex: 'current_stock',
      key: 'current_stock',
      width: 120,
      render: (value, record) => (
        <Space direction="vertical" size={0} style={{ width: '100%' }}>
          <span>{value.toLocaleString()}</span>
          <Progress
            percent={(value / record.reorder_point) * 100}
            size="small"
            strokeColor={value <= record.safety_stock ? '#ff4d4f' : '#faad14'}
            showInfo={false}
          />
        </Space>
      ),
      sorter: (a, b) => a.current_stock - b.current_stock,
    },
    {
      title: 'Reorder Point',
      dataIndex: 'reorder_point',
      key: 'reorder_point',
      width: 120,
      render: (value) => value.toLocaleString(),
    },
    {
      title: 'Stock Deficit',
      dataIndex: 'stock_deficit',
      key: 'stock_deficit',
      width: 120,
      render: (value) => (
        <span style={{ color: '#ff4d4f', fontWeight: 500 }}>
          -{value.toLocaleString()}
        </span>
      ),
      sorter: (a, b) => b.stock_deficit - a.stock_deficit,
    },
    {
      title: 'Recommended Order',
      dataIndex: 'recommended_order_qty',
      key: 'recommended_order_qty',
      width: 150,
      render: (value) => (
        <Tag color="blue">{value.toLocaleString()} units</Tag>
      ),
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: 'high' | 'medium' | 'low') => {
        const config = {
          high: { color: 'error', text: 'Urgent', icon: <AlertOutlined /> },
          medium: { color: 'warning', text: 'Medium', icon: null },
          low: { color: 'default', text: 'Low', icon: null },
        };
        const { color, text, icon } = config[priority];
        return (
          <Tag color={color} icon={icon}>
            {text}
          </Tag>
        );
      },
      filters: [
        { text: 'Urgent', value: 'high' },
        { text: 'Medium', value: 'medium' },
        { text: 'Low', value: 'low' },
      ],
      onFilter: (value, record) => record.priority === value,
    },
    {
      title: 'Pending PR',
      dataIndex: 'has_pending_pr',
      key: 'has_pending_pr',
      width: 110,
      render: (value) => value ? <Tag color="processing">Yes</Tag> : <Tag>No</Tag>,
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            <BarChartOutlined /> Inventory Optimization
          </Typography.Title>
          <Typography.Text type="secondary">
            Components below reorder point needing replenishment.
          </Typography.Text>
        </div>
        <Space>
          <Button
            icon={<BarChartOutlined />}
            onClick={() => navigate('/procurement/inventory/abc-analysis')}
          >
            ABC Analysis
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => refetch()}
            loading={isLoading}
          >
            Refresh
          </Button>
        </Space>
      </div>

      {/* Summary Cards */}
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Below ROP"
              value={belowROPComponents.length}
              valueStyle={{ color: belowROPComponents.length > 0 ? '#cf1322' : '#3f8600' }}
              suffix="components"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Urgent Priority"
              value={urgentCount}
              valueStyle={{ color: urgentCount > 0 ? '#cf1322' : undefined }}
              prefix={<AlertOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Medium Priority"
              value={mediumCount}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Low Priority"
              value={lowCount}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Table<ComponentBelowROP>
          rowKey="component_id"
          columns={columns}
          dataSource={belowROPComponents || []}
          loading={isLoading}
          pagination={{ pageSize: 20, showTotal: (total) => `Total ${total} components` }}
        />
      </Card>
    </div>
  );
};

export default InventoryOptimizationPage;
