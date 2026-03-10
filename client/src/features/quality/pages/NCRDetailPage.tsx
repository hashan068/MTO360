import { useState } from 'react';
import { Card, Descriptions, Button, Steps, Divider, Spin, Alert, Typography, Modal, Form, Input, Select, InputNumber } from 'antd';
import { ArrowLeftOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useNCR, useStartInvestigation, useApproveNCR, useCloseNCR } from '../hooks/useNCRs';
import { QualityStatusBadge } from '../components/QualityStatusBadge';
import dayjs from 'dayjs';

const { Step } = Steps;

const NCRDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: ncr, isLoading, isError } = useNCR(Number(id));

  const startInvestigation = useStartInvestigation();
  const approveNCR = useApproveNCR();
  const closeNCR = useCloseNCR();

  const [investigationModalVisible, setInvestigationModalVisible] = useState(false);
  const [approvalModalVisible, setApprovalModalVisible] = useState(false);
  const [form] = Form.useForm();

  if (isLoading) return <Spin className="flex justify-center p-12" />;
  if (isError || !ncr) return <Alert message="NCR not found" type="error" />;

  const currentStep = () => {
    switch (ncr.status) {
      case 'open': return 0;
      case 'under_investigation': return 1;
      case 'under_review': return 2;
      case 'approved': return 3;
      case 'closed': return 4;
      default: return 0;
    }
  };

  const handleInvestigationSubmit = async (values: any) => {
    await startInvestigation.mutateAsync({ id: ncr.id, data: values });
    setInvestigationModalVisible(false);
  };

  const handleApprovalSubmit = async (values: any) => {
    await approveNCR.mutateAsync({ id: ncr.id, data: values });
    setApprovalModalVisible(false);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)} />
        <div>
          <Typography.Title level={2} style={{ margin: 0 }}>
            {ncr.ncr_number}
          </Typography.Title>
          <Typography.Text type="secondary">
            Created on {dayjs(ncr.created_at).format('MMMM D, YYYY')}
          </Typography.Text>
        </div>
        <div className="ml-auto">
          {ncr.status === 'open' && (
            <Button type="primary" onClick={() => setInvestigationModalVisible(true)}>
              Start Investigation
            </Button>
          )}
          {ncr.status === 'under_investigation' && (
            <Button type="primary" onClick={() => setInvestigationModalVisible(true)}>
              Update Investigation
            </Button>
          )}
          {ncr.status === 'under_review' && (
            <Button type="primary" onClick={() => setApprovalModalVisible(true)}>
              Approve / Reject
            </Button>
          )}
          {ncr.status === 'approved' && (
            <Button type="primary" onClick={() => closeNCR.mutate(ncr.id)}>
              Close NCR
            </Button>
          )}
        </div>
      </div>

      <Card className="mb-6">
        <Steps current={currentStep()} size="small">
          <Step title="Open" description="Reported" />
          <Step title="Investigation" description="Root Cause Analysis" />
          <Step title="Review" description="Pending Approval" />
          <Step title="Disposition" description="Approved" />
          <Step title="Closed" description="Completed" />
        </Steps>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card title="NCR Details">
            <Descriptions column={2}>
              <Descriptions.Item label="Status">
                <QualityStatusBadge type="ncr" value={ncr.status} />
              </Descriptions.Item>
              <Descriptions.Item label="Priority">
                <span className="capitalize font-medium">{ncr.priority}</span>
              </Descriptions.Item>
              <Descriptions.Item label="Owner">User #{ncr.owner_id}</Descriptions.Item>
              <Descriptions.Item label="Defect">
                {ncr.defect_id ? <Button type="link" className="p-0">View Defect</Button> : 'N/A'}
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <Typography.Title level={5}>Description</Typography.Title>
            <p className="text-gray-600">{ncr.description}</p>

            {ncr.root_cause_analysis && (
              <>
                <Divider />
                <Typography.Title level={5}>Root Cause Analysis</Typography.Title>
                <p className="text-gray-600">{ncr.root_cause_analysis}</p>
              </>
            )}

            {ncr.containment_action && (
              <>
                <Divider />
                <Typography.Title level={5}>Containment Action</Typography.Title>
                <p className="text-gray-600">{ncr.containment_action}</p>
              </>
            )}

            {ncr.disposition && (
              <>
                <Divider />
                <Typography.Title level={5}>Disposition</Typography.Title>
                <p className="text-gray-600 capitalize">{ncr.disposition.replace('_', ' ')}</p>
              </>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <Card title="Cost Impact">
            <div className="text-center py-4">
              <Typography.Title level={2} style={{ margin: 0 }}>
                ${ncr.cost || 0}
              </Typography.Title>
              <Typography.Text type="secondary">Total Cost of Quality</Typography.Text>
            </div>
          </Card>
        </div>
      </div>

      {/* Investigation Modal */}
      <Modal
        title="NCR Investigation"
        open={investigationModalVisible}
        onCancel={() => setInvestigationModalVisible(false)}
        footer={null}
      >
        <Form layout="vertical" onFinish={handleInvestigationSubmit}>
          <Form.Item name="root_cause_analysis" label="Root Cause Analysis" rules={[{ required: true }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item name="containment_action" label="Containment Action" rules={[{ required: true }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <div className="flex justify-end gap-2">
            <Button onClick={() => setInvestigationModalVisible(false)}>Cancel</Button>
            <Button type="primary" htmlType="submit">Submit Investigation</Button>
          </div>
        </Form>
      </Modal>

      {/* Approval Modal */}
      <Modal
        title="NCR Disposition"
        open={approvalModalVisible}
        onCancel={() => setApprovalModalVisible(false)}
        footer={null}
      >
        <Form layout="vertical" onFinish={handleApprovalSubmit}>
          <Form.Item name="disposition" label="Disposition" rules={[{ required: true }]}>
            <Select options={[
              { label: 'Use As Is', value: 'use_as_is' },
              { label: 'Rework', value: 'rework' },
              { label: 'Scrap', value: 'scrap' },
              { label: 'Return to Vendor', value: 'return_to_vendor' },
            ]} />
          </Form.Item>
          <Form.Item name="cost" label="Estimated Cost">
            <InputNumber className="w-full" prefix="$" min={0} />
          </Form.Item>
          <div className="flex justify-end gap-2">
            <Button onClick={() => setApprovalModalVisible(false)}>Cancel</Button>
            <Button type="primary" htmlType="submit">Approve NCR</Button>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default NCRDetailPage;

