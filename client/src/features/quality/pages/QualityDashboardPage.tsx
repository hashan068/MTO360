import { Row, Col, Typography, Button, Alert } from 'antd';
import { ReloadOutlined, WarningOutlined, CheckCircleOutlined, DollarOutlined, StopOutlined } from '@ant-design/icons';
import { useQualityDashboard } from '../hooks/useQualityMetrics';
import { QualityMetricsCard } from '../components/QualityMetricsCard';
import { RecentDefectsList } from '../components/RecentDefectsList';
import { ActiveHoldsTable } from '../components/ActiveHoldsTable';

const QualityDashboardPage = () => {
  const { data, isLoading, refetch, isError } = useQualityDashboard();

  if (isError) {
    return (
      <Alert
        message="Error loading dashboard"
        description="Could not fetch quality metrics. Please try again later."
        type="error"
        showIcon
        action={<Button onClick={() => refetch()}>Retry</Button>}
      />
    );
  }

  const metrics = data?.metrics;

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Typography.Title level={2} style={{ margin: 0 }}>
            Quality Dashboard
          </Typography.Title>
          <Typography.Text type="secondary">
            Overview of quality performance and critical issues
          </Typography.Text>
        </div>
        <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
          Refresh
        </Button>
      </div>

      {/* KPI Cards */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <QualityMetricsCard
            title="First Pass Yield"
            value={metrics?.first_pass_yield ? `${metrics.first_pass_yield}%` : '-'}
            prefix={<CheckCircleOutlined />}
            loading={isLoading}
            color="#3f8600"
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <QualityMetricsCard
            title="Defect Rate (DPMO)"
            value={metrics?.defect_rate ?? '-'}
            prefix={<WarningOutlined />}
            loading={isLoading}
            color="#cf1322"
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <QualityMetricsCard
            title="Active Holds"
            value={metrics?.active_holds ?? '-'}
            prefix={<StopOutlined />}
            loading={isLoading}
            color="#d46b08"
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <QualityMetricsCard
            title="Cost of Quality"
            value={metrics?.cost_of_quality ?? '-'}
            prefix={<DollarOutlined />}
            loading={isLoading}
            precision={2}
          />
        </Col>
      </Row>

      {/* Main Content */}
      <Row gutter={[24, 24]}>
        {/* Left Column: Charts & Tables */}
        <Col xs={24} lg={16} className="space-y-6">
          {/* Active Holds */}
          <ActiveHoldsTable holds={data?.active_holds || []} loading={isLoading} />

          {/* Placeholder for Trend Chart (Phase 9C) */}
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 h-64 flex items-center justify-center text-gray-400">
            Quality Trend Chart (Coming Soon)
          </div>
        </Col>

        {/* Right Column: Lists & Alerts */}
        <Col xs={24} lg={8} className="space-y-6">
          {/* Recent Defects */}
          <RecentDefectsList defects={data?.recent_defects || []} loading={isLoading} />

          {/* Overdue NCRs Alert */}
          {data?.overdue_ncrs && data.overdue_ncrs.length > 0 && (
            <Alert
              message="Overdue NCRs"
              description={`${data.overdue_ncrs.length} Non-Conformance Reports are overdue.`}
              type="error"
              showIcon
              action={
                <Button size="small" type="link" href="/quality/ncrs?status=overdue">
                  View
                </Button>
              }
            />
          )}
        </Col>
      </Row>
    </div>
  );
};

export default QualityDashboardPage;

