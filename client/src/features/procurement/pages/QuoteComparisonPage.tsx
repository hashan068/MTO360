/**
 * Quote Comparison Page - Phase 2: RFQ & Competitive Bidding
 */
import { TrophyOutlined, CheckCircleOutlined, DollarOutlined, ClockCircleOutlined } from '@ant-design/icons';
import {
  Card,
  Table,
  Typography,
  Button,
  Space,
  Tag,
  Alert,
  Modal,
  Input,
  message
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { rfqApi } from '../api/procurementApi';
import type { QuoteComparison, QuoteComparisonItem } from '../types';
import { formatCurrency } from '@/shared/utils/format';

const { TextArea } = Input;

const QuoteComparisonPage = () => {
  const { rfqId } = useParams<{ rfqId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [sortBy, setSortBy] = useState<'price' | 'lead_time' | 'score'>('price');
  const [awardModalVisible, setAwardModalVisible] = useState(false);
  const [selectedQuoteId, setSelectedQuoteId] = useState<number | null>(null);
  const [justification, setJustification] = useState('');

  const {
    data: comparison,
    isLoading,
  } = useQuery<QuoteComparison>({
    queryKey: ['procurement', 'rfqs', rfqId, 'compare', sortBy],
    queryFn: () => rfqApi.compareQuotes(parseInt(rfqId!), sortBy),
    enabled: !!rfqId,
  });

  const awardMutation = useMutation({
    mutationFn: ({ quoteId, justification }: { quoteId: number; justification: string }) =>
      rfqApi.awardRFQ(parseInt(rfqId!), quoteId, justification),
    onSuccess: () => {
      message.success('RFQ awarded successfully! Purchase Order created.');
      queryClient.invalidateQueries({ queryKey: ['procurement', 'rfqs'] });
      navigate(`/procurement/rfqs/${rfqId}`);
    },
    onError: () => {
      message.error('Failed to award RFQ');
    },
  });

  const columns: ColumnsType<QuoteComparisonItem> = [
    {
      title: 'Supplier',
      dataIndex: 'supplier_name',
      key: 'supplier_name',
      render: (name, record) => (
        <Space direction="vertical" size={0}>
          <span style={{ fontWeight: 500 }}>{name}</span>
          {record.supplier_score && (
            <Typography.Text type="secondary" style={{ fontSize: 12 }}>
              Score: {record.supplier_score.toFixed(1)}%
            </Typography.Text>
          )}
        </Space>
      ),
    },
    {
      title: 'Unit Price',
      dataIndex: 'unit_price',
      key: 'unit_price',
      width: 140,
      render: (price, record) => (
        <Space>
          {formatCurrency(price)}
          {record.is_best_price && <Tag color="success" icon={<TrophyOutlined />}>Best</Tag>}
        </Space>
      ),
      sorter: (a, b) => a.unit_price - b.unit_price,
    },
    {
      title: 'Total Price',
      dataIndex: 'total_price',
      key: 'total_price',
      width: 150,
      render: (price) => <span style={{ fontWeight: 500 }}>{formatCurrency(price)}</span>,
      sorter: (a, b) => a.total_price - b.total_price,
    },
    {
      title: 'Lead Time',
      dataIndex: 'lead_time_days',
      key: 'lead_time_days',
      width: 140,
      render: (days, record) => (
        <Space>
          <ClockCircleOutlined /> {days} days
          {record.is_best_lead_time && <Tag color="success" icon={<TrophyOutlined />}>Fastest</Tag>}
        </Space>
      ),
      sorter: (a, b) => a.lead_time_days - b.lead_time_days,
    },
    {
      title: 'Delivery Date',
      dataIndex: 'delivery_date',
      key: 'delivery_date',
      width: 140,
      render: (date) => dayjs(date).format('MMM D, YYYY'),
    },
    {
      title: 'MOQ',
      dataIndex: 'minimum_order_quantity',
      key: 'minimum_order_quantity',
      width: 100,
      render: (qty) => qty.toLocaleString(),
    },
    {
      title: 'Valid Until',
      dataIndex: 'quote_valid_until',
      key: 'quote_valid_until',
      width: 120,
      render: (date) => dayjs(date).format('MMM D, YYYY'),
    },
    {
      title: 'Action',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button
          type="primary"
          size="small"
          icon={<CheckCircleOutlined />}
          onClick={(e) => {
            e.stopPropagation();
            setSelectedQuoteId(record.quote_id);
            setAwardModalVisible(true);
          }}
        >
          Award
        </Button>
      ),
    },
  ];

  const handleAward = async () => {
    if (!selectedQuoteId || !justification.trim()) {
      message.error('Please provide justification for the award');
      return;
    }

    await awardMutation.mutateAsync({
      quoteId: selectedQuoteId,
      justification,
    });

    setAwardModalVisible(false);
    setJustification('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            Quote Comparison - {comparison?.rfq.rfq_number}
          </Typography.Title>
          <Typography.Text type="secondary">
            Compare supplier quotes and award RFQ.
          </Typography.Text>
        </div>
        <Space>
          <Button onClick={() => setSortBy('price')} type={sortBy === 'price' ? 'primary' : 'default'}>
            <DollarOutlined /> Sort by Price
          </Button>
          <Button onClick={() => setSortBy('lead_time')} type={sortBy === 'lead_time' ? 'primary' : 'default'}>
            <ClockCircleOutlined /> Sort by Lead Time
          </Button>
          <Button onClick={() => setSortBy('score')} type={sortBy === 'score' ? 'primary' : 'default'}>
            <TrophyOutlined /> Sort by Score
          </Button>
        </Space>
      </div>

      {/* Recommendation */}
      {comparison?.recommendation && (
        <Alert
          message="Recommendation"
          description={comparison.recommendation}
          type="info"
          showIcon
          icon={<TrophyOutlined />}
        />
      )}

      {/* RFQ Details */}
      {comparison?.rfq && (
        <Card title="RFQ Details" size="small">
          <Space direction="vertical" style={{ width: '100%' }}>
            <div><strong>Component:</strong> {comparison.rfq.component_name}</div>
            <div><strong>Quantity:</strong> {comparison.rfq.quantity.toLocaleString()} units</div>
            <div><strong>Required By:</strong> {dayjs(comparison.rfq.required_by_date).format('MMMM D, YYYY')}</div>
            {comparison.rfq.specifications && (
              <div><strong>Specifications:</strong> {comparison.rfq.specifications}</div>
            )}
          </Space>
        </Card>
      )}

      {/* Quotes Comparison Table */}
      <Card>
        <Table<QuoteComparisonItem>
          rowKey="quote_id"
          columns={columns}
          dataSource={comparison?.quotes || []}
          loading={isLoading}
          pagination={false}
        />
      </Card>

      {/* Award Modal */}
      <Modal
        title="Award RFQ"
        open={awardModalVisible}
        onOk={handleAward}
        onCancel={() => {
          setAwardModalVisible(false);
          setJustification('');
        }}
        confirmLoading={awardMutation.isPending}
        okText="Confirm Award"
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Alert
            message="Award Confirmation"
            description="Awarding this RFQ will create a Purchase Order and reject other quotes. This action cannot be undone."
            type="warning"
            showIcon
          />
          <div>
            <Typography.Text strong>Award Justification (Required):</Typography.Text>
            <TextArea
              rows={4}
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              placeholder="Explain why this supplier was selected (e.g., best price, fastest delivery, proven track record...)"
              style={{ marginTop: 8 }}
            />
          </div>
        </Space>
      </Modal>
    </div>
  );
};

export default QuoteComparisonPage;
