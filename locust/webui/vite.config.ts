import reactSwcPlugin from '@vitejs/plugin-react-swc';
import { UserConfig, defineConfig } from 'vite';
import checkerPlugin from 'vite-plugin-checker';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig((config: UserConfig) => ({
  plugins: [
    reactSwcPlugin(),
    tsconfigPaths(),
    config.mode !== 'production' &&
      config.mode !== 'test' &&
      checkerPlugin({
        typescript: true,
        eslint: {
          lintCommand: 'eslint ./src/**/*.{ts,tsx}',
        },
      }),
  ],
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
