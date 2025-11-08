import api, { createCrudApi } from '@/shared/api/client';
import {
  Component,
  ComponentCreatePayload,
  ComponentUpdatePayload,
  Supplier,
  SupplierCreatePayload,
  SupplierUpdatePayload,
  PurchaseRequisition,
  PurchaseRequisitionCreatePayload,
  PurchaseRequisitionUpdatePayload,
  PurchaseOrder,
  PurchaseOrderCreatePayload,
  PurchaseOrderUpdatePayload,
  ReplenishTransaction,
  ConsumptionTransaction,
} from '@/features/inventory/types';

export const componentsApi = createCrudApi<Component, ComponentCreatePayload, ComponentUpdatePayload>(
  '/api/inventory/components'
);

export const suppliersApi = createCrudApi<Supplier, SupplierCreatePayload, SupplierUpdatePayload>(
  '/api/inventory/suppliers'
);

export const purchaseRequisitionsApi = createCrudApi<
  PurchaseRequisition,
  PurchaseRequisitionCreatePayload,
  PurchaseRequisitionUpdatePayload
>('/api/inventory/purchase-requisitions');

export const purchaseOrdersApi = createCrudApi<
  PurchaseOrder,
  PurchaseOrderCreatePayload,
  PurchaseOrderUpdatePayload
>('/api/inventory/purchase-orders');

export const replenishTransactionsApi = createCrudApi<ReplenishTransaction, ReplenishTransaction, Partial<ReplenishTransaction>>(
  '/api/inventory/replenish-transactions'
);

export const consumptionTransactionsApi = createCrudApi<
  ConsumptionTransaction,
  ConsumptionTransaction,
  Partial<ConsumptionTransaction>
>('/api/inventory/consumption-transactions');

export async function downloadInventoryReport(): Promise<Blob> {
  const response = await api.get('/api/inventory/reports/export', {
    responseType: 'blob',
  });
  return response.data;
}
