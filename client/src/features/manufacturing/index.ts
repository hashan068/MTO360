/**
 * Manufacturing Module Exports
 * Centralized exports for manufacturing feature
 */

// Work Centers
export { WorkCenterList } from './work-centers/components/WorkCenterList';
export { WorkCenterForm } from './work-centers/components/WorkCenterForm';
export { WorkCentersPage } from './work-centers/pages/WorkCentersPage';
export {
  useWorkCenters,
  useWorkCenter,
  useCreateWorkCenter,
  useUpdateWorkCenter,
  useDeleteWorkCenter,
} from './work-centers/hooks/useWorkCenters';

// Operation Routes
export { OperationRouteList } from './operation-routes/components/OperationRouteList';
export { OperationRouteForm } from './operation-routes/components/OperationRouteForm';
export { RouteOperationsList } from './operation-routes/components/RouteOperationsList';
export { OperationRoutesPage } from './operation-routes/pages/OperationRoutesPage';
export { OperationRouteDetailPage } from './operation-routes/pages/OperationRouteDetailPage';
export {
  useOperationRoutes,
  useOperationRoute,
  useRouteOperations,
  useCreateOperationRoute,
  useUpdateOperationRoute,
  useDeleteOperationRoute,
  useCopyOperationRoute,
  useAddRouteOperation,
  useUpdateRouteOperation,
  useDeleteRouteOperation,
} from './operation-routes/hooks/useOperationRoutes';

// API
export { manufacturingApi } from './api/manufacturingApi';
