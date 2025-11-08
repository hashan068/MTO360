import api, { createCrudApi } from '@/shared/api/client';
import {
  Customer,
  CustomerCreatePayload,
  CustomerUpdatePayload,
  Product,
  ProductCreatePayload,
  ProductUpdatePayload,
  RFQ,
  RFQCreatePayload,
  RFQUpdatePayload,
  Quotation,
  QuotationCreatePayload,
  QuotationUpdatePayload,
  SalesOrder,
  SalesOrderCreatePayload,
  SalesOrderUpdatePayload,
} from '@/features/sales/types';

export const customersApi = createCrudApi<Customer, CustomerCreatePayload, CustomerUpdatePayload>(
  '/api/sales/customers'
);

export const productsApi = createCrudApi<Product, ProductCreatePayload, ProductUpdatePayload>(
  '/api/sales/products'
);

export const rfqsApi = createCrudApi<RFQ, RFQCreatePayload, RFQUpdatePayload>('/api/sales/rfqs');

export const quotationsApi = createCrudApi<Quotation, QuotationCreatePayload, QuotationUpdatePayload>(
  '/api/sales/quotations'
);

export const salesOrdersApi = createCrudApi<
  SalesOrder,
  SalesOrderCreatePayload,
  SalesOrderUpdatePayload
>('/api/sales/orders');

export async function sendQuotationEmail(quotationId: number): Promise<void> {
  await api.post(`/api/sales/quotations/${quotationId}/send-email`);
}
