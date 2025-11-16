import { ArrowLeftOutlined } from '@ant-design/icons';
import { App as AntdApp, Button, Card, Form, Space, Spin, Typography, Alert } from 'antd';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { customersApi, productsApi, quotationsApi, rfqsApi } from '@/features/sales/api';
import type { Customer, Product, RFQ } from '@/features/sales/types';
import { QuotationForm, QuotationFormValues } from '@/features/sales/components/QuotationForm';

const QuotationCreatePage = () => {
  const navigate = useNavigate();
  const { message } = AntdApp.useApp();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const [form] = Form.useForm<QuotationFormValues>();

  const rfqId = searchParams.get('rfq_id');
  const isRfqConversion = !!rfqId;

  // Fetch RFQ if converting from RFQ
  const { data: sourceRfq, isLoading: isLoadingRfq } = useQuery<RFQ>({
    queryKey: ['sales', 'rfqs', parseInt(rfqId || '0', 10)],
    queryFn: () => rfqsApi.retrieve(parseInt(rfqId || '0', 10)),
    enabled: isRfqConversion,
  });

  // Fetch customers
  const { data: customers = [] } = useQuery<Customer[]>({
    queryKey: ['sales', 'customers', 'options'],
    queryFn: () => customersApi.list({ limit: 200 }),
  });

  // Fetch products
  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['sales', 'products', 'options'],
    queryFn: () => productsApi.list({ limit: 200 }),
  });

  // Create quotation mutation (direct creation)
  const createMutation = useMutation({
    mutationFn: (values: QuotationFormValues) => {
      return quotationsApi.create({
        customer_id: values.customer_id,
        date: values.date.format('YYYY-MM-DD'),
        expiration_date: values.expiration_date.format('YYYY-MM-DD'),
        invoicing_and_shipping_address: values.invoicing_and_shipping_address,
        quotation_items: values.quotation_items,
      });
    },
    onSuccess: (quotation) => {
      message.success('Quotation created successfully');
      queryClient.invalidateQueries({ queryKey: ['sales', 'quotations'] });
      navigate(`/sales/quotations/${quotation.id}`);
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || 'Failed to create quotation');
    },
  });

  // Convert RFQ to quotation mutation
  const convertMutation = useMutation({
    mutationFn: (values: QuotationFormValues) => {
      if (!rfqId) throw new Error('RFQ ID is required');
      return rfqsApi.convertToQuotation(parseInt(rfqId, 10), {
        customer_id: values.customer_id,
        date: values.date.format('YYYY-MM-DD'),
        expiration_date: values.expiration_date.format('YYYY-MM-DD'),
        invoicing_and_shipping_address: values.invoicing_and_shipping_address,
      });
    },
    onSuccess: (quotation) => {
      message.success('Quotation created from RFQ successfully');
      queryClient.invalidateQueries({ queryKey: ['sales', 'quotations'] });
      queryClient.invalidateQueries({ queryKey: ['sales', 'rfqs'] });
      navigate(`/sales/quotations/${quotation.id}`);
    },
    onError: (error: any) => {
      message.error(error?.response?.data?.detail || 'Failed to convert RFQ to quotation');
    },
  });

  const handleSubmit = (values: QuotationFormValues) => {
    if (isRfqConversion) {
      convertMutation.mutate(values);
    } else {
      createMutation.mutate(values);
    }
  };

  const isLoading = isRfqConversion ? isLoadingRfq : false;
  const isMutating = createMutation.isPending || convertMutation.isPending;

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '48px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (isRfqConversion && !sourceRfq) {
    return (
      <Alert
        message="Error"
        description="Failed to load RFQ details. The RFQ may not exist."
        type="error"
        showIcon
      />
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(isRfqConversion ? `/sales/rfqs/${rfqId}` : '/sales/quotations')}
          >
            Back
          </Button>
          <Typography.Title level={3} style={{ margin: 0 }}>
            {isRfqConversion ? `Create Quotation from RFQ #${rfqId}` : 'Create Quotation'}
          </Typography.Title>
        </Space>
      </div>

      <Card>
        <QuotationForm
          form={form}
          customers={customers}
          products={products}
          onSubmit={handleSubmit}
          loading={isMutating}
          mode={isRfqConversion ? 'rfq-conversion' : 'create'}
          sourceRfq={sourceRfq || null}
        />
      </Card>
    </div>
  );
};

export default QuotationCreatePage;
