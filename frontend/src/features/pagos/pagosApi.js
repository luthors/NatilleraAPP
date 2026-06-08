/**
 * Pagos API — calls to /api/v1/natilleras/:id/pagos/*
 */
import api from '@/lib/api'

export const pagosApi = {
  listar:           (natilleraId) => api.get(`/natilleras/${natilleraId}/pagos`),
  misPagos:         (natilleraId) => api.get(`/natilleras/${natilleraId}/mis-pagos`),
  registrarSocio:   (natilleraId, data) => api.post(`/natilleras/${natilleraId}/mis-pagos`, data),
  registrarAdmin:   (natilleraId, data) => api.post(`/natilleras/${natilleraId}/pagos/admin`, data),
  confirmar:        (natilleraId, pagoId, data) => api.post(`/natilleras/${natilleraId}/pagos/confirmar/${pagoId}`, data),
  rechazar:         (natilleraId, pagoId, data) => api.post(`/natilleras/${natilleraId}/pagos/rechazar/${pagoId}`, data),
  revertir:         (natilleraId, pagoId, data) => api.post(`/natilleras/${natilleraId}/pagos/revertir/${pagoId}`, data),
  saldo:            (natilleraId) => api.get(`/natilleras/${natilleraId}/saldo`),
  miEstado:         (natilleraId) => api.get(`/natilleras/${natilleraId}/mi-estado`),
}
