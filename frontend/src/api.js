import axios from 'axios'

// In dev, Vite proxies `/api` to the backend to avoid CORS.
// In prod, you can set VITE_API_BASE_URL to a full URL (e.g. https://...).
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 20000,
})

