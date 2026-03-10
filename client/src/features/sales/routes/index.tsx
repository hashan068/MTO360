import { lazy } from 'react';
import { RouteObject } from 'react-router-dom';

const SalesDashboardPage = lazy(() => import('@/features/sales/pages/SalesDashboardPage'));
const CustomersPage = lazy(() => import('@/features/sales/pages/CustomersPage'));
const ProductsPage = lazy(() => import('@/features/sales/pages/ProductsPage'));
const RfqsPage = lazy(() => import('@/features/sales/pages/RfqsPage'));
const RfqDetailPage = lazy(() => import('@/features/sales/pages/RfqDetailPage'));
const RfqCreatePage = lazy(() => import('@/features/sales/pages/RfqCreatePage'));
const QuotationsPage = lazy(() => import('@/features/sales/pages/QuotationsPage'));
const QuotationDetailPage = lazy(() => import('@/features/sales/pages/QuotationDetailPage'));
const QuotationCreatePage = lazy(() => import('@/features/sales/pages/QuotationCreatePage'));
const SalesOrdersPage = lazy(() => import('@/features/sales/pages/SalesOrdersPage'));
const SalesOrderDetailPage = lazy(() => import('@/features/sales/pages/SalesOrderDetailPage'));

export const salesRoutes: RouteObject[] = [
  { index: true, element: <SalesDashboardPage /> },
  { path: 'customers', element: <CustomersPage /> },
  { path: 'products', element: <ProductsPage /> },
  { path: 'rfqs', element: <RfqsPage /> },
  { path: 'rfqs/new', element: <RfqCreatePage /> },
  { path: 'rfqs/:id', element: <RfqDetailPage /> },
  { path: 'quotations', element: <QuotationsPage /> },
  { path: 'quotations/new', element: <QuotationCreatePage /> },
  { path: 'quotations/:id', element: <QuotationDetailPage /> },
  { path: 'orders', element: <SalesOrdersPage /> },
  { path: 'orders/:id', element: <SalesOrderDetailPage /> },
];

