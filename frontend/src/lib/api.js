/**
 * Axios instance pre-configured for the Natillera API.
 *
 * - Base URL from VITE_API_BASE_URL env var (defaults to http://localhost:8000)
 * - Request interceptor: attaches Bearer token from localStorage
 * - Response interceptor: handles 401 → clears token → redirects to /login
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
export const API_V1 = `${BASE_URL}/api/v1`

const api = axios.create({
  baseURL: API_V1,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
})

// ── Request interceptor ────────────────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor ──────────────────────────────────────────────────
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export default api
