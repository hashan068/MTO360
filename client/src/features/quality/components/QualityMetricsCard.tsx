import { Card, Statistic, Skeleton } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import type { ReactNode } from 'react';

interface QualityMetricsCardProps {
  title: string;
  value: number | string;
  prefix?: ReactNode;
  suffix?: ReactNode;
  trend?: number;
  loading?: boolean;
  precision?: number;
  color?: string;
}

export const QualityMetricsCard = ({
  title,
  value,
  prefix,
  suffix,
  trend,
  loading,
  precision,
  color,
}: QualityMetricsCardProps) => {
  return (
    <Card variant="borderless" className="h-full shadow-sm hover:shadow-md transition-shadow">
      <Skeleton loading={loading} active paragraph={{ rows: 1 }}>
        <Statistic
          title={<span className="text-gray-500 font-medium">{title}</span>}
          value={value}
          precision={precision}
          prefix={prefix}
          suffix={suffix}
          valueStyle={{ color: color }}
        />
        {trend !== undefined && (
          <div className={`mt-2 text-sm ${trend >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {trend >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            <span className="ml-1">{Math.abs(trend)}% vs last month</span>
          </div>
        )}
      </Skeleton>
    </Card>
  );
};
