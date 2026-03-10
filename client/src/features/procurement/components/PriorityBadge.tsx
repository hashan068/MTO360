/**
 * Priority Badge Component for inventory urgency levels
 */
import { Tag } from 'antd';
import { AlertOutlined } from '@ant-design/icons';

interface PriorityBadgeProps {
  priority: 'high' | 'medium' | 'low';
}

export const PriorityBadge = ({ priority }: PriorityBadgeProps) => {
  const config = {
    high: { color: 'error', text: 'Urgent', icon: <AlertOutlined /> },
    medium: { color: 'warning', text: 'Medium', icon: null },
    low: { color: 'default', text: 'Low', icon: null },
  };

  const { color, text, icon } = config[priority];

  return (
    <Tag color={color} icon={icon}>
      {text}
    </Tag>
  );
};
