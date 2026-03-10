import { Tag } from 'antd';
import type {
  InspectionResult,
  DefectSeverity,
  DefectStatus,
  NCRStatus,
  CAPAStatus,
  HoldStatus
} from '../types';

interface QualityStatusBadgeProps {
  type: 'inspection' | 'defect-severity' | 'defect-status' | 'ncr' | 'capa' | 'hold';
  value: string;
  className?: string;
}

export const QualityStatusBadge = ({ type, value, className }: QualityStatusBadgeProps) => {
  // Guard against undefined/null values
  if (!value) {
    return (
      <Tag color="default" className={className}>
        N/A
      </Tag>
    );
  }

  let color = 'default';
  let text = value;

  switch (type) {
    case 'inspection':
      const result = value as InspectionResult;
      if (result === 'pass') color = 'success';
      else if (result === 'fail') color = 'error';
      else if (result === 'conditional') color = 'warning';
      text = result.toUpperCase();
      break;

    case 'defect-severity':
      const severity = value as DefectSeverity;
      if (severity === 'critical') color = 'error';
      else if (severity === 'major') color = 'warning';
      else if (severity === 'minor') color = 'processing';
      text = severity.toUpperCase();
      break;

    case 'defect-status':
      const dStatus = value as DefectStatus;
      if (dStatus === 'open') color = 'error';
      else if (dStatus === 'investigating') color = 'processing';
      else if (dStatus === 'resolved') color = 'success';
      else if (dStatus === 'closed') color = 'default';
      text = dStatus.replace('_', ' ').toUpperCase();
      break;

    case 'ncr':
      const nStatus = value as NCRStatus;
      if (nStatus === 'open') color = 'error';
      else if (nStatus === 'under_investigation') color = 'processing';
      else if (nStatus === 'under_review') color = 'warning';
      else if (nStatus === 'approved') color = 'purple';
      else if (nStatus === 'closed') color = 'success';
      else if (nStatus === 'rejected') color = 'default';
      text = nStatus.replace('_', ' ').toUpperCase();
      break;

    case 'capa':
      const cStatus = value as CAPAStatus;
      if (cStatus === 'open') color = 'error';
      else if (cStatus === 'in_progress') color = 'processing';
      else if (cStatus === 'verification') color = 'warning';
      else if (cStatus === 'closed') color = 'success';
      text = cStatus.replace('_', ' ').toUpperCase();
      break;

    case 'hold':
      const hStatus = value as HoldStatus;
      if (hStatus === 'active') color = 'error';
      else if (hStatus === 'released') color = 'success';
      else if (hStatus === 'cancelled') color = 'default';
      text = hStatus.toUpperCase();
      break;
  }

  return (
    <Tag color={color} className={className}>
      {text}
    </Tag>
  );
};

