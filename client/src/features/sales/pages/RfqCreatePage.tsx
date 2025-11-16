import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { App as AntdApp, Button, Card, Space, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { rfqsApi, productsApi } from '@/features/sales/api';
import type { RFQCreatePayload, Product } from '@/features/sales/types';
import { RfqForm } from '@/features/sales/components';

const RfqCreatePage = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['sales', 'products', 'list'],
    queryFn: () => productsApi.list({ limit: 500 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: RFQCreatePayload) => rfqsApi.create(values),
    onSuccess: (data) => {
      message.success('RFQ created successfully');
      queryClient.invalidateQueries({ queryKey: ['sales', 'rfqs', 'list'] });
      navigate(`/sales/rfqs/${data.id}`);
    },
    onError: () => {
      message.error('Failed to create RFQ');
    },
  });

  const handleCreate = async (values: RFQCreatePayload) => {
    await createMutation.mutateAsync({ ...values, status: 'draft' });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/sales/rfqs')}>
            Back to RFQs
          </Button>
          <Typography.Title level={3} style={{ margin: 0 }}>
            Create New RFQ
          </Typography.Title>
        </Space>
      </div>

      <Card>
        <RfqForm
          products={products}
          onSubmit={handleCreate}
          onCancel={() => navigate('/sales/rfqs')}
          isLoading={createMutation.isPending}
          mode="create"
        />
      </Card>
    </div>
  );
};

export default RfqCreatePage;
