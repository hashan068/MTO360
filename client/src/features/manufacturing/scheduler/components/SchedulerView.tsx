/**
 * Scheduler View Component
 * Main container for production scheduler with controls
 */
import { useState } from 'react';
import { Card, DatePicker, Space, Select, Button, Segmented } from 'antd';
import {
  ZoomInOutlined,
  ZoomOutOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { GanttChart } from './GanttChart';
import { useWorkCenters } from '../../work-centers/hooks/useWorkCenters';
import { useScheduledOperations, useRescheduleOperation } from '../hooks/useScheduler';
import { getVisibleDateRange } from '../utils/schedulerUtils';
import type { ManufacturingOrderOperation } from '@/types/manufacturing';

type ZoomLevel = 'day' | 'week' | 'month';

export const SchedulerView = () => {
  const [centerDate, setCenterDate] = useState<Dayjs>(dayjs());
  const [zoomLevel, setZoomLevel] = useState<ZoomLevel>('week');
  const [selectedWorkCenter, setSelectedWorkCenter] = useState<number | undefined>();

  const { data: workCenters, isLoading: loadingWorkCenters } = useWorkCenters();

  const dateRange = getVisibleDateRange(centerDate, zoomLevel);

  const { data: operations, isLoading: loadingOperations } = useScheduledOperations({
    start_date: dateRange.start.toISOString(),
    end_date: dateRange.end.toISOString(),
    work_center_id: selectedWorkCenter,
  });

  const reschedule = useRescheduleOperation();

  const pixelsPerHourMap: Record<ZoomLevel, number> = {
    day: 60,
    week: 20,
    month: 6,
  };

  const handleReschedule = (operationId: number, newStart: string) => {
    reschedule.mutate({ operationId, newStart });
  };

  const handleOperationClick = (operation: ManufacturingOrderOperation) => {
    // TODO: Open operation detail modal or navigate to detail page
    console.log('Operation clicked:', operation);
  };

  const handleZoomIn = () => {
    if (zoomLevel === 'month') setZoomLevel('week');
    else if (zoomLevel === 'week') setZoomLevel('day');
  };

  const handleZoomOut = () => {
    if (zoomLevel === 'day') setZoomLevel('week');
    else if (zoomLevel === 'week') setZoomLevel('month');
  };

  const handleRefresh = () => {
    // Queries will auto-refresh
    setCenterDate(dayjs());
  };

  const filteredWorkCenters = selectedWorkCenter
    ? workCenters?.filter((wc) => wc.id === selectedWorkCenter)
    : workCenters;

  const filteredOperations = selectedWorkCenter
    ? operations?.filter((op) => op.work_center_id === selectedWorkCenter)
    : operations;

  return (
    <Card
      title="Production Scheduler"
      extra={
        <Space>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
            Refresh
          </Button>
        </Space>
      }
    >
      {/* Controls */}
      <div className="mb-4 flex flex-wrap gap-4 items-center">
        <Space>
          <span className="text-sm text-gray-600">View:</span>
          <Segmented
            options={[
              { label: 'Day', value: 'day' },
              { label: 'Week', value: 'week' },
              { label: 'Month', value: 'month' },
            ]}
            value={zoomLevel}
            onChange={(value) => setZoomLevel(value as ZoomLevel)}
          />
        </Space>

        <Space>
          <span className="text-sm text-gray-600">Date:</span>
          <DatePicker
            value={centerDate}
            onChange={(date) => date && setCenterDate(date)}
          />
        </Space>

        <Space>
          <span className="text-sm text-gray-600">Work Center:</span>
          <Select
            style={{ width: 200 }}
            placeholder="All work centers"
            allowClear
            value={selectedWorkCenter}
            onChange={setSelectedWorkCenter}
            loading={loadingWorkCenters}
          >
            {workCenters?.map((wc) => (
              <Select.Option key={wc.id} value={wc.id}>
                {wc.name}
              </Select.Option>
            ))}
          </Select>
        </Space>

        <Space>
          <Button
            icon={<ZoomInOutlined />}
            onClick={handleZoomIn}
            disabled={zoomLevel === 'day'}
          >
            Zoom In
          </Button>
          <Button
            icon={<ZoomOutOutlined />}
            onClick={handleZoomOut}
            disabled={zoomLevel === 'month'}
          >
            Zoom Out
          </Button>
        </Space>
      </div>

      {/* Gantt Chart */}
      <div className="mt-4">
        <GanttChart
          workCenters={filteredWorkCenters || []}
          operations={filteredOperations || []}
          startDate={dateRange.start}
          endDate={dateRange.end}
          pixelsPerHour={pixelsPerHourMap[zoomLevel]}
          onReschedule={handleReschedule}
          onOperationClick={handleOperationClick}
          isLoading={loadingWorkCenters || loadingOperations}
        />
      </div>

      {/* Legend */}
      <div className="mt-4 flex gap-4 text-xs text-gray-600">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#d9d9d9' }} />
          <span>Pending</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#1890ff' }} />
          <span>Scheduled</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#52c41a' }} />
          <span>In Progress</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#8c8c8c' }} />
          <span>Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ff4d4f' }} />
          <span>Blocked</span>
        </div>
      </div>
    </Card>
  );
};

