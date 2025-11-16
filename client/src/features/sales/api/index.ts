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
  QuotationStatusUpdatePayload,
  SalesOrder,
  SalesOrderCreatePayload,
  SalesOrderUpdatePayload,
  SalesOrderStatusUpdatePayload,
  ConvertRFQToQuotationRequest,
  QuotationSummary,
  RFQStatus,
  QuotationStatus,
  SalesOrderStatus,
} from '@/features/sales/types';

export const customersApi = createCrudApi<Customer, CustomerCreatePayload, CustomerUpdatePayload>(
  '/api/sales/customers'
);

export const productsApi = createCrudApi<Product, ProductCreatePayload, ProductUpdatePayload>(
  '/api/sales/products'
);

// RFQ API with enhanced filtering
export const rfqsApi = {
  ...createCrudApi<RFQ, RFQCreatePayload, RFQUpdatePayload>('/api/sales/rfqs'),
  
  /**
   * List RFQs with optional filtering and search
   * @param params - Query parameters for filtering (status, search)
   */
  async list(params?: { status?: RFQStatus; search?: string; skip?: number; limit?: number }): Promise<RFQ[]> {
    const { data } = await api.get<RFQ[]>('/api/sales/rfqs/', { params });
    return data;
  },
  
  /**
   * Convert an RFQ to a Quotation
   * @param rfqId - The ID of the RFQ to convert
   * @param payload - Quotation details (customer, dates, address)
   */
  async convertToQuotation(rfqId: number, payload: ConvertRFQToQuotationRequest): Promise<Quotation> {
    const { data } = await api.post<Quotation>(`/api/sales/rfqs/${rfqId}/convert`, payload);
    return data;
  },
  
  /**
   * Get all quotations created from a specific RFQ
   * @param rfqId - The ID of the RFQ
   */
  async getQuotations(rfqId: number): Promise<QuotationSummary[]> {
    const { data } = await api.get<QuotationSummary[]>(`/api/sales/rfqs/${rfqId}/quotations`);
    return data;
  },
};

// Quotation API with enhanced filtering and status management
export const quotationsApi = {
  ...createCrudApi<Quotation, QuotationCreatePayload, QuotationUpdatePayload>('/api/sales/quotations'),
  
  /**
   * List quotations with optional filtering and search
   * @param params - Query parameters for filtering (status, search)
   */
  async list(params?: { status?: QuotationStatus; search?: string; skip?: number; limit?: number }): Promise<Quotation[]> {
    const { data } = await api.get<Quotation[]>('/api/sales/quotations/', { params });
    return data;
  },
  
  /**
   * Update quotation status
   * @param quotationId - The ID of the quotation
   * @param payload - New status
   */
  async updateStatus(quotationId: number, payload: QuotationStatusUpdatePayload): Promise<Quotation> {
    const { data } = await api.put<Quotation>(`/api/sales/quotations/${quotationId}/status`, payload);
    return data;
  },
  
  /**
   * Convert a quotation to a sales order
   * @param quotationId - The ID of the quotation to convert
   */
  async convertToSalesOrder(quotationId: number): Promise<SalesOrder> {
    const { data } = await api.post<SalesOrder>(`/api/sales/quotations/${quotationId}/convert`);
    return data;
  },
};

// Sales Order API with enhanced filtering and status management
export const salesOrdersApi = {
  ...createCrudApi<SalesOrder, SalesOrderCreatePayload, SalesOrderUpdatePayload>('/api/sales/orders'),
  
  /**
   * List sales orders with optional filtering and search
   * @param params - Query parameters for filtering (status, date_from, date_to, search)
   */
  async list(params?: { 
    status?: SalesOrderStatus; 
    date_from?: string; 
    date_to?: string; 
    search?: string; 
    skip?: number; 
    limit?: number;
  }): Promise<SalesOrder[]> {
    const { data } = await api.get<SalesOrder[]>('/api/sales/orders/', { params });
    return data;
  },
  
  /**
   * Update sales order status
   * @param orderId - The ID of the sales order
   * @param payload - New status and optional notes
   */
  async updateStatus(orderId: number, payload: SalesOrderStatusUpdatePayload): Promise<SalesOrder> {
    const { data } = await api.put<SalesOrder>(`/api/sales/orders/${orderId}/status`, payload);
    return data;
  },
};

export async function sendQuotationEmail(quotationId: number): Promise<Quotation> {
  const { data } = await api.post<Quotation>(`/api/sales/quotations/${quotationId}/send-email`);
  return data;
}
