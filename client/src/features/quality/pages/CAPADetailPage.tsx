import { useState } from 'react';
import { Card, Descriptions, Button, Steps, Divider, Spin, Alert, Typography, Modal, Form, Input, Checkbox, Table } from 'antd';
import { ArrowLeftOutlined, PlusOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useCAPA, useVerifyCAPA, useCloseCAPA } from '../hooks/useCAPAs';
import { QualityStatusBadge } from '../components/QualityStatusBadge';
import dayjs from 'dayjs';

const { Step } = Steps;

const CAPADetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: capa, isLoading, isError } = useCAPA(Number(id));

  const verifyCAPA = useVerifyCAPA();
  const closeCAPA = useCloseCAPA();

  const [verificationModalVisible, setVerificationModalVisible] = useState(false);

  if (isLoading) return <Spin className="flex justify-center p-12" />;
  if (isError || !capa) return <Alert message="CAPA not found" type="error" />;

  const currentStep = () => {
    switch (capa.status) {
      case 'open': return 0;
      case 'in_progress': return 1;
      case 'verification': return 2;
      case 'closed': return 3;
      default: return 0;
    }
  };

  const handleVerificationSubmit = async (values: any) => {
    await verifyCAPA.mutateAsync({ id: capa.id, data: values });
    setVerificationModalVisible(false);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)} />
        <div>
          <Typography.Title level={2} style={{ margin: 0 }}>
            {capa.capa_number}
          </Typography.Title>
          <Typography.Text type="secondary">
            {capa.title}
          </Typography.Text>
        </div>
        <div className="ml-auto">
          {capa.status === 'verification' && (
            <Button type="primary" onClick={() => setVerificationModalVisible(true)}>
              Verify Effectiveness
            </Button>
          )}
          {capa.status === 'closed' ? (
            <Button disabled>Closed</Button>
          ) : null}
        </div>
      </div>

      <Card className="mb-6">
        <Steps current={currentStep()} size="small">
          <Step title="Open" description="Defined" />
          <Step title="In Progress" description="Actions Ongoing" />
          <Step title="Verification" description="Verify Effectiveness" />
          <Step title="Closed" description="Completed" />
        </Steps>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card title="CAPA Details">
            <Descriptions column={2}>
              <Descriptions.Item label="Status">
                <QualityStatusBadge type="capa" value={capa.status} />
              </Descriptions.Item>
              <Descriptions.Item label="Owner">User #{capa.owner_id}</Descriptions.Item>
              <Descriptions.Item label="Due Date">
                {capa.due_date ? dayjs(capa.due_date).format('MMM D, YYYY') : 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="NCR">
                {capa.ncr_id ? <Button type="link" className="p-0">View NCR</Button> : 'N/A'}
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <Typography.Title level={5}>Description</Typography.Title>
            <p className="text-gray-600">{capa.description}</p>

            <Divider />
            <Typography.Title level={5}>Root Cause</Typography.Title>
            <p className="text-gray-600">{capa.root_cause}</p>
          </Card>

          <Card title="Action Items" extra={<Button size="small" icon={<PlusOutlined />}>Add Action</Button>}>
            <Table
              dataSource={[]} // TODO: Add action items to CAPA type and API
              columns={[
                { title: 'Description', dataIndex: 'description' },
                { title: 'Assignee', dataIndex: 'assignee' },
                { title: 'Due Date', dataIndex: 'due_date' },
                { title: 'Status', dataIndex: 'status' }
              ]}
              locale={{ emptyText: 'No action items yet' }}
            />
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Verification">
            {capa.verified_at ? (
              <div>
                <Alert message="Verified Effective" type="success" showIcon />
                <p className="mt-2 text-gray-500">Verified on {dayjs(capa.verified_at).format('MMM D, YYYY')}</p>
              </div>
            ) : (
              <div className="text-gray-400 text-center py-4">
                Pending Verification
              </div>
            )}
          </Card>
        </div>
      </div>

      {/* Verification Modal */}
      <Modal
        title="Verify Effectiveness"
        open={verificationModalVisible}
        onCancel={() => setVerificationModalVisible(false)}
        footer={null}
      >
        <Form layout="vertical" onFinish={handleVerificationSubmit}>
          <Form.Item name="verification_notes" label="Verification Notes" rules={[{ required: true }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item name="is_effective" valuePropName="checked">
            <Checkbox>Corrective actions are effective</Checkbox>
          </Form.Item>
          <div className="flex justify-end gap-2">
            <Button onClick={() => setVerificationModalVisible(false)}>Cancel</Button>
            <Button type="primary" htmlType="submit">Submit Verification</Button>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default CAPADetailPage;


