/**
 * Natilleras API — calls to /api/v1/natilleras/*
 */
import api from '@/lib/api'

export const natillerasApi = {
  listar: () => api.get('/natilleras'),
  obtener: (id) => api.get(`/natilleras/${id}`),
  crear: (data) => api.post('/natilleras', data),
  editar: (id, data) => api.patch(`/natilleras/${id}`, data),
  activar: (id) => api.post(`/natilleras/${id}/activar`),
  cerrar: (id, forzar = false) => api.post(`/natilleras/${id}/cerrar`, { forzar }),
  archivar: (id) => api.post(`/natilleras/${id}/archivar`),
  periodos: (id) => api.get(`/natilleras/${id}/periodos`),
}
