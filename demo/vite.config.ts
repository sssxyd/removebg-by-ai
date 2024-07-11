import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import * as path from 'path';

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
    port: 3000,
    proxy: {
      '/removebg': {
        target: 'http://localhost:8080', 
        changeOrigin: true,   
      }
    }
  },  
})
