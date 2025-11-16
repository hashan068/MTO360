import type { BaseEntity } from '@/shared/types/common';

export interface Customer extends BaseEntity {
  name: string;
  email: string;
  phone: string;
  street_address: string;
  city: string;
  is_active: boolean;
  notes?: string | null;
}

export type CustomerCreatePayload = Pick<
  Customer,
  'name' | 'email' | 'phone' | 'street_address' | 'city' | 'is_active' | 'notes'
>;

export type CustomerUpdatePayload = Partial<CustomerCreatePayload>;

export type InverterType = 'GRID_TIED' | 'OFF_GRID' | 'HYBRID' | 'MICRO' | 'STRING';

export interface Product extends BaseEntity {
  name: string;
  description: string;
  price: string;
  inverter_type: InverterType;
  power_rating: number;
  frequency: string;
  efficiency: string;
  surge_power: number;
  warranty_years: number;
  input_voltage: string;
  output_voltage: string;
  model_number: string;
  product_name?: string | null;
  bom?: number | null;
}

export type ProductCreatePayload = Pick<
  Product,
  | 'description'
  | 'price'
  | 'inverter_type'
  | 'power_rating'
  | 'frequency'
  | 'efficiency'
  | 'surge_power'
  | 'warranty_years'
  | 'input_voltage'
  | 'output_voltage'
>;

export type ProductUpdatePayload = Partial<ProductCreatePayload> & {
  description?: string;
};

// RFQ Status Enum - aligned with backend RFQStatusEnum
export type RFQStatus = 'draft' | 'sent' | 'cancelled' | 'completed';

export interface RFQItem {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: string;
}

export interface RFQSummary {
  id: number;
  creator_id: number;
  status: RFQStatus;
  due_date?: string | null;
  created_at: string;
}

export interface RFQ extends BaseEntity {
  creator_id: number;
  creator_name?: string | null;
  status: RFQStatus;
  due_date?: string | null;
  description?: string | null;
  items: RFQItem[];
  quotations?: QuotationSummary[];
}

export interface RFQItemCreatePayload {
  product_id: number;
  quantity: number;
  unit_price: string;
}

export interface RFQCreatePayload {
  status?: RFQStatus;
  due_date?: string | null;
  description?: string | null;
  items?: RFQItemCreatePayload[];
}

export type RFQUpdatePayload = Partial<RFQCreatePayload>;

export interface ConvertRFQToQuotationRequest {
  customer_id: number;
  date: string;
  expiration_date: string;
  invoicing_and_shipping_address: string;
}

// Quotation Status Enum - aligned with backend QuotationStatusEnum
export type QuotationStatus =
  | 'quotation'
  | 'quotation_sent'
  | 'accepted'
  | 'rejected'
  | 'cancelled'
  | 'expired';

export interface QuotationItem {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: string;
}

export interface QuotationSummary {
  id: number;
  customer_id: number;
  customer_name?: string | null;
  date: string;
  total_amount: string;
  status: QuotationStatus;
}

export interface EmailHistoryEntry {
  sent_at: string;
  sent_by_user_id: number;
  sent_by_username: string;
  recipient: string;
  count: number;
}

export interface Quotation extends BaseEntity {
  customer_id: number;
  customer_name?: string | null;
  rfq_id?: number | null;
  rfq_reference?: RFQSummary | null;
  date: string;
  expiration_date: string;
  invoicing_and_shipping_address: string;
  total_amount: string;
  status: QuotationStatus;
  is_expired: boolean;
  can_edit: boolean;
  created_by_id: number;
  email_sent_at?: string | null;
  email_sent_count: number;
  email_history?: EmailHistoryEntry[] | null;
  quotation_items: QuotationItem[];
  sales_orders?: SalesOrderSummary[];
}

export interface QuotationItemCreatePayload {
  product_id: number;
  quantity: number;
  unit_price: string;
}

export interface QuotationCreatePayload {
  customer_id: number;
  date: string;
  expiration_date: string;
  invoicing_and_shipping_address: string;
  quotation_items: QuotationItemCreatePayload[];
  status?: QuotationStatus;
}

export type QuotationUpdatePayload = Partial<QuotationCreatePayload>;

export interface QuotationStatusUpdatePayload {
  status: QuotationStatus;
}

// Sales Order Status Enum - aligned with backend SalesOrderStatusEnum
export type SalesOrderStatus =
  | 'pending'
  | 'confirmed'
  | 'processing'
  | 'in_production'
  | 'ready_for_delivery'
  | 'cancelled'
  | 'delivered';

export interface SalesOrderItem {
  id: number;
  sales_order_item_id?: number | null;
  product_id: number;
  product_name?: string | null;
  quantity: number;
  price: string;
}

export interface SalesOrderSummary {
  id: number;
  customer_id: number;
  customer_name?: string | null;
  total_amount: string;
  status: SalesOrderStatus;
  created_at: string;
}

export interface SalesOrder extends BaseEntity {
  customer_id: number;
  customer_name?: string | null;
  quotation_id?: number | null;
  quotation_reference?: QuotationSummary | null;
  rfq_reference?: RFQSummary | null;
  total_amount: string;
  status: SalesOrderStatus;
  can_edit: boolean;
  delivery_date?: string | null;
  created_at_date?: string | null;
  order_items: SalesOrderItem[];
}

export interface SalesOrderItemCreatePayload {
  product_id: number;
  quantity: number;
  price: string;
}

export interface SalesOrderCreatePayload {
  customer_id: number;
  order_items: SalesOrderItemCreatePayload[];
}

export type SalesOrderUpdatePayload = Partial<SalesOrderCreatePayload> & {
  status?: SalesOrderStatus;
};

export interface SalesOrderStatusUpdatePayload {
  status: SalesOrderStatus;
  notes?: string | null;
}
