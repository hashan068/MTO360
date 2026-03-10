import { lazy } from 'react';
import { RouteObject } from 'react-router-dom';

const InventoryDashboardPage = lazy(() => import('@/features/inventory/pages/InventoryDashboardPage'));
const ComponentsPage = lazy(() => import('@/features/inventory/pages/ComponentsPage'));
const ComponentFormPage = lazy(() => import('@/features/inventory/pages/ComponentFormPage'));
const PurchaseRequisitionsPage = lazy(() => import('@/features/inventory/pages/PurchaseRequisitionsPage'));
const PurchaseOrdersPage = lazy(() => import('@/features/inventory/pages/PurchaseOrdersPage'));
const SuppliersPage = lazy(() => import('@/features/inventory/pages/SuppliersPage'));
const InventoryReportsPage = lazy(() => import('@/features/inventory/pages/InventoryReportsPage'));

export const inventoryRoutes: RouteObject[] = [
  { index: true, element: <InventoryDashboardPage /> },
  { path: 'components', element: <ComponentsPage /> },
  { path: 'components/new', element: <ComponentFormPage /> },
  { path: 'components/:id', element: <ComponentFormPage /> },
  { path: 'purchase-requisitions', element: <PurchaseRequisitionsPage /> },
  { path: 'purchase-orders', element: <PurchaseOrdersPage /> },
  { path: 'suppliers', element: <SuppliersPage /> },
  { path: 'reports', element: <InventoryReportsPage /> },
];

