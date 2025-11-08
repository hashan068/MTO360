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

export type RFQStatus = 'DRAFT' | 'OPEN' | 'REVIEW' | 'APPROVED' | 'REJECTED' | 'CLOSED';

export interface RFQItem {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: string;
}

export interface RFQ extends BaseEntity {
  creator_id: number;
  status: RFQStatus;
  due_date?: string | null;
  description?: string | null;
  items: RFQItem[];
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

export type QuotationStatus =
  | 'QUOTATION'
  | 'NEGOTIATION'
  | 'APPROVED'
  | 'REJECTED'
  | 'EXPIRED'
  | 'CONVERTED';

export interface QuotationItem {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: string;
}

export interface Quotation extends BaseEntity {
  customer_id: number;
  customer_name?: string | null;
  date: string;
  expiration_date: string;
  invoicing_and_shipping_address: string;
  total_amount: string;
  status: QuotationStatus;
  created_by_id: number;
  quotation_items: QuotationItem[];
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

export type SalesOrderStatus = 'PENDING' | 'PROCESSING' | 'FULFILLED' | 'CANCELLED';

export interface SalesOrderItem {
  id: number;
  product_id: number;
  product_name?: string | null;
  quantity: number;
  price: string;
}

export interface SalesOrder extends BaseEntity {
  customer_id: number;
  customer_name?: string | null;
  total_amount: string;
  status: SalesOrderStatus;
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
