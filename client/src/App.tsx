import { useEffect, useMemo, useState } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppRoutes from '@/routes';
import { useUIStore } from '@/shared/state/uiStore';
import { getAntdThemeConfig, syncThemeToDom, type ResolvedTheme } from '@/shared/theme';

const queryClient = new QueryClient();

const App = () => {
  const themeMode = useUIStore((state) => state.theme);
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>('light');

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');

    const computeTheme = (): ResolvedTheme => {
      if (themeMode === 'dark') return 'dark';
      if (themeMode === 'light') return 'light';
      return mq.matches ? 'dark' : 'light';
    };

    const updateTheme = () => {
      const next = computeTheme();
      setResolvedTheme(next);
      syncThemeToDom(next);
    };

    updateTheme();

    if (themeMode === 'system') {
      mq.addEventListener('change', updateTheme);
      return () => mq.removeEventListener('change', updateTheme);
    }

    return undefined;
  }, [themeMode]);

  const themeConfig = useMemo(() => getAntdThemeConfig(resolvedTheme), [resolvedTheme]);

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider theme={themeConfig}>
        <AntdApp>
          <BrowserRouter
            future={{
              v7_startTransition: true,
              v7_relativeSplatPath: true,
            }}
          >
            <AppRoutes />
          </BrowserRouter>
        </AntdApp>
      </ConfigProvider>
    </QueryClientProvider>
  );
};

export default App;

