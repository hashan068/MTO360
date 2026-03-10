import { Card, Row, Col, Typography, Select, DatePicker } from 'antd';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, ComposedChart } from 'recharts';
import { useQualityDashboard } from '../hooks/useQualityMetrics';

const { RangePicker } = DatePicker;

const QualityAnalyticsPage = () => {
  const { data, isLoading } = useQualityDashboard(30);

  // Mock data for charts (since API might not return exact shape yet)
  const trendData = data?.trends || [
    { date: '2023-10-01', fpy: 92, defects: 5 },
    { date: '2023-10-02', fpy: 94, defects: 3 },
    { date: '2023-10-03', fpy: 91, defects: 6 },
    { date: '2023-10-04', fpy: 95, defects: 2 },
    { date: '2023-10-05', fpy: 96, defects: 2 },
    { date: '2023-10-06', fpy: 93, defects: 4 },
    { date: '2023-10-07', fpy: 97, defects: 1 },
  ];

  const paretoData = [
    { name: 'Dimensional', count: 45, cumulative: 45 },
    { name: 'Visual', count: 25, cumulative: 70 },
    { name: 'Material', count: 15, cumulative: 85 },
    { name: 'Assembly', count: 10, cumulative: 95 },
    { name: 'Other', count: 5, cumulative: 100 },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Typography.Title level={2} style={{ margin: 0 }}>
            Quality Analytics
          </Typography.Title>
          <Typography.Text type="secondary">
            Performance trends and defect analysis
          </Typography.Text>
        </div>
        <div className="flex gap-2">
          <RangePicker />
          <Select defaultValue="all" options={[{ label: 'All Products', value: 'all' }]} className="w-40" />
        </div>
      </div>

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card title="First Pass Yield Trend" loading={isLoading}>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[80, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="fpy" stroke="#3f8600" name="FPY %" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Defect Rate Trend" loading={isLoading}>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="defects" fill="#cf1322" name="Defect Count" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        <Col xs={24}>
          <Card title="Defect Pareto Analysis" loading={isLoading}>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={paretoData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Bar yAxisId="left" dataKey="count" fill="#1890ff" name="Defect Count" barSize={40} />
                  <Line yAxisId="right" type="monotone" dataKey="cumulative" stroke="#faad14" name="Cumulative %" strokeWidth={2} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default QualityAnalyticsPage;

