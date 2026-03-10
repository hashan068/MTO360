import { useMemo } from 'react';
import { ArrowUpOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { Card, Col, Progress, Row, Statistic, Table, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { componentsApi, purchaseOrdersApi, purchaseRequisitionsApi } from '@/features/inventory/api';
import { salesOrdersApi } from '@/features/sales/api';
import { manufacturingOrdersApi } from '@/features/manufacturing/api';
import type { Component, PurchaseOrder, PurchaseRequisition } from '@/features/inventory/types';
import type { SalesOrder } from '@/features/sales/types';
import type { ManufacturingOrder } from '@/features/manufacturing/types';
import { useAuthStore } from '@/features/auth/store/authStore';
import { formatCurrency } from '@/shared/utils/format';

const DashboardPage = () => {
  const isAuthenticated = useAuthStore((state) => Boolean(state.accessToken));
  const navigate = useNavigate();

  const { data: components = [] } = useQuery<Component[]>({
    queryKey: ['inventory', 'components', 'summary'],
    queryFn: () => componentsApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: purchaseRequisitions = [] } = useQuery<PurchaseRequisition[]>({
    queryKey: ['inventory', 'purchase-requisitions', 'summary'],
    queryFn: () => purchaseRequisitionsApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: purchaseOrders = [] } = useQuery<PurchaseOrder[]>({
    queryKey: ['inventory', 'purchase-orders', 'summary'],
    queryFn: () => purchaseOrdersApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: salesOrders = [] } = useQuery<SalesOrder[]>({
    queryKey: ['sales', 'orders', 'summary'],
    queryFn: () => salesOrdersApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: manufacturingOrders = [] } = useQuery<ManufacturingOrder[]>({
    queryKey: ['manufacturing', 'orders', 'summary'],
    queryFn: () => manufacturingOrdersApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const inventoryStats = useMemo(() => {
    const totalStock = components.reduce((sum, component) => sum + component.quantity, 0);
    const lowStockCount = components.filter((component) => component.quantity <= component.reorder_level).length;
    return { totalStock, lowStockCount };
  }, [components]);

  const salesStats = useMemo(() => {
    const totalOrders = salesOrders.length;
    const fulfilled = salesOrders.filter((order) => order.status === 'delivered').length;
    const fulfillmentRate = totalOrders === 0 ? 0 : Math.round((fulfilled / totalOrders) * 100);
    return { totalOrders, fulfilled, fulfillmentRate };
  }, [salesOrders]);

  const manufacturingStats = useMemo(() => {
    const total = manufacturingOrders.length;
    const inProgress = manufacturingOrders.filter((order) => order.status === 'IN_PROGRESS').length;
    return { total, inProgress };
  }, [manufacturingOrders]);

  const requisitionStats = useMemo(() => {
    const pending = purchaseRequisitions.filter((pr) => pr.status === 'PENDING').length;
    const approved = purchaseRequisitions.filter((pr) => pr.status === 'APPROVED').length;
    return { pending, approved };
  }, [purchaseRequisitions]);

  const topComponentsColumns: ColumnsType<Component> = [
    { title: 'Component', dataIndex: 'name', key: 'name' },
    { title: 'Quantity', dataIndex: 'quantity', key: 'quantity' },
    { title: 'Reorder Level', dataIndex: 'reorder_level', key: 'reorder_level' },
    { title: 'Unit', dataIndex: 'unit_of_measure', key: 'unit_of_measure' },
  ];

  const recentOrdersColumns: ColumnsType<SalesOrder> = [
    { title: 'Order #', dataIndex: 'id', key: 'id' },
    { title: 'Customer', dataIndex: 'customer_name', key: 'customer_name' },
    { title: 'Total', dataIndex: 'total_amount', key: 'total_amount', render: (value) => formatCurrency(value) },
    { title: 'Status', dataIndex: 'status', key: 'status' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <Typography.Title level={2} style={{ margin: 0, marginBottom: '8px' }}>
          Executive Dashboard
        </Typography.Title>
        <Typography.Text type="secondary">
          Overview of key metrics and recent activity
        </Typography.Text>
      </div>
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic
              title="Total Inventory Stock"
              value={inventoryStats.totalStock}
              suffix="units"
              valueStyle={{ color: '#1677ff' }}
            />
            <Typography.Text type="secondary">
              {inventoryStats.lowStockCount} items near reorder level
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic
              title="Sales Orders"
              value={salesStats.totalOrders}
              prefix={<ArrowUpOutlined />}
              suffix="MTD"
            />
            <Progress
              percent={salesStats.fulfillmentRate}
              size="small"
              strokeColor="#52c41a"
              format={(value) => `${value}% fulfilled`}
            />
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic
              title="Manufacturing Orders"
              value={manufacturingStats.total}
              prefix={<ThunderboltOutlined />}
            />
            <Typography.Text type="secondary">
              {manufacturingStats.inProgress} currently in production
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic title="Pending Requisitions" value={requisitionStats.pending} suffix="open" />
            <Typography.Text type="secondary">
              {requisitionStats.approved} approved in the last cycle
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="Low Stock Components"
            extra={
              <Typography.Link onClick={() => navigate('/inventory/components')}>
                View all
              </Typography.Link>
            }
          >
            <Table<Component>
              rowKey="id"
              size="small"
              pagination={false}
              columns={topComponentsColumns}
              dataSource={components.filter((component) => component.quantity <= component.reorder_level)}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card
            title="Recent Sales Orders"
            extra={
              <Typography.Link onClick={() => navigate('/sales/orders')}>
                View all
              </Typography.Link>
            }
          >
            <Table<SalesOrder>
              rowKey="id"
              size="small"
              pagination={false}
              columns={recentOrdersColumns}
              dataSource={salesOrders.slice(0, 5) || []}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Purchase Orders">
            <Table<PurchaseOrder>
              rowKey="id"
              size="small"
              pagination={false}
              columns={[
                { title: 'PO #', dataIndex: 'id', key: 'id' },
                { title: 'Status', dataIndex: 'status', key: 'status' },
                { title: 'Supplier', dataIndex: ['purchase_requisition', 'supplier_name'], key: 'supplier' },
                { title: 'Total', dataIndex: 'total_price', key: 'total_price', render: (value) => formatCurrency(value) },
              ]}
              dataSource={purchaseOrders.slice(0, 5) || []}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Manufacturing Throughput">
            <Typography.Paragraph type="secondary">
              Track the progress of manufacturing orders against targets.
            </Typography.Paragraph>
            <Progress percent={Math.min(100, manufacturingStats.inProgress * 10)} status="active" />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;


