import reactSwcPlugin from '@vitejs/plugin-react-swc';
import { UserConfig, defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig((config: UserConfig) => ({
  plugins: [reactSwcPlugin(), tsconfigPaths()],
  base: './',
  build: {
    emptyOutDir: false,
    chunkSizeWarningLimit: 2000,
    rollupOptions: {
      input: {
        index: './index.html',
        auth: './auth.html',
      },
    },
    sourcemap: config.mode !== 'production',
  },
  server: {
    port: 4000,
    open: './dev.html',
  },
}));
