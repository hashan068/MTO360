/**
 * Procurement Module Routes Configuration
 */
import { lazy } from 'react';
import type { RouteObject } from 'react-router-dom';

// Lazy load all procurement pages
const ProcurementDashboardPage = lazy(() => import('./pages/ProcurementDashboardPage'));
const SupplierRankingsPage = lazy(() => import('./pages/SupplierRankingsPage'));
const RFQListPage = lazy(() => import('./pages/RFQListPage'));
const CreateRFQPage = lazy(() => import('./pages/CreateRFQPage'));
const QuoteComparisonPage = lazy(() => import('./pages/QuoteComparisonPage'));
const ContractListPage = lazy(() => import('./pages/ContractListPage'));
const InventoryOptimizationPage = lazy(() => import('./pages/InventoryOptimizationPage'));
const ABCAnalysisPage = lazy(() => import('./pages/ABCAnalysisPage'));
const CostAnalysisPage = lazy(() => import('./pages/CostAnalysisPage'));
const BudgetTrackingPage = lazy(() => import('./pages/BudgetTrackingPage'));

export const procurementRoutes: RouteObject[] = [
  {
    index: true,
    element: <ProcurementDashboardPage />,
  },
  // Phase 1: Supplier Performance
  {
    path: 'suppliers/rankings',
    element: <SupplierRankingsPage />,
  },
  // Phase 2: RFQ & Competitive Bidding
  {
    path: 'rfqs',
    element: <RFQListPage />,
  },
  {
    path: 'rfqs/create',
    element: <CreateRFQPage />,
  },
  {
    path: 'rfqs/:rfqId/compare',
    element: <QuoteComparisonPage />,
  },
  // Phase 3: Contract Management
  {
    path: 'contracts',
    element: <ContractListPage />,
  },
  // Phase 4: Inventory Optimization
  {
    path: 'inventory/below-rop',
    element: <InventoryOptimizationPage />,
  },
  {
    path: 'inventory/abc-analysis',
    element: <ABCAnalysisPage />,
  },
  // Phase 5: Cost Analysis & Reporting
  {
    path: 'cost-analysis',
    element: <CostAnalysisPage />,
  },
  {
    path: 'budgets/:fiscalYear',
    element: <BudgetTrackingPage />,
  },
];

