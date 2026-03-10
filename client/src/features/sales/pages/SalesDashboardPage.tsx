import { useMemo } from 'react';
import { RiseOutlined, ShoppingOutlined, UserSwitchOutlined } from '@ant-design/icons';
import { Card, Col, List, Progress, Row, Statistic, Table, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { customersApi, productsApi, quotationsApi, salesOrdersApi } from '@/features/sales/api';
import type { Customer, Product, Quotation, SalesOrder } from '@/features/sales/types';
import { useAuthStore } from '@/features/auth/store/authStore';
import { formatCurrency } from '@/shared/utils/format';

const SalesDashboardPage = () => {
  const isAuthenticated = useAuthStore((state) => Boolean(state.accessToken));
  const navigate = useNavigate();

  const { data: customers = [] } = useQuery<Customer[]>({
    queryKey: ['sales', 'customers', 'dashboard'],
    queryFn: () => customersApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['sales', 'products', 'dashboard'],
    queryFn: () => productsApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: quotations = [] } = useQuery<Quotation[]>({
    queryKey: ['sales', 'quotations', 'dashboard'],
    queryFn: () => quotationsApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const { data: salesOrders = [] } = useQuery<SalesOrder[]>({
    queryKey: ['sales', 'orders', 'dashboard'],
    queryFn: () => salesOrdersApi.list({ limit: 20 }),
    enabled: isAuthenticated,
  });

  const pipelineStats = useMemo(() => {
    const totalQuotations = quotations.length;
    const approved = quotations.filter((quotation) => quotation.status === 'accepted').length;
    const conversionRate = totalQuotations === 0 ? 0 : Math.round((approved / totalQuotations) * 100);
    return { totalQuotations, approved, conversionRate };
  }, [quotations]);

  const recentOrdersColumns: ColumnsType<SalesOrder> = [
    { title: 'Order', dataIndex: 'id', key: 'id', width: 90 },
    { title: 'Customer', dataIndex: 'customer_name', key: 'customer_name' },
    { title: 'Total', dataIndex: 'total_amount', key: 'total_amount' },
    { title: 'Status', dataIndex: 'status', key: 'status' },
  ];

  return (
    <div className="space-y-6">
      <Typography.Title level={3}>Sales Dashboard</Typography.Title>
      <Row gutter={[16, 16]}>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic title="Active Customers" value={customers.length} prefix={<UserSwitchOutlined />} />
            <Typography.Text type="secondary">{customers.filter((c) => c.is_active).length} active accounts</Typography.Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic title="Product Catalog" value={products.length} prefix={<ShoppingOutlined />} />
            <Typography.Text type="secondary">{products.filter((p) => p.price).length} priced variations</Typography.Text>
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic title="Quotations" value={pipelineStats.totalQuotations} prefix={<RiseOutlined />} />
            <Progress percent={pipelineStats.conversionRate} size="small" status="active" />
          </Card>
        </Col>
        <Col xs={24} md={12} lg={6}>
          <Card>
            <Statistic title="Sales Orders" value={salesOrders.length} suffix="open" />
            <Typography.Text type="secondary">
              {salesOrders.filter((order) => order.status === 'delivered').length} fulfilled this month
            </Typography.Text>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="Recent Sales Orders"
            extra={<Typography.Link onClick={() => navigate('/sales/orders')}>View orders</Typography.Link>}
          >
            <Table<SalesOrder>
              rowKey="id"
              columns={recentOrdersColumns}
              dataSource={salesOrders.slice(0, 6) || []}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card
            title="Top Products"
            extra={<Typography.Link onClick={() => navigate('/sales/products')}>Manage products</Typography.Link>}
          >
            <List
              dataSource={products.slice(0, 5) || []}
              renderItem={(product) => (
                <List.Item actions={[<span key="price">{formatCurrency(product.price)}</span>]}>
                  <List.Item.Meta
                    title={product.product_name ?? product.description}
                    description={`Power rating ${product.power_rating}W • Warranty ${product.warranty_years} years`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="Quotation Pipeline"
            extra={<Typography.Link onClick={() => navigate('/sales/quotations')}>Quotation board</Typography.Link>}
          >
            <List
              dataSource={quotations.slice(0, 5) || []}
              renderItem={(quotation) => (
                <List.Item actions={[<span key="amount">{formatCurrency(quotation.total_amount)}</span>]}>
                  <List.Item.Meta
                    title={`Quotation #${quotation.id}`}
                    description={`${quotation.customer_name ?? 'Customer'} • Status ${quotation.status}`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Customer Activity" extra={<Typography.Link onClick={() => navigate('/sales/customers')}>Customer list</Typography.Link>}>
            <List
              dataSource={customers.slice(0, 5) || []}
              renderItem={(customer) => (
                <List.Item actions={[<span key="city">{customer.city}</span>]}>
                  <List.Item.Meta
                    title={customer.name}
                    description={`${customer.email} • ${customer.phone}`}
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

export default SalesDashboardPage;


