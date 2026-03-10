import { useState } from 'react';
import { Card, Descriptions, Button, Divider, Spin, Alert, Typography, Modal, Form, Input } from 'antd';
import { ArrowLeftOutlined, UnlockOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useQualityHolds, useReleaseHold } from '../hooks/useQualityMetrics'; // Using existing hook, might need specific getHold
import { QualityStatusBadge } from '../components/QualityStatusBadge';
import dayjs from 'dayjs';

// Note: We need a specific useQualityHold(id) hook, but for now we'll fetch list and find (or assume hook exists)
// Let's assume we add useQualityHold to hooks/useQualityMetrics.ts or use axios directly for now to save a step
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

const useHoldDetail = (id: number) => useQuery({
  queryKey: ['quality', 'holds', id],
  queryFn: async () => {
    const { data } = await axios.get(`/api/quality/holds/${id}`);
    return data;
  },
  enabled: !!id
});

const QualityHoldDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: hold, isLoading, isError } = useHoldDetail(Number(id));
  const releaseHold = useReleaseHold();
  const [releaseModalVisible, setReleaseModalVisible] = useState(false);

  if (isLoading) return <Spin className="flex justify-center p-12" />;
  if (isError || !hold) return <Alert message="Hold not found" type="error" />;

  const handleReleaseSubmit = async (values: any) => {
    await releaseHold.mutateAsync({ id: hold.id, releaseNotes: values.release_notes });
    setReleaseModalVisible(false);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)} />
        <div>
          <Typography.Title level={2} style={{ margin: 0 }}>
            {hold.hold_number}
          </Typography.Title>
          <Typography.Text type="secondary">
            Placed on {dayjs(hold.placed_at).format('MMMM D, YYYY')}
          </Typography.Text>
        </div>
        <div className="ml-auto">
          {hold.status === 'active' && (
            <Button type="primary" danger icon={<UnlockOutlined />} onClick={() => setReleaseModalVisible(true)}>
              Release Hold
            </Button>
          )}
        </div>
      </div>

      <Card title="Hold Details">
        <Descriptions column={2}>
          <Descriptions.Item label="Status">
            <QualityStatusBadge type="hold" value={hold.status} />
          </Descriptions.Item>
          <Descriptions.Item label="Type">
            <span className="capitalize">{hold.hold_type.replace('_', ' ')}</span>
          </Descriptions.Item>
          <Descriptions.Item label="Reason">
            {hold.hold_reason}
          </Descriptions.Item>
          <Descriptions.Item label="Placed By">
            User #{hold.placed_by_id}
          </Descriptions.Item>
          <Descriptions.Item label="Target Entity">
            {hold.manufacturing_order_id ? `MO-${hold.manufacturing_order_id}` :
              hold.component_id ? `Component #${hold.component_id}` : 'N/A'}
          </Descriptions.Item>
        </Descriptions>

        {hold.status === 'released' && (
          <>
            <Divider />
            <Typography.Title level={5}>Release Information</Typography.Title>
            <Descriptions column={1}>
              <Descriptions.Item label="Released At">
                {dayjs(hold.released_at).format('MMM D, YYYY HH:mm')}
              </Descriptions.Item>
              <Descriptions.Item label="Released By">
                User #{hold.released_by_id}
              </Descriptions.Item>
              <Descriptions.Item label="Release Notes">
                {hold.release_notes}
              </Descriptions.Item>
            </Descriptions>
          </>
        )}
      </Card>

      <Modal
        title="Release Quality Hold"
        open={releaseModalVisible}
        onCancel={() => setReleaseModalVisible(false)}
        footer={null}
      >
        <Alert
          message="Warning"
          description="Releasing this hold will allow operations to proceed. Ensure all quality issues are resolved."
          type="warning"
          showIcon
          className="mb-4"
        />
        <Form layout="vertical" onFinish={handleReleaseSubmit}>
          <Form.Item name="release_notes" label="Release Notes / Justification" rules={[{ required: true }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <div className="flex justify-end gap-2">
            <Button onClick={() => setReleaseModalVisible(false)}>Cancel</Button>
            <Button type="primary" htmlType="submit">Confirm Release</Button>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default QualityHoldDetailPage;

