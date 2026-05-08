/**
 * API client for React Native (Expo).
 *
 * Base URL from app.json → expo.extra.apiBaseUrl
 * Token stored in expo-secure-store (not localStorage).
 */
import axios from 'axios'
import * as SecureStore from 'expo-secure-store'
import Constants from 'expo-constants'

const BASE_URL = Constants.expoConfig?.extra?.apiBaseUrl ?? 'http://localhost:8000'

const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
})

api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) {
      await SecureStore.deleteItemAsync('access_token')
      await SecureStore.deleteItemAsync('refresh_token')
      // Navigation reset handled by AuthContext
    }
    return Promise.reject(err)
  },
)

export default api
