/**
 * Route Operations List Component
 * Drag-and-drop list for managing operations in a route
 */
import { useState } from 'react';
import { Table, Button, Space, Modal, Form, Input, InputNumber, Select, Popconfirm } from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  HolderOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useRouteOperations,
  useAddRouteOperation,
  useUpdateRouteOperation,
  useDeleteRouteOperation,
} from '../hooks/useOperationRoutes';
import { useWorkCenters } from '../../work-centers/hooks/useWorkCenters';
import type { RouteOperation, RouteOperationCreate } from '@/types/manufacturing';

interface RouteOperationsListProps {
  routeId: number;
}

export const RouteOperationsList = ({ routeId }: RouteOperationsListProps) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingOperation, setEditingOperation] = useState<RouteOperation | undefined>();
  const [form] = Form.useForm<RouteOperationCreate>();

  const { data: operations, isLoading } = useRouteOperations(routeId);
  const { data: workCenters } = useWorkCenters();
  const addOperation = useAddRouteOperation();
  const updateOperation = useUpdateRouteOperation();
  const deleteOperation = useDeleteRouteOperation();

  const isSubmitting = addOperation.isPending || updateOperation.isPending;

  const handleAdd = () => {
    setEditingOperation(undefined);
    form.resetFields();
    // Auto-set sequence to next number
    const nextSequence = operations ? operations.length + 1 : 1;
    form.setFieldsValue({ sequence: nextSequence });
    setIsModalOpen(true);
  };

  const handleEdit = (operation: RouteOperation) => {
    setEditingOperation(operation);
    form.setFieldsValue({
      sequence: operation.sequence,
      name: operation.name,
      description: operation.description,
      work_center_id: operation.work_center_id,
      standard_time_minutes: operation.standard_time_minutes,
      setup_time_minutes: operation.setup_time_minutes,
    });
    setIsModalOpen(true);
  };

  const handleDelete = (operationId: number) => {
    deleteOperation.mutate({ routeId, operationId });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      if (editingOperation) {
        await updateOperation.mutateAsync({
          routeId,
          operationId: editingOperation.id,
          data: values,
        });
      } else {
        await addOperation.mutateAsync({
          routeId,
          data: values,
        });
      }

      setIsModalOpen(false);
      form.resetFields();
    } catch (error) {
      console.error('Form error:', error);
    }
  };

  const columns: ColumnsType<RouteOperation> = [
    {
      key: 'drag',
      width: 40,
      render: () => <HolderOutlined style={{ cursor: 'grab' }} />,
    },
    {
      title: 'Seq',
      dataIndex: 'sequence',
      key: 'sequence',
      width: 60,
      align: 'center',
    },
    {
      title: 'Operation Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Work Center',
      dataIndex: 'work_center_name',
      key: 'work_center',
      render: (_, record) => {
        const wc = workCenters?.find((w) => w.id === record.work_center_id);
        return wc?.name || record.work_center_id;
      },
    },
    {
      title: 'Standard Time (min)',
      dataIndex: 'standard_time_minutes',
      key: 'standard_time',
      width: 150,
      align: 'right',
    },
    {
      title: 'Setup Time (min)',
      dataIndex: 'setup_time_minutes',
      key: 'setup_time',
      width: 140,
      align: 'right',
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      align: 'center',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          />
          <Popconfirm
            title="Delete this operation?"
            onConfirm={() => handleDelete(record.id)}
            okText="Delete"
            okType="danger"
          >
            <Button type="link" danger icon={<DeleteOutlined />} size="small" />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="mb-4">
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          Add Operation
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={operations || []}
        rowKey="id"
        loading={isLoading}
        pagination={false}
        size="small"
      />

      <Modal
        title={editingOperation ? 'Edit Operation' : 'Add Operation'}
        open={isModalOpen}
        onOk={handleSubmit}
        onCancel={() => setIsModalOpen(false)}
        confirmLoading={isSubmitting}
        okText={editingOperation ? 'Update' : 'Add'}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="sequence"
            label="Sequence"
            rules={[{ required: true, message: 'Please enter sequence' }]}
          >
            <InputNumber style={{ width: '100%' }} min={1} />
          </Form.Item>

          <Form.Item
            name="name"
            label="Operation Name"
            rules={[{ required: true, message: 'Please enter operation name' }]}
          >
            <Input placeholder="e.g., PCB Assembly" />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <Input.TextArea rows={2} placeholder="Optional description..." />
          </Form.Item>

          <Form.Item
            name="work_center_id"
            label="Work Center"
            rules={[{ required: true, message: 'Please select work center' }]}
          >
            <Select
              showSearch
              placeholder="Select work center"
              optionFilterProp="children"
              loading={!workCenters}
            >
              {workCenters?.map((wc) => (
                <Select.Option key={wc.id} value={wc.id}>
                  {wc.name} ({wc.code})
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="standard_time_minutes"
            label="Standard Time (minutes)"
            rules={[{ required: true, message: 'Please enter standard time' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={0.1}
              step={5}
              precision={1}
              addonAfter="minutes"
            />
          </Form.Item>

          <Form.Item
            name="setup_time_minutes"
            label="Setup Time (minutes)"
            rules={[{ required: true, message: 'Please enter setup time' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={0}
              step={5}
              precision={1}
              addonAfter="minutes"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};


