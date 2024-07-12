import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import * as path from 'path';
import { resolve } from 'path';
import { rmSync } from 'fs';

// function cleanOutputDir() {
//   return {
//     name: 'clean-output-dir',
//     buildStart() {
//       rmSync(resolve(__dirname, '../static'), { recursive: true, force: true });
//     }
//   };
// }

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: path.resolve(__dirname, '../static')
  },  
  server: {
    host: '192.168.2.22',
    port: 3000,
    proxy: {
      '/removebg': {
        target: 'http://localhost:8080', 
        changeOrigin: true,   
      }
    }
  },  
})
