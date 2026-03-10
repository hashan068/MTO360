/**
 * Work Center Row Component
 * Single row in Gantt chart representing a work center
 */
import React, { useState } from 'react';
import { Tag } from 'antd';
import type { ManufacturingOrderOperation, WorkCenter } from '@/types/manufacturing';
import { OperationBlock } from './OperationBlock';
import type { TimelineConfig } from '../utils/schedulerUtils';
import { datetimeToPixel, pixelToDatetime, snapToHour } from '../utils/schedulerUtils';

interface WorkCenterRowProps {
  workCenter: WorkCenter;
  operations: ManufacturingOrderOperation[];
  timelineConfig: TimelineConfig;
  rowHeight: number;
  onReschedule?: (operationId: number, newStart: string) => void;
  onOperationClick?: (operation: ManufacturingOrderOperation) => void;
}

export const WorkCenterRow: React.FC<WorkCenterRowProps> = ({
  workCenter,
  operations,
  timelineConfig,
  rowHeight,
  onReschedule,
  onOperationClick,
}) => {
  const [isDraggingOver, setIsDraggingOver] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDraggingOver(false);

    try {
      const operationData = e.dataTransfer.getData('application/json');
      const operation: ManufacturingOrderOperation = JSON.parse(operationData);

      // Calculate new start time from drop position
      const rect = e.currentTarget.getBoundingClientRect();
      const dropX = e.clientX - rect.left;
      const newStartTime = pixelToDatetime(dropX, timelineConfig);
      const snappedTime = snapToHour(newStartTime);

      onReschedule?.(operation.id, snappedTime.toISOString());
    } catch (error) {
      console.error('Error handling drop:', error);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const capacityDisplay = `${workCenter.capacity_hours_per_day}h/day`;
  const operationCount = operations.length;

  return (
    <div className="flex border-b border-gray-200 hover:bg-gray-50 transition-colors">
      {/* Work Center Info */}
      <div
        className="w-48 flex-shrink-0 p-2 border-r border-gray-200 flex flex-col justify-center"
        style={{ height: `${rowHeight}px` }}
      >
        <div className="font-medium text-sm truncate" title={workCenter.name}>
          {workCenter.name}
        </div>
        <div className="text-xs text-gray-500 flex items-center gap-2 mt-1">
          <span>{capacityDisplay}</span>
          <Tag color="blue" className="text-xs">{operationCount} ops</Tag>
        </div>
      </div>

      {/* Timeline (Drop Zone) */}
      <div
        className={`flex-1 relative ${isDraggingOver ? 'bg-blue-50' : ''}`}
        style={{ height: `${rowHeight}px` }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragEnter={() => setIsDraggingOver(true)}
        onDragLeave={() => setIsDraggingOver(false)}
      >
        {operations.map((operation) => (
          <OperationBlock
            key={operation.id}
            operation={operation}
            timelineConfig={timelineConfig}
            rowHeight={rowHeight}
            onDoubleClick={onOperationClick}
          />
        ))}
      </div>
    </div>
  );
};

