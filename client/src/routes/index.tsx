import { lazy, Suspense } from 'react';
import { Navigate, RouteObject, useRoutes } from 'react-router-dom';
import ProtectedRoute from '@/features/auth/routes/ProtectedRoute';
import FullScreenLoader from '@/shared/components/feedback/FullScreenLoader';
import AppLayout from '@/shared/components/layout/AppLayout';
import { inventoryRoutes } from '@/features/inventory/routes';
import { salesRoutes } from '@/features/sales/routes';
import { manufacturingRoutes } from '@/features/manufacturing/routes';
import { qualityRoutes } from '@/features/quality/routes';
import { procurementRoutes } from '@/features/procurement';

const DashboardPage = lazy(() => import('@/features/dashboard/pages/DashboardPage'));
const LoginPage = lazy(() => import('@/features/auth/pages/LoginPage'));
const NotFoundPage = lazy(() => import('@/shared/pages/NotFoundPage'));

const routes: RouteObject[] = [
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <Navigate to="/dashboard" replace /> },
          { path: 'dashboard', element: <DashboardPage /> },
          {
            path: 'inventory',
            children: inventoryRoutes,
          },
          {
            path: 'sales',
            children: salesRoutes,
          },
          {
            path: 'manufacturing',
            children: manufacturingRoutes,
          },
          {
            path: 'procurement',
            children: procurementRoutes,
          },
          {
            path: 'quality',
            children: qualityRoutes,
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
];

const AppRoutes = () => {
  const element = useRoutes(routes);

  return <Suspense fallback={<FullScreenLoader />}>{element}</Suspense>;
};

export default AppRoutes;

