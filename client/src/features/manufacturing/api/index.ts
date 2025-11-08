import api, { createCrudApi } from '@/shared/api/client';
import {
  BillOfMaterial,
  BillOfMaterialCreatePayload,
  BillOfMaterialUpdatePayload,
  ManufacturingOrder,
  ManufacturingOrderCreatePayload,
  ManufacturingOrderUpdatePayload,
  MaterialRequisition,
  MaterialRequisitionCreatePayload,
  MaterialRequisitionUpdatePayload,
} from '@/features/manufacturing/types';

export const billOfMaterialsApi = createCrudApi<
  BillOfMaterial,
  BillOfMaterialCreatePayload,
  BillOfMaterialUpdatePayload
>('/api/manufacturing/boms');

export const manufacturingOrdersApi = createCrudApi<
  ManufacturingOrder,
  ManufacturingOrderCreatePayload,
  ManufacturingOrderUpdatePayload
>('/api/manufacturing/orders');

export const materialRequisitionsApi = createCrudApi<
  MaterialRequisition,
  MaterialRequisitionCreatePayload,
  MaterialRequisitionUpdatePayload
>('/api/manufacturing/material-requisitions');

export async function startManufacturing(orderId: number): Promise<ManufacturingOrder> {
  const { data } = await api.post<ManufacturingOrder>(`/api/manufacturing/orders/${orderId}/start`);
  return data;
}

export async function completeManufacturing(orderId: number): Promise<ManufacturingOrder> {
  const { data } = await api.post<ManufacturingOrder>(`/api/manufacturing/orders/${orderId}/complete`);
  return data;
}
