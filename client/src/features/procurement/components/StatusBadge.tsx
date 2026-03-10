/**
 * Status Badge Component for Procurement module
 */
import { Tag } from 'antd';
import type { RFQStatus, QuoteStatus, ContractStatus } from '../types';

interface StatusBadgeProps {
  status: RFQStatus | QuoteStatus | ContractStatus | string;
  type?: 'rfq' | 'quote' | 'contract';
}

export const ProcurementStatusBadge = ({ status, type = 'rfq' }: StatusBadgeProps) => {
  const getStatusConfig = () => {
    const statusStr = status.toString().toLowerCase();

    // RFQ Status
    if (type === 'rfq') {
      switch (statusStr) {
        case 'draft':
          return { color: 'default', text: 'Draft' };
        case 'sent':
          return { color: 'processing', text: 'Sent' };
        case 'quotes_received':
          return { color: 'cyan', text: 'Quotes Received' };
        case 'awarded':
          return { color: 'success', text: 'Awarded' };
        case 'cancelled':
          return { color: 'error', text: 'Cancelled' };
        default:
          return { color: 'default', text: status };
      }
    }

    // Quote Status
    if (type === 'quote') {
      switch (statusStr) {
        case 'pending':
          return { color: 'warning', text: 'Pending' };
        case 'submitted':
          return { color: 'processing', text: 'Submitted' };
        case 'accepted':
          return { color: 'success', text: 'Accepted' };
        case 'rejected':
          return { color: 'error', text: 'Rejected' };
        default:
          return { color: 'default', text: status };
      }
    }

    // Contract Status
    if (type === 'contract') {
      switch (statusStr) {
        case 'draft':
          return { color: 'default', text: 'Draft' };
        case 'active':
          return { color: 'success', text: 'Active' };
        case 'expired':
          return { color: 'warning', text: 'Expired' };
        case 'cancelled':
          return { color: 'error', text: 'Cancelled' };
        default:
          return { color: 'default', text: status };
      }
    }

    return { color: 'default', text: status };
  };

  const { color, text } = getStatusConfig();

  return <Tag color={color}>{text}</Tag>;
};
