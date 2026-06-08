/**
 * Auth API — calls to /api/v1/auth/*
 */
import api from '@/lib/api'

export const authApi = {
  registro: (data) => api.post('/auth/registro', data),
  login: (data) => api.post('/auth/login', data),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  logout: (refreshToken) => api.post('/auth/logout', { refresh_token: refreshToken }),
  me: () => api.get('/auth/me'),
  recuperarPassword: (email) => api.post('/auth/recuperar-password', { email }),
  resetPassword: (token, nuevaPassword) =>
    api.post('/auth/reset-password', { token, nueva_password: nuevaPassword }),
}
