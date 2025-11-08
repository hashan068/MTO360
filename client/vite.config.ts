import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react-swc';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  const proxyTarget = env.VITE_API_PROXY;

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '@features': fileURLToPath(new URL('./src/features', import.meta.url)),
        '@shared': fileURLToPath(new URL('./src/shared', import.meta.url)),
      },
    },
    server: {
      host: true,
      port: Number(env.VITE_DEV_SERVER_PORT ?? 5173),
      proxy:
        proxyTarget && proxyTarget.length > 0
          ? {
              '/api': {
                target: proxyTarget,
                changeOrigin: true,
                secure: false,
              },
            }
          : undefined,
    },
    build: {
      sourcemap: true,
      outDir: 'dist',
    },
  };
});
