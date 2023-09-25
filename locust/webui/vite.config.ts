import reactSwcPlugin from '@vitejs/plugin-react-swc';
import { defineConfig, splitVendorChunkPlugin } from 'vite';
import checkerPlugin from 'vite-plugin-checker';
import tsconfigPaths from 'vite-tsconfig-paths';


// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    reactSwcPlugin(),
    tsconfigPaths(),
    splitVendorChunkPlugin(),
    checkerPlugin({
      typescript: true,
      eslint: {
        lintCommand: 'eslint ./src/**/*.{ts,tsx}',
      },
    }),
  ],
  server: {
    port: 4000,
    open: './dev.html'
  },
});
