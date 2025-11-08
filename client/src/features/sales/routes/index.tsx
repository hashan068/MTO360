import { lazy } from 'react';
import { RouteObject } from 'react-router-dom';

const SalesDashboardPage = lazy(() => import('@/features/sales/pages/SalesDashboardPage'));
const CustomersPage = lazy(() => import('@/features/sales/pages/CustomersPage'));
const ProductsPage = lazy(() => import('@/features/sales/pages/ProductsPage'));
const RfqsPage = lazy(() => import('@/features/sales/pages/RfqsPage'));
const QuotationsPage = lazy(() => import('@/features/sales/pages/QuotationsPage'));
const SalesOrdersPage = lazy(() => import('@/features/sales/pages/SalesOrdersPage'));

export const salesRoutes: RouteObject[] = [
  { index: true, element: <SalesDashboardPage /> },
  { path: 'customers', element: <CustomersPage /> },
  { path: 'products', element: <ProductsPage /> },
  { path: 'rfqs', element: <RfqsPage /> },
  { path: 'quotations', element: <QuotationsPage /> },
  { path: 'orders', element: <SalesOrdersPage /> },
];
