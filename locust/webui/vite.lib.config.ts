import reactSwcPlugin from '@vitejs/plugin-react-swc';
import { LibraryFormats, UserConfig, defineConfig } from 'vite';
import checkerPlugin from 'vite-plugin-checker';
import dts from 'vite-plugin-dts';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig((config: UserConfig) => ({
  plugins: [
    reactSwcPlugin(),
    tsconfigPaths(),
    dts({
      outDir: './lib/types',
      exclude: ['**/*.test.ts', '**/*.test.tsx', '**/test', '**/tests'],
    }),
    config.mode !== 'production' &&
      config.mode !== 'test' &&
      checkerPlugin({
        typescript: true,
        eslint: {
          lintCommand: 'eslint ./src/**/*.{ts,tsx}',
        },
      }),
  ],
  build: {
    outDir: 'lib',
    minify: true,
    sourcemap: false,
    lib: {
      entry: './src/lib.tsx',
      formats: ['es'] as LibraryFormats[],
      fileName: () => 'webui.js',
    },
    rollupOptions: {
      external: ['react', 'react-dom', 'react-redux'],
    },
  },
}));
