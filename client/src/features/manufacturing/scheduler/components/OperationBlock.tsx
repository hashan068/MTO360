/**
 * Operation Block Component
 * Visual representation of a scheduled operation in timeline
 */
import React from 'react';
import { Tooltip } from 'antd';
import type { ManufacturingOrderOperation } from '@/types/manufacturing';
import { getOperationStatusColor, durationToPixels, datetimeToPixel, type TimelineConfig } from '../utils/schedulerUtils';
import dayjs from 'dayjs';

interface OperationBlockProps {
  operation: ManufacturingOrderOperation;
  timelineConfig: TimelineConfig;
  rowHeight: number;
  onDragStart?: (operation: ManufacturingOrderOperation, e: React.DragEvent) => void;
  onDoubleClick?: (operation: ManufacturingOrderOperation) => void;
}

export const OperationBlock: React.FC<OperationBlockProps> = ({
  operation,
  timelineConfig,
  rowHeight,
  onDragStart,
  onDoubleClick,
}) => {
  if (!operation.scheduled_start || !operation.scheduled_end) {
    return null;
  }

  const startX = datetimeToPixel(operation.scheduled_start, timelineConfig);
  const width = durationToPixels(operation.scheduled_duration_minutes, timelineConfig);
  const color = getOperationStatusColor(operation.status);

  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('application/json', JSON.stringify(operation));
    onDragStart?.(operation, e);
  };

  const variance = operation.actual_duration_minutes
    ? operation.actual_duration_minutes - operation.scheduled_duration_minutes
    : 0;

  return (
    <Tooltip
      title={
        <div className="text-xs">
          <div className="font-semibold">{operation.name}</div>
          <div>MO: {operation.manufacturing_order_id}</div>
          <div>Sequence: {operation.sequence}</div>
          <div>Duration: {operation.scheduled_duration_minutes} min</div>
          <div>Start: {dayjs(operation.scheduled_start).format('MMM DD, HH:mm')}</div>
          <div>End: {dayjs(operation.scheduled_end).format('MMM DD, HH:mm')}</div>
          {operation.actual_start && <div>Actual Start: {dayjs(operation.actual_start).format('MMM DD, HH:mm')}</div>}
          {operation.actual_duration_minutes && (
            <div>
              Actual Duration: {operation.actual_duration_minutes} min
              {variance !== 0 && (
                <span className={variance > 0 ? 'text-red-400' : 'text-green-400'}>
                  {' '}({variance > 0 ? '+' : ''}{variance} min)
                </span>
              )}
            </div>
          )}
          {operation.assigned_operator_id && <div>Operator: {operation.assigned_operator_id}</div>}
          {operation.blocking_reason && <div className="text-red-400">Blocked: {operation.blocking_reason}</div>}
        </div>
      }
      mouseEnterDelay={0.5}
    >
      <div
        draggable={operation.status === 'scheduled' || operation.status === 'pending'}
        onDragStart={handleDragStart}
        onDoubleClick={() => onDoubleClick?.(operation)}
        className="absolute cursor-move rounded px-2 py-1 text-xs font-medium text-white overflow-hidden hover:opacity-90 transition-opacity"
        style={{
          left: `${startX}px`,
          width: `${width}px`,
          height: `${rowHeight - 8}px`,
          backgroundColor: color,
          minWidth: '40px',
          border: operation.status === 'in_progress' ? '2px solid #389e0d' : 'none',
          boxShadow: operation.status === 'blocked' ? '0 0 0 2px #ff4d4f' : '0 1px 2px rgba(0,0,0,0.1)',
        }}
      >
        <div className="truncate">
          {operation.name}
        </div>
        <div className="text-xs opacity-75 truncate">
          {operation.scheduled_duration_minutes}m
        </div>
      </div>
    </Tooltip>
  );
};

