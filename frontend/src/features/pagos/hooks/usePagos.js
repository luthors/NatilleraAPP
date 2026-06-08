import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../../lib/apiClient';

export function useSaldoFondo(natilleraId, enabled = true) {
  return useQuery({
    queryKey: ['saldo', natilleraId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/natilleras/${natilleraId}/saldo`);
      return data;
    },
    enabled: !!natilleraId && enabled,
  });
}

export function useEstadoSocio(natilleraId, enabled = true) {
  return useQuery({
    queryKey: ['estado-socio', natilleraId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/natilleras/${natilleraId}/mi-estado`);
      return data;
    },
    enabled: !!natilleraId && enabled,
  });
}

export function usePagos(natilleraId, isAdmin = false) {
  return useQuery({
    queryKey: ['pagos', natilleraId, isAdmin ? 'admin' : 'socio'],
    queryFn: async () => {
      const url = isAdmin
        ? `/natilleras/${natilleraId}/pagos`
        : `/natilleras/${natilleraId}/mis-pagos`;
      const { data } = await apiClient.get(url);
      return data;
    },
    enabled: !!natilleraId,
  });
}

export function usePagosPendientes(natilleraId) {
  return useQuery({
    queryKey: ['pagos-pendientes', natilleraId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/natilleras/${natilleraId}/pagos?estado=PENDIENTE_CONFIRMACION`);
      return Array.isArray(data) ? data : data?.items || [];
    },
    enabled: !!natilleraId,
  });
}

export function useRegistrarPagoAdmin(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body) => {
      const { data } = await apiClient.post(`/natilleras/${natilleraId}/pagos/admin`, body);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pagos', natilleraId] });
      queryClient.invalidateQueries({ queryKey: ['saldo', natilleraId] });
    },
  });
}

export function useRegistrarPagoSocio(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body) => {
      const { data } = await apiClient.post(`/natilleras/${natilleraId}/mis-pagos`, body);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pagos', natilleraId] });
      queryClient.invalidateQueries({ queryKey: ['pagos-pendientes', natilleraId] });
    },
  });
}

export function useConfirmarPago(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ pagoId }) => {
      const { data } = await apiClient.post(`/natilleras/${natilleraId}/pagos/confirmar/${pagoId}`, {});
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pagos', natilleraId] });
      queryClient.invalidateQueries({ queryKey: ['pagos-pendientes', natilleraId] });
      queryClient.invalidateQueries({ queryKey: ['saldo', natilleraId] });
    },
  });
}

export function useRechazarPago(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ pagoId, razon }) => {
      const { data } = await apiClient.post(`/natilleras/${natilleraId}/pagos/rechazar/${pagoId}`, { razon });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pagos', natilleraId] });
      queryClient.invalidateQueries({ queryKey: ['pagos-pendientes', natilleraId] });
    },
  });
}

export function useRevertirPago(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ pagoId, justificacion }) => {
      const { data } = await apiClient.post(`/natilleras/${natilleraId}/pagos/revertir/${pagoId}`, { justificacion });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pagos', natilleraId] });
      queryClient.invalidateQueries({ queryKey: ['saldo', natilleraId] });
    },
  });
}
