import { useState } from 'react';
import { Row, Col, Typography, Button, Card, Statistic } from 'antd';
import { PlusOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useMyInspections } from '../hooks/useInspections';
import { InspectionQueueCard } from '../components/InspectionQueueCard';
import { InspectionHistoryList } from '../components/InspectionHistoryList';
import { QuickInspectionModal } from '../components/QuickInspectionModal';

const InspectorDashboardPage = () => {
  const { data: myInspections, isLoading } = useMyInspections();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedInspectionId, setSelectedInspectionId] = useState<number>();

  // Mock pending data for now (would come from API)
  const pendingInspections = [
    { id: 1, mo_id: 101, op_sequence: 10, inspection_point_name: 'Visual Check' },
    { id: 2, mo_id: 102, op_sequence: 20, inspection_point_name: 'Dimensional Check' },
  ];

  const handleInspect = (id?: number) => {
    setSelectedInspectionId(id);
    setIsModalVisible(true);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Typography.Title level={2} style={{ margin: 0 }}>
            Inspector Dashboard
          </Typography.Title>
          <Typography.Text type="secondary">
            My assignments and inspection queue
          </Typography.Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          size="large"
          onClick={() => handleInspect()}
        >
          Quick Inspection
        </Button>
      </div>

      {/* Stats Row */}
      <Row gutter={16}>
        <Col span={12}>
          <Card>
            <Statistic
              title="Completed Today"
              value={myInspections?.length || 0}
              prefix={<CheckCircleOutlined className="text-green-500" />}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card>
            <Statistic
              title="Pending Queue"
              value={pendingInspections.length}
              prefix={<ClockCircleOutlined className="text-orange-500" />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={24}>
        <Col xs={24} lg={16}>
          <InspectionQueueCard
            pendingInspections={pendingInspections}
            onInspect={handleInspect}
          />
        </Col>
        <Col xs={24} lg={8}>
          <InspectionHistoryList
            inspections={myInspections || []}
            loading={isLoading}
          />
        </Col>
      </Row>

      <QuickInspectionModal
        visible={isModalVisible}
        onClose={() => setIsModalVisible(false)}
        inspectionPointId={selectedInspectionId}
      />
    </div>
  );
};

export default InspectorDashboardPage;

