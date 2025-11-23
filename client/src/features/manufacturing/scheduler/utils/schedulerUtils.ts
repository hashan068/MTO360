/**
 * Scheduler Utility Functions
 * Helper functions for timeline calculations and rendering
 */
import dayjs, { Dayjs } from 'dayjs';

export interface TimelineConfig {
  startDate: Dayjs;
  endDate: Dayjs;
  pixelsPerHour: number;
  workDayStartHour: number;
  workDayEndHour: number;
}

/**
 * Calculate pixel position from datetime
 */
export const datetimeToPixel = (
  datetime: string | Date,
  config: TimelineConfig
): number => {
  const date = dayjs(datetime);
  const hoursSinceStart = date.diff(config.startDate, 'hour', true);
  return hoursSinceStart * config.pixelsPerHour;
};

/**
 * Calculate datetime from pixel position
 */
export const pixelToDatetime = (
  pixel: number,
  config: TimelineConfig
): Dayjs => {
  const hoursFromStart = pixel / config.pixelsPerHour;
  return config.startDate.add(hoursFromStart, 'hour');
};

/**
 * Calculate duration in pixels
 */
export const durationToPixels = (
  durationMinutes: number,
  config: TimelineConfig
): number => {
  const hours = durationMinutes / 60;
  return hours * config.pixelsPerHour;
};

/**
 * Snap datetime to nearest hour
 */
export const snapToHour = (datetime: Dayjs): Dayjs => {
  const minutes = datetime.minute();
  if (minutes < 30) {
    return datetime.startOf('hour');
  } else {
    return datetime.startOf('hour').add(1, 'hour');
  }
};

/**
 * Generate time markers for timeline
 */
export const generateTimeMarkers = (
  startDate: Dayjs,
  endDate: Dayjs,
  interval: 'hour' | 'day' = 'hour'
): Dayjs[] => {
  const markers: Dayjs[] = [];
  let current = startDate.startOf(interval);

  while (current.isBefore(endDate) || current.isSame(endDate)) {
    markers.push(current);
    current = current.add(1, interval);
  }

  return markers;
};

/**
 * Check if operation overlaps with time range
 */
export const operationOverlaps = (
  opStart: string,
  opEnd: string,
  rangeStart: Dayjs,
  rangeEnd: Dayjs
): boolean => {
  const start = dayjs(opStart);
  const end = dayjs(opEnd);

  return (
    (start.isBefore(rangeEnd) && end.isAfter(rangeStart)) ||
    start.isSame(rangeStart) ||
    end.isSame(rangeEnd)
  );
};

/**
 * Get operation status color
 */
export const getOperationStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    pending: '#d9d9d9',
    scheduled: '#1890ff',
    in_progress: '#52c41a',
    completed: '#8c8c8c',
    blocked: '#ff4d4f',
    cancelled: '#595959',
  };
  return colors[status] || colors.pending;
};

/**
 * Format timeline date label
 */
export const formatTimelineLabel = (
  date: Dayjs,
  format: 'hour' | 'day' | 'week'
): string => {
  switch (format) {
    case 'hour':
      return date.format('HH:mm');
    case 'day':
      return date.format('MMM DD');
    case 'week':
      return date.format('MMM DD');
    default:
      return date.format('HH:mm');
  }
};

/**
 * Calculate visible date range based on zoom level
 */
export const getVisibleDateRange = (
  centerDate: Dayjs,
  zoomLevel: 'day' | 'week' | 'month'
): { start: Dayjs; end: Dayjs } => {
  switch (zoomLevel) {
    case 'day':
      return {
        start: centerDate.startOf('day'),
        end: centerDate.endOf('day'),
      };
    case 'week':
      return {
        start: centerDate.startOf('week'),
        end: centerDate.endOf('week'),
      };
    case 'month':
      return {
        start: centerDate.startOf('month'),
        end: centerDate.endOf('month'),
      };
  }
};
