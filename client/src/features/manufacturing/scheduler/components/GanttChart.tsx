/**
 * Gantt Chart Component
 * Main timeline visualization for scheduled operations
 */
import React, { useMemo } from 'react';
import { Spin } from 'antd';
import type { Dayjs } from 'dayjs';
import type { ManufacturingOrderOperation, WorkCenter } from '@/types/manufacturing';
import { WorkCenterRow } from './WorkCenterRow';
import {
  generateTimeMarkers,
  datetimeToPixel,
  type TimelineConfig,
  formatTimelineLabel,
} from '../utils/schedulerUtils';

interface GanttChartProps {
  workCenters: WorkCenter[];
  operations: ManufacturingOrderOperation[];
  startDate: Dayjs;
  endDate: Dayjs;
  pixelsPerHour?: number;
  onReschedule?: (operationId: number, newStart: string) => void;
  onOperationClick?: (operation: ManufacturingOrderOperation) => void;
  isLoading?: boolean;
}

const ROW_HEIGHT = 60;
const HEADER_HEIGHT = 40;

export const GanttChart: React.FC<GanttChartProps> = ({
  workCenters,
  operations,
  startDate,
  endDate,
  pixelsPerHour = 40,
  onReschedule,
  onOperationClick,
  isLoading,
}) => {
  const timelineConfig: TimelineConfig = useMemo(
    () => ({
      startDate,
      endDate,
      pixelsPerHour,
      workDayStartHour: 8,
      workDayEndHour: 17,
    }),
    [startDate, endDate, pixelsPerHour]
  );

  const timeMarkers = useMemo(
    () => generateTimeMarkers(startDate, endDate, 'hour'),
    [startDate, endDate]
  );

  const totalWidth = useMemo(() => {
    const hours = endDate.diff(startDate, 'hour');
    return hours * pixelsPerHour;
  }, [startDate, endDate, pixelsPerHour]);

  // Group operations by work center
  const operationsByWorkCenter = useMemo(() => {
    const grouped: Record<number, ManufacturingOrderOperation[]> = {};
    operations.forEach((op) => {
      if (!grouped[op.work_center_id]) {
        grouped[op.work_center_id] = [];
      }
      grouped[op.work_center_id].push(op);
    });
    return grouped;
  }, [operations]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
      {/* Timeline Header */}
      <div className="flex border-b border-gray-200 bg-gray-50 sticky top-0 z-10">
        <div className="w-48 flex-shrink-0 border-r border-gray-200 p-2 font-semibold">
          Work Centers
        </div>
        <div className="flex-1 overflow-x-auto">
          <div
            className="relative"
            style={{ height: `${HEADER_HEIGHT}px`, width: `${totalWidth}px` }}
          >
            {timeMarkers.map((marker, index) => {
              const x = datetimeToPixel(marker.toISOString(), timelineConfig);
              const isNoonOrMidnight = marker.hour() === 0 || marker.hour() === 12;

              return (
                <div
                  key={index}
                  className="absolute flex flex-col items-center"
                  style={{ left: `${x}px`, top: 0 }}
                >
                  <div
                    className={`text-xs ${isNoonOrMidnight ? 'font-semibold' : 'text-gray-500'
                      }`}
                  >
                    {formatTimelineLabel(marker, 'hour')}
                  </div>
                  {marker.hour() === 0 && (
                    <div className="text-xs text-gray-600 font-medium">
                      {marker.format('MMM DD')}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Work Center Rows */}
      <div className="overflow-auto" style={{ maxHeight: '600px' }}>
        <div className="flex flex-col">
          {workCenters.map((workCenter) => (
            <WorkCenterRow
              key={workCenter.id}
              workCenter={workCenter}
              operations={operationsByWorkCenter[workCenter.id] || []}
              timelineConfig={timelineConfig}
              rowHeight={ROW_HEIGHT}
              onReschedule={onReschedule}
              onOperationClick={onOperationClick}
            />
          ))}
        </div>

        {/* Grid Lines */}
        <div className="absolute inset-0 pointer-events-none">
          {timeMarkers.map((marker, index) => {
            const x = datetimeToPixel(marker.toISOString(), timelineConfig);
            const isDay = marker.hour() === 0;

            return (
              <div
                key={index}
                className="absolute top-0 bottom-0 border-l"
                style={{
                  left: `${x}px`,
                  borderColor: isDay ? '#d9d9d9' : '#f0f0f0',
                  borderWidth: isDay ? '1px' : '1px',
                }}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
};

