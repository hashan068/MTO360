import { useMemo } from 'react';
import { BarcodeOutlined, FileSyncOutlined, TeamOutlined } from '@ant-design/icons';
import { Card, Col, List, Progress, Row, Statistic, Table, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { componentsApi, purchaseOrdersApi, purchaseRequisitionsApi, suppliersApi } from '@/features/inventory/api';
import type { Component, PurchaseOrder, PurchaseRequisition, Supplier } from '@/features/inventory/types';
import { useAuthStore } from '@/features/auth/store/authStore';

const InventoryDashboardPage = () => {
  const isAuthenticated = useAuthStore((state) => Boolean(state.accessToken));
  const navigate = useNavigate();

  const { data: components = [], isLoading: isLoadingComponents } = useQuery<Component[]>({
    queryKey: ['inventory', 'components', 'dashboard'],
    queryFn: () => componentsApi.list({ limit: 50 }),
    enabled: isAuthenticated,
  });

  const { data: requisitions = [], isLoading: isLoadingRequisitions } = useQuery<PurchaseRequisition[]>({
    queryKey: ['inventory', 'requisitions', 'dashboard'],
    queryFn: () => purchaseRequisitionsApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: orders = [] } = useQuery<PurchaseOrder[]>({
    queryKey: ['inventory', 'orders', 'dashboard'],
    queryFn: () => purchaseOrdersApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: suppliers = [] } = useQuery<Supplier[]>({
    queryKey: ['inventory', 'suppliers', 'dashboard'],
    queryFn: () => suppliersApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const lowStock = useMemo(
    () => components.filter((component) => component.quantity <= component.reorder_level),
    [components]
  );

  const activeSuppliers = suppliers.filter((supplier) => supplier.is_active);

  const columns: ColumnsType<PurchaseRequisition> = [
    { title: 'Req #', dataIndex: 'id', key: 'id', width: 90 },
    { title: 'Component', dataIndex: 'component_name', key: 'component_name' },
    { title: 'Quantity', dataIndex: 'quantity', key: 'quantity' },
    { title: 'Priority', dataIndex: 'priority', key: 'priority' },
    { title: 'Status', dataIndex: 'status', key: 'status' },
  ];

  return (
    <div className="space-y-6">
      <Typography.Title level={3}>Inventory Dashboard</Typography.Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12} lg={6}>
          <Card loading={isLoadingComponents}>
            <Statistic
              title="Tracked Components"
              value={components.length}
              prefix={<BarcodeOutlined />}
              suffix="SKU"
            />
            <Typography.Text type="secondary">
              {lowStock.length} require replenishment
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card loading={isLoadingRequisitions}>
            <Statistic
              title="Pending Requisitions"
              value={requisitions.filter((req) => req.status === 'PENDING').length}
              prefix={<FileSyncOutlined />}
            />
            <Typography.Text type="secondary">
              {requisitions.filter((req) => req.status === 'APPROVED').length} approved this week
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic
              title="Active Suppliers"
              value={activeSuppliers.length}
              prefix={<TeamOutlined />}
            />
            <Typography.Text type="secondary">
              {suppliers.length - activeSuppliers.length} inactive suppliers
            </Typography.Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Typography.Text type="secondary">Order Fulfillment Progress</Typography.Text>
            <Progress
              percent={Math.min(
                100,
                Math.round(
                  (orders.filter((order) => order.status === 'RECEIVED').length / (orders.length || 1)) * 100
                )
              )}
              status="active"
              style={{ marginTop: 12 }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="Low Stock Components"
            extra={
              <Typography.Link onClick={() => navigate('/inventory/components')}>
                Manage components
              </Typography.Link>
            }
          >
            <List
              dataSource={lowStock.slice(0, 5) || []}
              locale={{ emptyText: 'All components are above reorder levels.' }}
              renderItem={(component) => (
                <List.Item actions={[<span key="quantity">{component.quantity} {component.unit_of_measure}</span>]}> 
                  <List.Item.Meta
                    title={component.name}
                    description={`Reorder level ${component.reorder_level} • Supplier ${component.supplier_id ?? '—'}`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card
            title="Requisition Pipeline"
            extra={
              <Typography.Link onClick={() => navigate('/inventory/purchase-requisitions')}>
                View requisitions
              </Typography.Link>
            }
          >
            <Table<PurchaseRequisition>
              rowKey="id"
              columns={columns}
              dataSource={requisitions.slice(0, 6) || []}
              size="small"
              pagination={false}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default InventoryDashboardPage;


