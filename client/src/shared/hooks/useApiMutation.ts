import { useMutation, type UseMutationOptions } from '@tanstack/react-query';
import type { AxiosError } from 'axios';
import { App as AntdApp } from 'antd';

export const useApiMutation = <TData = unknown, TVariables = void, TContext = unknown>(
  options: UseMutationOptions<TData, AxiosError, TVariables, TContext>
) => {
  const { message } = AntdApp.useApp();

  const mutation = useMutation<TData, AxiosError, TVariables, TContext>({
    ...options,
    onError: (error, variables, onMutateResult, context) => {
      const detail = (error.response?.data as { detail?: string })?.detail;
      message.error(detail ?? error.message ?? 'Unexpected error');
      options.onError?.(error, variables, onMutateResult, context);
    },
  });

  return mutation;
};
