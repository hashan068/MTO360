import { Link } from 'react-router-dom';
import { FileTextOutlined } from '@ant-design/icons';
import { Typography } from 'antd';

type DocumentType = 'rfq' | 'quotation' | 'sales_order';

interface DocumentLinkProps {
  type: DocumentType;
  id: number;
  label?: string;
}

const documentTypeLabels: Record<DocumentType, string> = {
  rfq: 'RFQ',
  quotation: 'Quotation',
  sales_order: 'Sales Order',
};

const documentTypePaths: Record<DocumentType, string> = {
  rfq: '/sales/rfqs',
  quotation: '/sales/quotations',
  sales_order: '/sales/orders',
};

export const DocumentLink = ({ type, id, label }: DocumentLinkProps) => {
  const displayLabel = label || `${documentTypeLabels[type]} #${id}`;
  const path = `${documentTypePaths[type]}/${id}`;

  return (
    <Link to={path} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
      <FileTextOutlined />
      <Typography.Text style={{ color: 'inherit' }}>{displayLabel}</Typography.Text>
    </Link>
  );
};
