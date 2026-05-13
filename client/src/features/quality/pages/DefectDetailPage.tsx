import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Button, Divider, Spin, Alert, Typography } from 'antd';
import { ArrowLeftOutlined, FileTextOutlined } from '@ant-design/icons';
import { useDefect, useCloseDefect } from '../hooks/useDefects';
import { QualityStatusBadge } from '../components/QualityStatusBadge';
import dayjs from 'dayjs';

const DefectDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: defect, isLoading, isError } = useDefect(Number(id));
  const closeDefect = useCloseDefect();

  if (isLoading) return <Spin className="flex justify-center p-12" />;
  if (isError || !defect) return <Alert message="Defect not found" type="error" />;

  const handleClose = async () => {
    // In a real app, this would open a modal to enter resolution
    try {
      await closeDefect.mutateAsync({ id: defect.id, resolution: 'Closed by user' });
    } catch (error) {
      // Error handled by hook/global handler
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)} />
        <div>
          <Typography.Title level={2} style={{ margin: 0 }}>
            {defect.defect_number}
          </Typography.Title>
          <Typography.Text type="secondary">
            Reported on {dayjs(defect.created_at).format('MMMM D, YYYY HH:mm')}
          </Typography.Text>
        </div>
        <div className="ml-auto flex gap-2">
          {defect.status !== 'closed' && (
            <Button type="primary" onClick={handleClose}>
              Close Defect
            </Button>
          )}
          <Button icon={<FileTextOutlined />}>Create NCR</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card title="Defect Details">
            <Descriptions column={2}>
              <Descriptions.Item label="Type">
                <span className="capitalize">{defect.defect_type}</span>
              </Descriptions.Item>
              <Descriptions.Item label="Severity">
                <QualityStatusBadge type="defect-severity" value={defect.severity} />
              </Descriptions.Item>
              <Descriptions.Item label="Status">
                <QualityStatusBadge type="defect-status" value={defect.status} />
              </Descriptions.Item>
              <Descriptions.Item label="Quantity Affected">
                {defect.quantity_affected}
              </Descriptions.Item>
              <Descriptions.Item label="Manufacturing Order">
                {defect.manufacturing_order_id ? (
                  <Button type="link" className="p-0">
                    MO-{defect.manufacturing_order_id}
                  </Button>
                ) : 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="Operation">
                {defect.mo_operation_id ? `Op #${defect.mo_operation_id}` : 'N/A'}
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <Typography.Title level={5}>Description</Typography.Title>
            <p className="text-gray-600">{defect.description}</p>

            {defect.root_cause && (
              <>
                <Divider />
                <Typography.Title level={5}>Root Cause</Typography.Title>
                <p className="text-gray-600">{defect.root_cause}</p>
              </>
            )}

            {defect.corrective_action && (
              <>
                <Divider />
                <Typography.Title level={5}>Corrective Action</Typography.Title>
                <p className="text-gray-600">{defect.corrective_action}</p>
              </>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Related Items">
            {/* Placeholder for related NCRs/CAPAs */}
            <div className="text-gray-400 text-center py-4">
              No related NCRs
            </div>
          </Card>

          <Card title="History">
            {/* Placeholder for history timeline */}
            <div className="text-gray-400 text-center py-4">
              Timeline coming soon
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DefectDetailPage;

