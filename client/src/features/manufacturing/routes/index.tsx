import { lazy } from 'react';
import { RouteObject } from 'react-router-dom';

const ManufacturingDashboardPage = lazy(() => import('@/features/manufacturing/pages/ManufacturingDashboardPage'));
const BillOfMaterialsPage = lazy(() => import('@/features/manufacturing/pages/BillOfMaterialsPage'));
const ManufacturingOrdersPage = lazy(() => import('@/features/manufacturing/pages/ManufacturingOrdersPage'));
const MaterialRequisitionsPage = lazy(() => import('@/features/manufacturing/pages/MaterialRequisitionsPage'));

export const manufacturingRoutes: RouteObject[] = [
  { index: true, element: <ManufacturingDashboardPage /> },
  { path: 'boms', element: <BillOfMaterialsPage /> },
  { path: 'orders', element: <ManufacturingOrdersPage /> },
  { path: 'material-requisitions', element: <MaterialRequisitionsPage /> },
];
