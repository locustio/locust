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
    lib: {
      entry: './src/lib.tsx',
      formats: ['es'] as LibraryFormats[],
      fileName: () => 'webui.js',
    },
    sourcemap: true,
    rollupOptions: {
      external: ['react', 'react-dom', 'react-redux'],
      output: {
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM',
          'react-redux': 'react-redux',
        },
      },
    },
  },
}));
