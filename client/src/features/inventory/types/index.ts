import type { BaseEntity } from '@/shared/types/common';

export interface Component extends BaseEntity {
  name: string;
  description?: string | null;
  quantity: number;
  reorder_level: number;
  reorder_quantity: number;
  unit_of_measure: string;
  supplier_id?: number | null;
  cost: string;
  category_id?: number | null;
}

export type ComponentCreatePayload = Pick<
  Component,
  | 'name'
  | 'description'
  | 'quantity'
  | 'reorder_level'
  | 'reorder_quantity'
  | 'unit_of_measure'
  | 'supplier_id'
  | 'cost'
  | 'category_id'
>;

export type ComponentUpdatePayload = Partial<ComponentCreatePayload>;

export interface Supplier extends BaseEntity {
  name: string;
  email?: string | null;
  address?: string | null;
  website?: string | null;
  is_active: boolean;
  notes?: string | null;
  date_added?: string;
}

export type SupplierCreatePayload = Pick<
  Supplier,
  'name' | 'email' | 'address' | 'website' | 'is_active' | 'notes'
>;

export type SupplierUpdatePayload = Partial<SupplierCreatePayload>;

export type Status = 'PENDING' | 'APPROVED' | 'REJECTED' | 'COMPLETED' | 'CANCELLED';
export type Priority = 'LOW' | 'MEDIUM' | 'HIGH';

export interface PurchaseRequisition extends BaseEntity {
  component_id: number;
  component_name?: string;
  quantity: number;
  status: Status;
  notes?: string | null;
  expected_delivery_date?: string | null;
  priority: Priority;
  user_id?: number | null;
  created_at_date?: string | null;
}

export type PurchaseRequisitionCreatePayload = Pick<
  PurchaseRequisition,
  'component_id' | 'quantity' | 'status' | 'notes' | 'expected_delivery_date' | 'priority'
>;

export type PurchaseRequisitionUpdatePayload = Partial<PurchaseRequisitionCreatePayload>;

export type PurchaseOrderStatus =
  | 'DRAFT'
  | 'PENDING_APPROVAL'
  | 'APPROVED'
  | 'REJECTED'
  | 'SENT'
  | 'RECEIVED'
  | 'CANCELLED';

export interface PurchaseOrder extends BaseEntity {
  purchase_requisition_id: number;
  supplier_id?: number | null;
  status: PurchaseOrderStatus;
  notes?: string | null;
  price_per_unit?: string | null;
  total_price?: string | null;
  creator_id?: number | null;
  purchase_requisition?: Record<string, unknown> | null;
}

export type PurchaseOrderCreatePayload = Pick<
  PurchaseOrder,
  'purchase_requisition_id' | 'supplier_id' | 'status' | 'notes' | 'price_per_unit' | 'total_price'
>;

export type PurchaseOrderUpdatePayload = Partial<PurchaseOrderCreatePayload>;

export interface ReplenishTransaction extends BaseEntity {
  purchase_requisition_id: number;
  component_id: number;
  component_name?: string;
  quantity: number;
  user_id?: number | null;
  user_name?: string | null;
  timestamp: string;
}

export interface ConsumptionTransaction extends BaseEntity {
  material_requisition_item_id: number;
  component_id: number;
  component_name?: string;
  quantity: number;
  user_id?: number | null;
  user_name?: string | null;
  timestamp: string;
}
