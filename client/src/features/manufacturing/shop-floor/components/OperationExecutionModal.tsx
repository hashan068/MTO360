/**
 * Operation Execution Modal Component
 * Modal for executing operations (start, complete, pause, block)
 */
import { useState } from 'react';
import { Modal, Descriptions, Button, Space, Input, Form, Tag, Statistic } from 'antd';
import {
  PlayCircleOutlined,
  CheckCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
} from '@ant-design/icons';
import {
  useStartOperation,
  useCompleteOperation,
  usePauseOperation,
  useBlockOperation,
  useUnblockOperation,
} from '../hooks/useShopFloor';
import dayjs from 'dayjs';
import duration from 'dayjs/plugin/duration';
import type { OperationStatus } from '@/types/manufacturing';

dayjs.extend(duration);

interface OperationExecutionModalProps {
  operationId: number;
  open: boolean;
  onClose: () => void;
}

export const OperationExecutionModal = ({
  operationId,
  open,
  onClose,
}: OperationExecutionModalProps) => {
  const [reasonModalOpen, setReasonModalOpen] = useState(false);
  const [reasonType, setReasonType] = useState<'pause' | 'block'>('pause');
  const [form] = Form.useForm();

  const startMutation = useStartOperation();
  const completeMutation = useCompleteOperation();
  const pauseMutation = usePauseOperation();
  const blockMutation = useBlockOperation();
  const unblockMutation = useUnblockOperation();

  // Mock operation data - in real app, fetch from API
  const operation = {
    id: operationId,
    name: 'PCB Assembly',
    mo_number: 'MO-2025-001',
    sequence: 1,
    status: 'scheduled' as OperationStatus,
    scheduled_start: '2025-01-15T08:00:00',
    scheduled_duration_minutes: 45,
    actual_start: null as string | null,
  };

  const handleStart = () => {
    startMutation.mutate({ operationId });
  };

  const handleComplete = () => {
    Modal.confirm({
      title: 'Complete Operation?',
      content: 'Mark this operation as completed?',
      onOk: () => {
        completeMutation.mutate(operationId);
        onClose();
      },
    });
  };

  const handlePauseClick = () => {
    setReasonType('pause');
    setReasonModalOpen(true);
  };

  const handleBlockClick = () => {
    setReasonType('block');
    setReasonModalOpen(true);
  };

  const handleReasonSubmit = async () => {
    try {
      const values = await form.validateFields();
      const reason = values.reason;

      if (reasonType === 'pause') {
        await pauseMutation.mutateAsync({ operationId, reason });
      } else {
        await blockMutation.mutateAsync({ operationId, reason });
      }

      setReasonModalOpen(false);
      form.resetFields();
      onClose();
    } catch (error) {
      // Form validation failed
    }
  };

  const handleUnblock = () => {
    unblockMutation.mutate(operationId);
  };

  const getElapsedTime = () => {
    if (!operation.actual_start) return '00:00:00';
    const start = dayjs(operation.actual_start);
    const now = dayjs();
    const diff = now.diff(start);
    const dur = dayjs.duration(diff);
    return `${String(Math.floor(dur.asHours())).padStart(2, '0')}:${String(dur.minutes()).padStart(2, '0')}:${String(dur.seconds()).padStart(2, '0')}`;
  };

  const canStart = operation.status === 'scheduled' || operation.status === 'pending';
  const canComplete = operation.status === 'in_progress';
  const canPause = operation.status === 'in_progress';
  const canBlock = operation.status !== 'completed' && operation.status !== 'blocked';
  const canUnblock = operation.status === 'blocked';

  return (
    <>
      <Modal
        title="Operation Execution"
        open={open}
        onCancel={onClose}
        footer={null}
        width={600}
      >
        <div className="space-y-4">
          {/* Operation Info */}
          <Descriptions column={2} size="small">
            <Descriptions.Item label="MO" span={2}>
              {operation.mo_number}
            </Descriptions.Item>
            <Descriptions.Item label="Operation" span={2}>
              {operation.name}
            </Descriptions.Item>
            <Descriptions.Item label="Sequence">
              {operation.sequence}
            </Descriptions.Item>
            <Descriptions.Item label="Status">
              <Tag color={operation.status === 'in_progress' ? 'green' : operation.status === 'blocked' ? 'red' : 'blue'}>
                {operation.status.toUpperCase().replace('_', ' ')}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Scheduled Start">
              {dayjs(operation.scheduled_start).format('MMM DD, HH:mm')}
            </Descriptions.Item>
            <Descriptions.Item label="Duration">
              {operation.scheduled_duration_minutes} min
            </Descriptions.Item>
          </Descriptions>

          {/* Timer for in-progress operations */}
          {operation.status === 'in_progress' && (
            <div className="p-4 bg-green-50 rounded">
              <Statistic
                title="Elapsed Time"
                value={getElapsedTime()}
                valueStyle={{ color: '#52c41a', fontSize: '32px', fontFamily: 'monospace' }}
              />
            </div>
          )}

          {/* Action Buttons */}
          <Space size="middle" className="w-full justify-center">
            {canStart && (
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleStart}
                loading={startMutation.isPending}
                size="large"
              >
                Start
              </Button>
            )}

            {canComplete && (
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={handleComplete}
                loading={completeMutation.isPending}
                style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                size="large"
              >
                Complete
              </Button>
            )}

            {canPause && (
              <Button
                icon={<PauseCircleOutlined />}
                onClick={handlePauseClick}
                loading={pauseMutation.isPending}
                size="large"
              >
                Pause
              </Button>
            )}

            {canBlock && (
              <Button
                danger
                icon={<StopOutlined />}
                onClick={handleBlockClick}
                loading={blockMutation.isPending}
                size="large"
              >
                Block
              </Button>
            )}

            {canUnblock && (
              <Button
                type="primary"
                onClick={handleUnblock}
                loading={unblockMutation.isPending}
                size="large"
              >
                Unblock
              </Button>
            )}
          </Space>
        </div>
      </Modal>

      {/* Reason Modal */}
      <Modal
        title={`${reasonType === 'pause' ? 'Pause' : 'Block'} Operation`}
        open={reasonModalOpen}
        onOk={handleReasonSubmit}
        onCancel={() => {
          setReasonModalOpen(false);
          form.resetFields();
        }}
        okText="Submit"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="reason"
            label="Reason"
            rules={[{ required: true, message: 'Please provide a reason' }]}
          >
            <Input.TextArea
              rows={3}
              placeholder={`Explain why this operation is being ${reasonType}ed...`}
            />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

