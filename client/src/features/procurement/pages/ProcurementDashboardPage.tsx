/**
 * Procurement Module Main Dashboard
 */
import { ShoppingCartOutlined, FileTextOutlined, ContainerOutlined, BarChartOutlined, DollarOutlined } from '@ant-design/icons';
import { Card, Row, Col, Statistic, Space, Typography, Button } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  supplierPerformanceApi,
  rfqApi,
  contractApi,
  inventoryOptimizationApi
} from '../api/procurementApi';

const ProcurementDashboardPage = () => {
  const navigate = useNavigate();

  // Fetch summary data
  const { data: rankings = [] } = useQuery({
    queryKey: ['procurement', 'supplier-rankings', 10],
    queryFn: () => supplierPerformanceApi.getSupplierRankings(10),
  });

  const { data: rfqs = [] } = useQuery({
    queryKey: ['procurement', 'rfqs', 'list'],
    queryFn: () => rfqApi.listRFQs({ limit: 100 }),
  });

  const { data: contracts = [] } = useQuery({
    queryKey: ['procurement', 'contracts', 'list'],
    queryFn: () => contractApi.listContracts({ limit: 100 }),
  });

  const { data: belowROPComponents = [] } = useQuery({
    queryKey: ['procurement', 'inventory', 'below-rop'],
    queryFn: () => inventoryOptimizationApi.getComponentsBelowROP(),
  });

  const activeRFQs = rfqs.filter(r => r.status === 'sent' || r.status === 'quotes_received').length;
  const activeContracts = contracts.filter(c => c.status === 'active').length;
  const urgentComponents = belowROPComponents.filter(c => c.priority === 'high').length;
  const avgSupplierScore = rankings.length > 0
    ? rankings.reduce((sum, r) => sum + r.overall_score, 0) / rankings.length
    : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
          <ShoppingCartOutlined /> Procurement Dashboard
        </Typography.Title>
        <Typography.Text type="secondary">
          Advanced procurement & supplier management overview.
        </Typography.Text>
      </div>

      {/* Key Metrics */}
      <Row gutter={16}>
        <Col span={6}>
          <Card
            hoverable
            onClick={() => navigate('/procurement/suppliers/rankings')}
            style={{ cursor: 'pointer' }}
          >
            <Statistic
              title="Avg Supplier Score"
              value={avgSupplierScore.toFixed(1)}
              suffix="%"
              valueStyle={{ color: avgSupplierScore >= 80 ? '#3f8600' : '#cf1322' }}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {rankings.length} suppliers ranked
            </Typography.Text>
          </Card>
        </Col>
        <Col span={6}>
          <Card
            hoverable
            onClick={() => navigate('/procurement/rfqs')}
            style={{ cursor: 'pointer' }}
          >
            <Statistic
              title="Active RFQs"
              value={activeRFQs}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: activeRFQs > 0 ? '#1890ff' : undefined }}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {rfqs.length} total RFQs
            </Typography.Text>
          </Card>
        </Col>
        <Col span={6}>
          <Card
            hoverable
            onClick={() => navigate('/procurement/contracts')}
            style={{ cursor: 'pointer' }}
          >
            <Statistic
              title="Active Contracts"
              value={activeContracts}
              prefix={<ContainerOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              {contracts.length} total contracts
            </Typography.Text>
          </Card>
        </Col>
        <Col span={6}>
          <Card
            hoverable
            onClick={() => navigate('/procure/inventory/below-rop')}
            style={{ cursor: 'pointer', borderColor: urgentComponents > 0 ? '#ff4d4f' : undefined }}
          >
            <Statistic
              title="Components Below ROP"
              value={belowROPComponents.length}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: urgentComponents > 0 ? '#cf1322' : undefined }}
            />
            <Typography.Text type="secondary" style={{ fontSize: 12, color: urgentComponents > 0 ? '#cf1322' : undefined }}>
              {urgentComponents} urgent priority
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Card title="Quick Actions">
        <Space wrap size="large">
          <Button
            type="primary"
            icon={<FileTextOutlined />}
            size="large"
            onClick={() => navigate('/procurement/rfqs/create')}
          >
            Create RFQ
          </Button>
          <Button
            icon={<ContainerOutlined />}
            size="large"
            onClick={() => navigate('/procurement/contracts/create')}
          >
            Create Contract
          </Button>
          <Button
            icon={<BarChartOutlined />}
            size="large"
            onClick={() => navigate('/procurement/inventory/abc-analysis')}
          >
            Run ABC Analysis
          </Button>
          <Button
            icon={<DollarOutlined />}
            size="large"
            onClick={() => navigate('/procurement/cost-analysis')}
          >
            View Cost Analysis
          </Button>
        </Space>
      </Card>

      {/* Module Overview */}
      <Row gutter={16}>
        <Col span={12}>
          <Card title="Module Features" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div><strong>✓ Supplier Performance Management</strong> - Monthly scoring & rankings</div>
              <div><strong>✓ RFQ & Competitive Bidding</strong> - Complete lifecycle management</div>
              <div><strong>✓ Contract Management</strong> - Pricing, volume discounts, expiry tracking</div>
              <div><strong>✓ Inventory Optimization</strong> - ROP, EOQ, ABC analysis</div>
              <div><strong>✓ Cost Analysis & Reporting</strong> - Spend analysis, budget tracking</div>
            </Space>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Recent Activity" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Typography.Text type="secondary">
                Click on metric cards above to navigate to detailed views.
              </Typography.Text>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ProcurementDashboardPage;
