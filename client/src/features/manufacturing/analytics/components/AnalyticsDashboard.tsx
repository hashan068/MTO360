/**
 * Analytics Dashboard Component
 * Main analytics dashboard with charts and metrics
 */
import { useState } from 'react';
import { Card, DatePicker, Row, Col, Select, Space } from 'antd';
import dayjs, { Dayjs } from 'dayjs';
import {
  useUtilization,
  useBottlenecks,
  useOperationPerformance,
  useCycleTimes,
} from '../hooks/useAnalytics';
import { useWorkCenters } from '../../work-centers/hooks/useWorkCenters';
import { UtilizationChart } from '../components/UtilizationChart';
import { PerformanceMetrics } from '../components/PerformanceMetrics';
import { BottleneckView } from '../components/BottleneckView';
import { CycleTimeChart } from '../components/CycleTimeChart';

const { RangePicker } = DatePicker;

export const AnalyticsDashboard = () => {
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs]>([
    dayjs().subtract(30, 'days'),
    dayjs(),
  ]);
  const [selectedWorkCenter, setSelectedWorkCenter] = useState<number | undefined>();
  const [selectedProduct, setSelectedProduct] = useState<number | undefined>();

  const { data: workCenters } = useWorkCenters();

  // Fetch analytics data
  const { data: utilizationData, isLoading: loadingUtilization } = useUtilization({
    start_date: dateRange[0].format('YYYY-MM-DD'),
    end_date: dateRange[1].format('YYYY-MM-DD'),
    work_center_id: selectedWorkCenter,
  });

  const { data: bottlenecks, isLoading: loadingBottlenecks } = useBottlenecks(10);

  const { data: performanceData, isLoading: loadingPerformance } = useOperationPerformance({
    work_center_id: selectedWorkCenter,
    product_id: selectedProduct,
    start_date: dateRange[0].format('YYYY-MM-DD'),
    end_date: dateRange[1].format('YYYY-MM-DD'),
  });

  const { data: cycleTimeData, isLoading: loadingCycleTimes } = useCycleTimes({
    product_id: selectedProduct,
    start_date: dateRange[0].format('YYYY-MM-DD'),
    end_date: dateRange[1].format('YYYY-MM-DD'),
  });

  return (
    <div className="space-y-6">
      {/* Header with Filters */}
      <Card>
        <div className="flex flex-wrap gap-4 items-center">
          <h2 className="text-2xl font-semibold">Production Analytics</h2>

          <Space wrap>
            <RangePicker
              value={dateRange}
              onChange={(dates) => dates && setDateRange(dates as [Dayjs, Dayjs])}
              format="MMM DD, YYYY"
              presets={[
                { label: 'Last 7 Days', value: [dayjs().subtract(7, 'days'), dayjs()] },
                { label: 'Last 30 Days', value: [dayjs().subtract(30, 'days'), dayjs()] },
                { label: 'Last 90 Days', value: [dayjs().subtract(90, 'days'), dayjs()] },
              ]}
            />

            <Select
              style={{ width: 200 }}
              placeholder="All work centers"
              allowClear
              value={selectedWorkCenter}
              onChange={setSelectedWorkCenter}
            >
              {workCenters?.map((wc) => (
                <Select.Option key={wc.id} value={wc.id}>
                  {wc.name}
                </Select.Option>
              ))}
            </Select>

            <Select
              style={{ width: 200 }}
              placeholder="All products"
              allowClear
              value={selectedProduct}
              onChange={setSelectedProduct}
            >
              {/* In real app, fetch products from API */}
              <Select.Option value={1}>Product A</Select.Option>
              <Select.Option value={2}>Product B</Select.Option>
            </Select>
          </Space>
        </div>
      </Card>

      {/* Charts Grid */}
      <Row gutter={[16, 16]}>
        {/* Utilization Chart */}
        <Col xs={24} lg={12}>
          <UtilizationChart data={utilizationData} isLoading={loadingUtilization} />
        </Col>

        {/* Performance Metrics */}
        <Col xs={24} lg={12}>
          <PerformanceMetrics data={performanceData} isLoading={loadingPerformance} />
        </Col>

        {/* Cycle Time Chart */}
        <Col xs={24} lg={12}>
          <CycleTimeChart data={cycleTimeData} isLoading={loadingCycleTimes} />
        </Col>

        {/* Bottleneck Analysis */}
        <Col xs={24} lg={12}>
          <BottleneckView data={bottlenecks} isLoading={loadingBottlenecks} />
        </Col>
      </Row>

      {/* Export Section */}
      <Card>
        <div className="text-center text-sm text-gray-600">
          <p>Analytics data updated: {new Date().toLocaleString()}</p>
        </div>
      </Card>
    </div>
  );
};
