import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/pages': path.resolve(__dirname, './src/pages'),
      '@/api': path.resolve(__dirname, './src/api'),
      '@/hooks': path.resolve(__dirname, './src/hooks'),
      '@/store': path.resolve(__dirname, './src/store'),
      '@/utils': path.resolve(__dirname, './src/utils'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/theme': path.resolve(__dirname, './src/theme'),
      '@/constants': path.resolve(__dirname, './src/constants'),
    },
  },
  server: {
    host: true,
    hmr: {
      host: '3ea2e94601b7.ngrok-free.app',
      clientPort: 443,
      protocol: 'wss'
    }
  }
})
