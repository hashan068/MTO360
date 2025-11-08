import { useEffect } from 'react';
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
    signOut,
  } = useAuthStore((state) => ({
    accessToken: state.accessToken,
    user: state.user,
    isInitialized: state.isInitialized,
    isAuthenticating: state.isAuthenticating,
    error: state.error,
    initialize: state.initialize,
    signIn: state.signIn,
    signOut: state.signOut,
  }));

  useEffect(() => {
    if (!isInitialized) {
      initialize();
    }
  }, [initialize, isInitialized]);

  return {
    accessToken,
    user,
    isAuthenticating,
    isInitialized,
    isAuthenticated: Boolean(accessToken),
    error,
    signIn,
    signOut,
    resetError: () => useAuthStore.setState({ error: null }),
  };
};
