import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendHost = process.env.BACKEND_HOST ?? 'localhost'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/ws': {
        target: `ws://${backendHost}:8000`,
        ws: true,
        changeOrigin: true,
      },
      '/api': {
        target: `http://${backendHost}:8000`,
        changeOrigin: true,
      },
    },
  },
})
