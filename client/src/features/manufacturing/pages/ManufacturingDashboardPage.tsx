import { useMemo } from 'react';
import { AlertOutlined, BuildOutlined, DeploymentUnitOutlined } from '@ant-design/icons';
import { Card, Col, List, Progress, Row, Statistic, Table, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { billOfMaterialsApi, manufacturingOrdersApi, materialRequisitionsApi } from '@/features/manufacturing/api';
import type {
  BillOfMaterial,
  ManufacturingOrder,
  MaterialRequisition,
} from '@/features/manufacturing/types';
import { useAuthStore } from '@/features/auth/store/authStore';

const ManufacturingDashboardPage = () => {
  const isAuthenticated = useAuthStore((state) => Boolean(state.accessToken));
  const navigate = useNavigate();

  const { data: manufacturingOrders = [] } = useQuery<ManufacturingOrder[]>({
    queryKey: ['manufacturing', 'orders', 'dashboard'],
    queryFn: () => manufacturingOrdersApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: materialRequisitions = [] } = useQuery<MaterialRequisition[]>({
    queryKey: ['manufacturing', 'material-requisitions', 'dashboard'],
    queryFn: () => materialRequisitionsApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: boms = [] } = useQuery<BillOfMaterial[]>({
    queryKey: ['manufacturing', 'boms', 'dashboard'],
    queryFn: () => billOfMaterialsApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const statusBreakdown = useMemo(() => {
    const total = manufacturingOrders.length || 1;
    return {
      planned: manufacturingOrders.filter((order) => order.status === 'PLANNED').length,
      inProgress: manufacturingOrders.filter((order) => order.status === 'IN_PROGRESS').length,
      completed: manufacturingOrders.filter((order) => order.status === 'COMPLETED').length,
      progress: Math.round(
        (manufacturingOrders.filter((order) => order.status === 'IN_PROGRESS').length / total) * 100
      ),
    };
  }, [manufacturingOrders]);

  const requisitionsColumns: ColumnsType<MaterialRequisition> = [
    { title: 'Req #', dataIndex: 'id', key: 'id', width: 100 },
    { title: 'Order', dataIndex: 'manufacturing_order_id', key: 'manufacturing_order_id' },
    { title: 'Status', dataIndex: 'status', key: 'status' },
    { title: 'Created', dataIndex: 'created_at', key: 'created_at' },
  ];

  return (
    <div className="space-y-6">
      <Typography.Title level={3}>Manufacturing Dashboard</Typography.Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic title="Open Orders" value={manufacturingOrders.length} prefix={<BuildOutlined />} />
            <Typography.Text type="secondary">
              {statusBreakdown.inProgress} currently in production
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic title="BOM Library" value={boms.length} prefix={<DeploymentUnitOutlined />} />
            <Typography.Text type="secondary">Supporting product assemblies</Typography.Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic title="Material Reqs" value={materialRequisitions.length} prefix={<AlertOutlined />} />
            <Typography.Text type="secondary">
              {materialRequisitions.filter((req) => req.status === 'PENDING').length} pending allocation
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Typography.Text type="secondary">Work in Progress</Typography.Text>
            <Progress percent={statusBreakdown.progress} status="active" style={{ marginTop: 12 }} />
            <Typography.Text type="secondary">
              Planned {statusBreakdown.planned} • Completed {statusBreakdown.completed}
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="Production Orders"
            extra={<Typography.Link onClick={() => navigate('/manufacturing/orders')}>View all</Typography.Link>}
          >
            <List
              dataSource={manufacturingOrders.slice(0, 6)}
              renderItem={(order) => (
                <List.Item actions={[<span key="qty">Qty {order.quantity}</span>]}> 
                  <List.Item.Meta
                    title={`Order #${order.id}`}
                    description={`${order.product_name ?? 'Product'} • Status ${order.status}`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card
            title="Material Requisition Status"
            extra={<Typography.Link onClick={() => navigate('/manufacturing/material-requisitions')}>Manage</Typography.Link>}
          >
            <Table<MaterialRequisition>
              rowKey="id"
              columns={requisitionsColumns}
              dataSource={materialRequisitions.slice(0, 6)}
              size="small"
              pagination={false}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24}>
          <Card
            title="Key Bill of Materials"
            extra={<Typography.Link onClick={() => navigate('/manufacturing/boms')}>BOM catalog</Typography.Link>}
          >
            <List
              dataSource={boms.slice(0, 6)}
              renderItem={(bom) => (
                <List.Item actions={[<span key="items">{bom.bom_items.length} items</span>]}> 
                  <List.Item.Meta
                    title={bom.name}
                    description={`Product ${bom.product_name ?? 'N/A'} • Updated ${bom.updated_at?.slice(0, 10) ?? '—'}`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ManufacturingDashboardPage;
