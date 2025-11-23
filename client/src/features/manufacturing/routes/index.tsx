import { lazy } from 'react';
import { RouteObject } from 'react-router-dom';

const ManufacturingDashboardPage = lazy(() => import('@/features/manufacturing/pages/ManufacturingDashboardPage'));
const BillOfMaterialsPage = lazy(() => import('@/features/manufacturing/pages/BillOfMaterialsPage'));
const ManufacturingOrdersPage = lazy(() => import('@/features/manufacturing/pages/ManufacturingOrdersPage'));
const MaterialRequisitionsPage = lazy(() => import('@/features/manufacturing/pages/MaterialRequisitionsPage'));

// Production Scheduling & Shop Floor
const WorkCentersPage = lazy(() => import('@/features/manufacturing/work-centers/pages/WorkCentersPage'));
const OperationRoutesPage = lazy(() => import('@/features/manufacturing/operation-routes/pages/OperationRoutesPage'));
const OperationRouteDetailPage = lazy(() => import('@/features/manufacturing/operation-routes/pages/OperationRouteDetailPage'));
const SchedulerPage = lazy(() => import('@/features/manufacturing/scheduler/pages/SchedulerPage'));
const ShopFloorPage = lazy(() => import('@/features/manufacturing/shop-floor/pages/ShopFloorPage'));
const AnalyticsPage = lazy(() => import('@/features/manufacturing/analytics/pages/AnalyticsPage'));

export const manufacturingRoutes: RouteObject[] = [
  { index: true, element: <ManufacturingDashboardPage /> },
  { path: 'boms', element: <BillOfMaterialsPage /> },
  { path: 'orders', element: <ManufacturingOrdersPage /> },
  { path: 'material-requisitions', element: <MaterialRequisitionsPage /> },

  // Production Scheduling & Shop Floor
  { path: 'work-centers', element: <WorkCentersPage /> },
  {
    path: 'operation-routes',
    children: [
      { index: true, element: <OperationRoutesPage /> },
      { path: ':id', element: <OperationRouteDetailPage /> },
    ],
  },
  { path: 'scheduler', element: <SchedulerPage /> },
  { path: 'shop-floor', element: <ShopFloorPage /> },
  { path: 'analytics', element: <AnalyticsPage /> },
];
