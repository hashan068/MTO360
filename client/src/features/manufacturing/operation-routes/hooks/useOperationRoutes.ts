/**
 * Operation Route React Query Hooks
 * Custom hooks for operation route data fetching and mutations
 */
import { useQuery, useMutation, useQueryClient, type UseQueryResult } from '@tanstack/react-query';
import { message } from 'antd';
import { manufacturingApi } from '../../api/manufacturingApi';
import type { OperationRoute, OperationRouteCreate, RouteOperation, RouteOperationCreate } from '@/types/manufacturing';

// Query Keys
export const operationRouteKeys = {
  all: ['operationRoutes'] as const,
  detail: (id: number) => ['operationRoutes', id] as const,
  operations: (routeId: number) => ['operationRoutes', routeId, 'operations'] as const,
};

/**
 * Fetch all operation routes
 */
export const useOperationRoutes = (): UseQueryResult<OperationRoute[], Error> => {
  return useQuery({
    queryKey: operationRouteKeys.all,
    queryFn: () => manufacturingApi.operationRoutes.getAll(),
  });
};

/**
 * Fetch single operation route by ID
 */
export const useOperationRoute = (id: number): UseQueryResult<OperationRoute, Error> => {
  return useQuery({
    queryKey: operationRouteKeys.detail(id),
    queryFn: () => manufacturingApi.operationRoutes.getById(id),
    enabled: !!id,
  });
};

/**
 * Fetch route operations
 */
export const useRouteOperations = (routeId: number): UseQueryResult<RouteOperation[], Error> => {
  return useQuery({
    queryKey: operationRouteKeys.operations(routeId),
    queryFn: () => manufacturingApi.operationRoutes.getOperations(routeId),
    enabled: !!routeId,
  });
};

/**
 * Create new operation route
 */
export const useCreateOperationRoute = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: OperationRouteCreate) => manufacturingApi.operationRoutes.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: operationRouteKeys.all });
      message.success('Operation route created successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to create operation route');
    },
  });
};

/**
 * Update existing operation route
 */
export const useUpdateOperationRoute = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<OperationRouteCreate> }) =>
      manufacturingApi.operationRoutes.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: operationRouteKeys.all });
      queryClient.invalidateQueries({ queryKey: operationRouteKeys.detail(variables.id) });
      message.success('Operation route updated successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to update operation route');
    },
  });
};

/**
 * Delete operation route
 */
export const useDeleteOperationRoute = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => manufacturingApi.operationRoutes.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: operationRouteKeys.all });
      message.success('Operation route deleted successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to delete operation route');
    },
  });
};

/**
 * Copy operation route
 */
export const useCopyOperationRoute = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) =>
      manufacturingApi.operationRoutes.copy(id, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: operationRouteKeys.all });
      message.success('Operation route copied successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to copy operation route');
    },
  });
};

/**
 * Add operation to route
 */
export const useAddRouteOperation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ routeId, data }: { routeId: number; data: RouteOperationCreate }) =>
      manufacturingApi.operationRoutes.addOperation(routeId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: operationRouteKeys.operations(variables.routeId) });
      message.success('Operation added successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to add operation');
    },
  });
};

/**
 * Update route operation
 */
export const useUpdateRouteOperation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      routeId,
      operationId,
      data,
    }: {
      routeId: number;
      operationId: number;
      data: Partial<RouteOperationCreate>;
    }) => manufacturingApi.operationRoutes.updateOperation(routeId, operationId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: operationRouteKeys.operations(variables.routeId) });
      message.success('Operation updated successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to update operation');
    },
  });
};

/**
 * Delete route operation
 */
export const useDeleteRouteOperation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ routeId, operationId }: { routeId: number; operationId: number }) =>
      manufacturingApi.operationRoutes.deleteOperation(routeId, operationId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: operationRouteKeys.operations(variables.routeId) });
      message.success('Operation deleted successfully');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || 'Failed to delete operation');
    },
  });
};
