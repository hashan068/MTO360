import type { BaseEntity } from '@/shared/types/common';

export interface BillOfMaterialItem {
  id: number;
  component_id?: number | null;
  component_name?: string | null;
  quantity: number;
}

export interface BillOfMaterial extends BaseEntity {
  name: string;
  product_id?: number | null;
  product_name?: string | null;
  bom_items: BillOfMaterialItem[];
}

export interface BillOfMaterialItemCreatePayload {
  component_id?: number | null;
  quantity: number;
}

export interface BillOfMaterialCreatePayload {
  name: string;
  product_id?: number | null;
  bom_items?: BillOfMaterialItemCreatePayload[];
}

export type BillOfMaterialUpdatePayload = Partial<BillOfMaterialCreatePayload>;

export type ManufacturingOrderStatus =
  | 'PENDING'
  | 'PLANNED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED';

export interface ManufacturingOrder extends BaseEntity {
  sales_order_item_id?: number | null;
  product_id?: number | null;
  product_name?: string | null;
  quantity: number;
  bom_id?: number | null;
  status: ManufacturingOrderStatus;
  creator_id?: number | null;
  created_at_date?: string | null;
  end_at?: string | null;
  production_start_at?: string | null;
  estimated_mfg_lead_time?: string | null;
  mfg_lead_time?: string | null;
  production_lead_time?: string | null;
}

export interface ManufacturingOrderCreatePayload {
  product_id?: number | null;
  sales_order_item_id?: number | null;
  quantity: number;
}

export type ManufacturingOrderUpdatePayload = Partial<ManufacturingOrderCreatePayload> & {
  status?: ManufacturingOrderStatus;
};

export type MaterialRequisitionStatus =
  | 'PENDING'
  | 'APPROVED'
  | 'REJECTED'
  | 'FULFILLED'
  | 'CANCELLED';

export type MaterialRequisitionItemStatus =
  | 'PENDING'
  | 'ALLOCATED'
  | 'PICKED'
  | 'CONSUMED'
  | 'RETURNED';

export interface MaterialRequisitionItem {
  id: number;
  component_id: number;
  component_name?: string | null;
  quantity: number;
  status: MaterialRequisitionItemStatus;
}

export interface MaterialRequisition extends BaseEntity {
  manufacturing_order_id: number;
  bom_id?: number | null;
  status: MaterialRequisitionStatus;
  created_at_date?: string | null;
  items: MaterialRequisitionItem[];
}

export interface MaterialRequisitionCreatePayload {
  manufacturing_order_id: number;
  bom_id?: number | null;
}

export type MaterialRequisitionUpdatePayload = Partial<MaterialRequisitionCreatePayload> & {
  status?: MaterialRequisitionStatus;
};
