import reactSwcPlugin from '@vitejs/plugin-react-swc';
import { viteSingleFile } from 'vite-plugin-singlefile';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default {
  plugins: [reactSwcPlugin(), tsconfigPaths(), viteSingleFile()],
  build: {
    emptyOutDir: false,
    minify: 'terser',
    rollupOptions: {
      input: {
        report: './report.html',
      },
    },
  },
};
