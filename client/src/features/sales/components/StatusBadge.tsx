import { Tag } from 'antd';
import type { RFQStatus, QuotationStatus, SalesOrderStatus } from '@/features/sales/types';

type StatusType = RFQStatus | QuotationStatus | SalesOrderStatus;

interface StatusBadgeProps {
  status: StatusType;
  isExpired?: boolean;
}

// Color mappings for each status type
const rfqStatusColors: Record<RFQStatus, string> = {
  draft: 'default',
  sent: 'blue',
  cancelled: 'red',
  completed: 'green',
};

const quotationStatusColors: Record<QuotationStatus, string> = {
  quotation: 'blue',
  quotation_sent: 'cyan',
  accepted: 'green',
  rejected: 'red',
  cancelled: 'volcano',
  expired: 'default',
};

const salesOrderStatusColors: Record<SalesOrderStatus, string> = {
  pending: 'default',
  confirmed: 'blue',
  processing: 'cyan',
  in_production: 'geekblue',
  ready_for_delivery: 'purple',
  cancelled: 'red',
  delivered: 'green',
};

// Status label formatting
const formatStatusLabel = (status: StatusType): string => {
  return status
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const getStatusColor = (status: StatusType): string => {
  // Check which status type it is and return appropriate color
  if (status in rfqStatusColors) {
    return rfqStatusColors[status as RFQStatus];
  }
  if (status in quotationStatusColors) {
    return quotationStatusColors[status as QuotationStatus];
  }
  if (status in salesOrderStatusColors) {
    return salesOrderStatusColors[status as SalesOrderStatus];
  }
  return 'default';
};

export const StatusBadge = ({ status, isExpired = false }: StatusBadgeProps) => {
  const color = getStatusColor(status);
  const label = formatStatusLabel(status);

  // Show expired indicator for quotations
  if (isExpired && (status === 'quotation' || status === 'quotation_sent')) {
    return (
      <Tag color="orange" style={{ fontWeight: 500 }}>
        {label} (Expired)
      </Tag>
    );
  }

  return (
    <Tag color={color} style={{ fontWeight: 500 }}>
      {label}
    </Tag>
  );
};
