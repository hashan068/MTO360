/**
 * Operation Route Detail Page
 * Full page for editing route and managing its operations
 */
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Button, Space, Tag, Spin } from 'antd';
import { ArrowLeftOutlined, EditOutlined } from '@ant-design/icons';
import { useOperationRoute } from '../hooks/useOperationRoutes';
import { RouteOperationsList } from '../components/RouteOperationsList';

export const OperationRouteDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const routeId = parseInt(id || '0', 10);

  const { data: route, isLoading } = useOperationRoute(routeId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" />
      </div>
    );
  }

  if (!route) {
    return (
      <div className="p-6">
        <Card>
          <div className="text-center py-8">
            <p className="text-gray-500">Operation route not found</p>
            <Button type="link" onClick={() => navigate('/manufacturing/operation-routes')}>
              Back to Routes
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-4">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/manufacturing/operation-routes')}
        >
          Back to Routes
        </Button>
      </div>

      <Card
        title={route.name}
        extra={
          <Space>
            <Tag color={route.is_active ? 'success' : 'default'}>
              {route.is_active ? 'Active' : 'Inactive'}
            </Tag>
            <Button icon={<EditOutlined />} onClick={() => { }}>
              Edit Route Info
            </Button>
          </Space>
        }
      >
        <Descriptions column={2} size="small" className="mb-6">
          <Descriptions.Item label="Route Name">{route.name}</Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color={route.is_active ? 'success' : 'default'}>
              {route.is_active ? 'Active' : 'Inactive'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Product ID">
            {route.product_id || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="BOM ID">
            {route.bom_id || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="Created">
            {new Date(route.created_at).toLocaleDateString()}
          </Descriptions.Item>
          <Descriptions.Item label="Last Updated">
            {new Date(route.updated_at).toLocaleDateString()}
          </Descriptions.Item>
        </Descriptions>

        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-4">Route Operations</h3>
          <RouteOperationsList routeId={routeId} />
        </div>
      </Card>
    </div>
  );
};

export default OperationRouteDetailPage;

