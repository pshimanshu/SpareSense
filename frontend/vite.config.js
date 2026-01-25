import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Backend runs on 5050 per the hackathon README quickstart.
      // Frontend should call `/api/...` to avoid CORS in dev.
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http://localhost:5050',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
