import { BarChartOutlined, CloudDownloadOutlined } from '@ant-design/icons';
import { App as AntdApp, Button, Card, Col, Row, Statistic, Typography } from 'antd';
import { useMutation, useQuery } from '@tanstack/react-query';
import { saveAs } from 'file-saver';
import { componentsApi, downloadInventoryReport, purchaseRequisitionsApi } from '@/features/inventory/api';
import type { Component, PurchaseRequisition } from '@/features/inventory/types';

const InventoryReportsPage = () => {
  const { message } = AntdApp.useApp();

  const { data: components = [] } = useQuery<Component[]>({
    queryKey: ['inventory', 'components', 'reports'],
    queryFn: () => componentsApi.list({ limit: 200 }),
  });

  const { data: requisitions = [] } = useQuery<PurchaseRequisition[]>({
    queryKey: ['inventory', 'requisitions', 'reports'],
    queryFn: () => purchaseRequisitionsApi.list({ limit: 200 }),
  });

  const reportMutation = useMutation({
    mutationFn: downloadInventoryReport,
    onSuccess: (blob) => {
      saveAs(blob, `inventory-report-${new Date().toISOString().slice(0, 10)}.xlsx`);
      message.success('Inventory report downloaded');
    },
    onError: () => message.error('Unable to generate report'),
  });

  const lowStockCount = components.filter((component) => component.quantity <= component.reorder_level).length;
  const pendingRequisitions = requisitions.filter((req) => req.status === 'PENDING').length;

  return (
    <div className="space-y-6">
      <Typography.Title level={3}>Inventory Reports</Typography.Title>
      <Typography.Paragraph type="secondary">
        Export data for further analysis and share updates with stakeholders.
      </Typography.Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="Tracked Components" value={components.length} prefix={<BarChartOutlined />} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="Low Stock Items" value={lowStockCount} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="Pending Requisitions" value={pendingRequisitions} suffix="open" />
          </Card>
        </Col>
      </Row>

      <Card>
        <Typography.Paragraph>
          Generate an Excel snapshot containing component levels, requisition activity, and supplier performance.
        </Typography.Paragraph>
        <Button
          type="primary"
          icon={<CloudDownloadOutlined />}
          loading={reportMutation.isPending}
          onClick={() => reportMutation.mutate()}
        >
          Download Excel Report
        </Button>
      </Card>
    </div>
  );
};

export default InventoryReportsPage;

