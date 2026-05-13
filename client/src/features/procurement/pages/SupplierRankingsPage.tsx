/**
 * Supplier Rankings Page - Phase 1: Supplier Performance
 */
import { TrophyOutlined, ReloadOutlined } from '@ant-design/icons';
import { Card, Table, Typography, Button, Progress, Statistic, Row, Col } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supplierPerformanceApi } from '../api/procurementApi';
import type { SupplierRanking } from '../types';
import { formatCurrency } from '@/shared/utils/format';

const SupplierRankingsPage = () => {
  const navigate = useNavigate();
  const [limit] = useState(20);

  const {
    data: rankings = [],
    isLoading,
    refetch,
  } = useQuery<SupplierRanking[]>({
    queryKey: ['procurement', 'supplier-rankings', limit],
    queryFn: () => supplierPerformanceApi.getSupplierRankings(limit),
  });

  const columns: ColumnsType<SupplierRanking> = [
    {
      title: 'Rank',
      dataIndex: 'rank',
      key: 'rank',
      width: 80,
      render: (rank: number) => {
        if (rank === 1) return <TrophyOutlined style={{ color: '#FFD700', fontSize: 20 }} />;
        if (rank === 2) return <TrophyOutlined style={{ color: '#C0C0C0', fontSize: 18 }} />;
        if (rank === 3) return <TrophyOutlined style={{ color: '#CD7F32', fontSize: 16 }} />;
        return `#${rank}`;
      },
    },
    {
      title: 'Supplier',
      dataIndex: 'supplier_name',
      key: 'supplier_name',
      ellipsis: true,
    },
    {
      title: 'Overall Score',
      dataIndex: 'overall_score',
      key: 'overall_score',
      width: 180,
      render: (score: number) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Progress
            percent={score}
            size="small"
            strokeColor={score >= 90 ? '#52c41a' : score >= 75 ? '#faad14' : '#ff4d4f'}
            style={{ width: 100 }}
          />
          <span style={{ fontWeight: 500 }}>{score.toFixed(1)}%</span>
        </div>
      ),
      sorter: (a, b) => a.overall_score - b.overall_score,
    },
    {
      title: 'On-Time Delivery',
      dataIndex: 'on_time_delivery_rate',
      key: 'on_time_delivery_rate',
      width: 140,
      render: (rate: number) => `${rate.toFixed(1)}%`,
      sorter: (a, b) => a.on_time_delivery_rate - b.on_time_delivery_rate,
    },
    {
      title: 'Quality Rating',
      dataIndex: 'quality_rating',
      key: 'quality_rating',
      width: 120,
      render: (rating: number) => `${rating.toFixed(1)}%`,
      sorter: (a, b) => a.quality_rating - b.quality_rating,
    },
    {
      title: 'Total Spend',
      dataIndex: 'total_spend',
      key: 'total_spend',
      width: 140,
      render: (spend: number) => formatCurrency(spend),
      sorter: (a, b) => a.total_spend - b.total_spend,
    },
  ];

  const handleRowClick = (record: SupplierRanking) => {
    navigate(`/procurement/suppliers/${record.supplier_id}/performance`);
  };

  // Calculate summary stats
  const avgScore = rankings.length > 0
    ? rankings.reduce((sum, r) => sum + r.overall_score, 0) / rankings.length
    : 0;

  const topPerformers = rankings.filter(r => r.overall_score >= 90).length;
  const totalSpend = rankings.reduce((sum, r) => sum + r.total_spend, 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <Typography.Title level={3} style={{ margin: 0, marginBottom: '8px' }}>
            <TrophyOutlined /> Supplier Rankings
          </Typography.Title>
          <Typography.Text type="secondary">
            Supplier performance rankings based on delivery, quality, and price competitiveness.
          </Typography.Text>
        </div>
        <Button
          icon={<ReloadOutlined />}
          onClick={() => refetch()}
          loading={isLoading}
        >
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Average Score"
              value={avgScore.toFixed(1)}
              suffix="%"
              valueStyle={{ color: avgScore >= 80 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Top Performers (≥90%)"
              value={topPerformers}
              suffix={`/ ${rankings.length}`}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Suppliers"
              value={rankings.length}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Annual Spend"
              value={totalSpend}
              prefix="$"
              precision={0}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <Table<SupplierRanking>
          rowKey={(record) => `${record.supplier_id}-${record.period}`}
          columns={columns}
          dataSource={rankings || []}
          loading={isLoading}
          pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `Total ${total} suppliers` }}
          onRow={(record) => ({
            onClick: () => handleRowClick(record),
            style: { cursor: 'pointer' },
          })}
        />
      </Card>
    </div>
  );
};

export default SupplierRankingsPage;
