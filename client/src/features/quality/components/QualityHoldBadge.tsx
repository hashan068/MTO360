import { Badge, Tooltip } from 'antd';
import { StopOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';

interface QualityHoldBadgeProps {
  holdNumber: string;
  reason: string;
  showLabel?: boolean;
}

export const QualityHoldBadge = ({ holdNumber, reason, showLabel = true }: QualityHoldBadgeProps) => {
  return (
    <Tooltip title={`Quality Hold Active: ${reason} (${holdNumber})`}>
      <Link to={`/quality/holds?search=${holdNumber}`} className="inline-flex items-center gap-2">
        <Badge
          count={<StopOutlined style={{ color: '#f5222d' }} />}
          className="flex items-center"
        >
          {showLabel && (
            <span className="text-red-500 font-medium text-sm ml-2">
              QUALITY HOLD
            </span>
          )}
        </Badge>
      </Link>
    </Tooltip>
  );
};

