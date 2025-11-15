import { useEffect, useCallback } from 'react';
import { useAuthStore } from '@/features/auth/store/authStore';

export const useAuth = () => {
  const {
    accessToken,
    user,
    isInitialized,
    isAuthenticating,
    error,
    initialize,
    signIn,
    signUp,
    signOut,
  } = useAuthStore((state) => ({
    accessToken: state.accessToken,
    user: state.user,
    isInitialized: state.isInitialized,
    isAuthenticating: state.isAuthenticating,
    error: state.error,
    initialize: state.initialize,
    signIn: state.signIn,
    signUp: state.signUp,
    signOut: state.signOut,
  }));

  useEffect(() => {
    if (!isInitialized) {
      initialize();
    }
  }, [initialize, isInitialized]);

  const resetError = useCallback(() => {
    useAuthStore.setState({ error: null });
  }, []);

  return {
    accessToken,
    user,
    isAuthenticating,
    isInitialized,
    isAuthenticated: Boolean(accessToken),
    error,
    signIn,
    signUp,
    signOut,
    resetError,
  };
};
