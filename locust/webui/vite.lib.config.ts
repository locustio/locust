import typescript from '@rollup/plugin-typescript';
import reactSwcPlugin from '@vitejs/plugin-react-swc';
import { LibraryFormats, UserConfig, defineConfig } from 'vite';
import checkerPlugin from 'vite-plugin-checker';
import tsconfigPaths from 'vite-tsconfig-paths';

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
  build: {
    outDir: 'lib',
    lib: {
      entry: './src/lib.ts',
      fileName: 'webui',
      formats: ['es', 'cjs'] as LibraryFormats[],
    },
    rollupOptions: {
      external: ['react'],
      plugins: [
        typescript({
          sourceMap: false,
          declaration: true,
          outputToFilesystem: true,
          declarationDir: './lib/types',
        }),
      ],
    },
  },
}));
