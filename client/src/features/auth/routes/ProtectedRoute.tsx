import { useEffect } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { Flex, Spin } from 'antd';
import { useAuthStore } from '@/features/auth/store/authStore';

const ProtectedRoute = () => {
  const location = useLocation();
  const accessToken = useAuthStore((state) => state.accessToken);
  const isInitialized = useAuthStore((state) => state.isInitialized);
  const isAuthenticating = useAuthStore((state) => state.isAuthenticating);
  const initialize = useAuthStore((state) => state.initialize);

  useEffect(() => {
    if (!isInitialized) {
      initialize();
    }
  }, [initialize, isInitialized]);

  if (!isInitialized || isAuthenticating) {
    return (
      <Spin size="large" tip="Checking credentials..." style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ minHeight: '100vh' }} />
      </Spin>
    );
  }

  if (!accessToken) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
