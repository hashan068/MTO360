import { Breadcrumb } from 'antd';
import { Link } from 'react-router-dom';
import { HomeOutlined } from '@ant-design/icons';
import type { RFQSummary, QuotationSummary, SalesOrderSummary } from '@/features/sales/types';

interface DocumentBreadcrumbProps {
  rfq?: RFQSummary | null;
  quotation?: QuotationSummary | null;
  salesOrder?: SalesOrderSummary | null;
  currentPage: 'rfq' | 'quotation' | 'sales_order';
}

export const DocumentBreadcrumb = ({ rfq, quotation, salesOrder, currentPage }: DocumentBreadcrumbProps) => {
  const items = [
    {
      title: (
        <Link to="/sales">
          <HomeOutlined /> Sales
        </Link>
      ),
    },
  ];

  // Add RFQ breadcrumb if available
  if (rfq) {
    items.push({
      title: currentPage === 'rfq' ? (
        `RFQ #${rfq.id}`
      ) : (
        <Link to={`/sales/rfqs/${rfq.id}`}>RFQ #{rfq.id}</Link>
      ),
    });
  }

  // Add Quotation breadcrumb if available
  if (quotation) {
    items.push({
      title: currentPage === 'quotation' ? (
        `Quotation #${quotation.id}`
      ) : (
        <Link to={`/sales/quotations/${quotation.id}`}>Quotation #{quotation.id}</Link>
      ),
    });
  }

  // Add Sales Order breadcrumb if available
  if (salesOrder) {
    items.push({
      title: currentPage === 'sales_order' ? (
        `Sales Order #${salesOrder.id}`
      ) : (
        <Link to={`/sales/orders/${salesOrder.id}`}>Sales Order #{salesOrder.id}</Link>
      ),
    });
  }

  return <Breadcrumb items={items} style={{ marginBottom: 16 }} />;
};

