import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  App as AntdApp,
  Button,
  Card,
  Descriptions,
  Space,
  Typography,
  Spin,
  Alert,
  Modal,
  Table,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { ArrowLeftOutlined, EditOutlined, CheckOutlined } from '@ant-design/icons';
import { rfqsApi, productsApi } from '@/features/sales/api';
import type { RFQ, RFQUpdatePayload, Product, QuotationSummary } from '@/features/sales/types';
import { StatusBadge, LineItemsTable, RfqForm, DocumentLink, DocumentBreadcrumb } from '@/features/sales/components';
import { formatDate } from '@/shared/utils/format';

const RfqDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = AntdApp.useApp();
  const [isEditing, setIsEditing] = useState(false);
  const [showConvertModal, setShowConvertModal] = useState(false);

  const rfqId = parseInt(id || '0', 10);

  const { data: rfq, isLoading, error } = useQuery<RFQ>({
    queryKey: ['sales', 'rfqs', rfqId],
    queryFn: () => rfqsApi.retrieve(rfqId),
    enabled: rfqId > 0,
  });

  const { data: products = [] } = useQuery<Product[]>({
    queryKey: ['sales', 'products', 'list'],
    queryFn: () => productsApi.list({ limit: 500 }),
  });

  const { data: quotations = [] } = useQuery<QuotationSummary[]>({
    queryKey: ['sales', 'rfqs', rfqId, 'quotations'],
    queryFn: () => rfqsApi.getQuotations(rfqId),
    enabled: rfqId > 0,
  });

  const updateMutation = useMutation({
    mutationFn: (values: RFQUpdatePayload) => rfqsApi.update(rfqId, values),
    onSuccess: () => {
      message.success('RFQ updated successfully');
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ['sales', 'rfqs', rfqId] });
      queryClient.invalidateQueries({ queryKey: ['sales', 'rfqs', 'list'] });
    },
    onError: () => {
      message.error('Failed to update RFQ');
    },
  });

  const handleUpdate = async (values: RFQUpdatePayload) => {
    await updateMutation.mutateAsync(values);
  };

  const handleCreateQuotation = () => {
    setShowConvertModal(true);
  };

  const handleConvertConfirm = () => {
    // Navigate to quotation creation page with RFQ context
    navigate(`/sales/quotations/new?rfq_id=${rfqId}`);
  };

  const canEdit = rfq?.status === 'draft';
  const canConvert = rfq?.status === 'sent';

  const quotationColumns: ColumnsType<QuotationSummary> = [
    {
      title: 'Quotation #',
      dataIndex: 'id',
      key: 'id',
      width: 120,
      render: (id: number) => <DocumentLink type="quotation" id={id} />,
    },
    {
      title: 'Customer',
      dataIndex: 'customer_name',
      key: 'customer_name',
      render: (name: string | null, record: QuotationSummary) => name || `Customer #${record.customer_id}`,
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      width: 140,
      render: (date: string) => formatDate(date),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 140,
      render: (status) => <StatusBadge status={status} />,
    },
  ];

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error || !rfq) {
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
      <DocumentBreadcrumb
        rfq={rfq}
        currentPage="rfq"
      />
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/sales/rfqs')}>
            Back to RFQs
          </Button>
          <Typography.Title level={3} style={{ margin: 0 }}>
            RFQ #{rfq.id}
          </Typography.Title>
        </Space>
        <Space>
          {canConvert && (
            <Button type="primary" icon={<CheckOutlined />} onClick={handleCreateQuotation}>
              Create Quotation
            </Button>
          )}
          {!isEditing && (
            <Button
              icon={<EditOutlined />}
              onClick={() => setIsEditing(true)}
              disabled={!canEdit}
              title={!canEdit ? `Cannot edit RFQ with status "${rfq.status}"` : undefined}
            >
              Edit RFQ
            </Button>
          )}
        </Space>
      </div>

      {!canEdit && isEditing && (
        <Alert
          message="Editing Restricted"
          description={`This RFQ cannot be edited because its status is "${rfq.status}". Only draft RFQs can be edited.`}
          type="warning"
          showIcon
          closable
          onClose={() => setIsEditing(false)}
        />
      )}

      {isEditing && canEdit ? (
        <Card title="Edit RFQ">
          <RfqForm
            initialValues={rfq}
            products={products}
            onSubmit={handleUpdate}
            onCancel={() => setIsEditing(false)}
            isLoading={updateMutation.isPending}
            mode="edit"
          />
        </Card>
      ) : (
        <>
          <Card title="RFQ Information">
            <Descriptions column={2} variant="outlined">
              <Descriptions.Item label="RFQ #">{rfq.id}</Descriptions.Item>
              <Descriptions.Item label="Status">
                <StatusBadge status={rfq.status} />
              </Descriptions.Item>
              <Descriptions.Item label="Creator">
                {rfq.creator_name || `User #${rfq.creator_id}`}
              </Descriptions.Item>
              <Descriptions.Item label="Due Date">
                {rfq.due_date ? formatDate(rfq.due_date) : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Created Date">
                {formatDate(rfq.created_at)}
              </Descriptions.Item>
              <Descriptions.Item label="Last Updated">
                {rfq.updated_at ? formatDate(rfq.updated_at) : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="Description" span={2}>
                {rfq.description || '—'}
              </Descriptions.Item>
            </Descriptions>
          </Card>

          <Card title="Line Items">
            <LineItemsTable
              items={rfq.items}
              products={products}
              editable={false}
              showTotal={false}
            />
          </Card>

          {quotations.length > 0 && (
            <Card title="Linked Quotations">
              <Table<QuotationSummary>
                rowKey="id"
                columns={quotationColumns}
                dataSource={quotations || []}
                pagination={false}
                size="small"
              />
            </Card>
          )}
        </>
      )}

      <Modal
        title="Create Quotation from RFQ"
        open={showConvertModal}
        onOk={handleConvertConfirm}
        onCancel={() => setShowConvertModal(false)}
        okText="Continue"
      >
        <p>You will be redirected to create a new quotation with the line items from this RFQ pre-populated.</p>
        <p>You can modify the quotation details before saving.</p>
      </Modal>
    </div>
  );
};

export default RfqDetailPage;


