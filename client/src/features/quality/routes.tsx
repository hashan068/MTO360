import { lazy } from 'react';
import { RouteObject } from 'react-router-dom';

// Lazy load pages
const QualityDashboardPage = lazy(() => import('./pages/QualityDashboardPage'));
const InspectorDashboardPage = lazy(() => import('./pages/InspectorDashboardPage'));
const DefectManagementPage = lazy(() => import('./pages/DefectManagementPage'));
const DefectDetailPage = lazy(() => import('./pages/DefectDetailPage'));
const NCRManagementPage = lazy(() => import('./pages/NCRManagementPage'));
const NCRDetailPage = lazy(() => import('./pages/NCRDetailPage'));
const InspectionManagementPage = lazy(() => import('./pages/InspectionManagementPage'));
const CAPAManagementPage = lazy(() => import('./pages/CAPAManagementPage'));
const CAPADetailPage = lazy(() => import('./pages/CAPADetailPage'));
const ReworkQueuePage = lazy(() => import('./pages/ReworkQueuePage'));
const QualityHoldDetailPage = lazy(() => import('./pages/QualityHoldDetailPage'));
const QualityAnalyticsPage = lazy(() => import('./pages/QualityAnalyticsPage'));

export const qualityRoutes: RouteObject[] = [
  {
    path: 'dashboard',
    element: <QualityDashboardPage />,
  },
  {
    path: 'inspector',
    element: <InspectorDashboardPage />,
  },
  {
    path: 'defects',
    element: <DefectManagementPage />,
  },
  {
    path: 'defects/:id',
    element: <DefectDetailPage />,
  },
  {
    path: 'ncrs',
    element: <NCRManagementPage />,
  },
  {
    path: 'ncrs/:id',
    element: <NCRDetailPage />,
  },
  {
    path: 'capas',
    element: <CAPAManagementPage />,
  },
  {
    path: 'capas/:id',
    element: <CAPADetailPage />,
  },
  {
    path: 'rework',
    element: <ReworkQueuePage />,
  },
  {
    path: 'holds/:id',
    element: <QualityHoldDetailPage />,
  },
  {
    path: 'analytics',
    element: <QualityAnalyticsPage />,
  },
  {
    path: 'inspections/points',
    element: <InspectionManagementPage />,
  },
  // Redirect /quality to /quality/dashboard
  {
    path: '',
    element: <QualityDashboardPage />,
  },
];

