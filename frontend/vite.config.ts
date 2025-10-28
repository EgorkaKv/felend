import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Bundle analyzer (generates stats.html after build)
    visualizer({
      filename: './dist/stats.html',
      open: false, // set to true to auto-open after build
      gzipSize: true,
      brotliSize: true,
    }),
  ],
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
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // React core
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          
          // Material-UI core (самая тяжелая библиотека)
          'mui-core': ['@mui/material', '@emotion/react', '@emotion/styled'],
          
          // Material-UI icons (отдельно, т.к. очень тяжелые)
          'mui-icons': ['@mui/icons-material'],
          
          // Redux & state management
          'redux-vendor': ['@reduxjs/toolkit', 'react-redux', 'redux-persist'],
          
          // Forms & validation
          'forms-vendor': ['react-hook-form', '@hookform/resolvers', 'yup'],
          
          // HTTP & API
          'api-vendor': ['axios', 'swr'],
          
          // Utilities
          'utils-vendor': ['date-fns', 'swiper'],
        },
      },
    },
    // Target modern browsers for smaller bundle
    target: 'es2020',
    // Увеличим лимит предупреждения (после оптимизации chunks будут меньше)
    chunkSizeWarningLimit: 600,
    // Source maps только для debugging (отключаем в production)
    sourcemap: false,
  },
})
