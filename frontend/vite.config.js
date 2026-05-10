// vite.config.js
// Proxies /api requests to the Flask server on port 5000 so the React dev
// server and Flask can run side-by-side without CORS issues.

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000',
    },
  },
})
