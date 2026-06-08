import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../../lib/apiClient';

export function useCrearNatillera() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (datos) => {
      const { data } = await apiClient.post('/natilleras', datos);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['natilleras'] });
    },
  });
}

export function useActivarNatillera(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post(`/natilleras/${natilleraId}/activar`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['natilleras'] });
      queryClient.invalidateQueries({ queryKey: ['natilleras', natilleraId] });
    },
  });
}

export function useEditarNatillera(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (datos) => {
      const { data } = await apiClient.patch(`/natilleras/${natilleraId}`, datos);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['natilleras', natilleraId] });
      queryClient.invalidateQueries({ queryKey: ['natilleras'] });
    },
  });
}

export function useCerrarNatillera(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ forzar = false } = {}) => {
      const { data } = await apiClient.post(`/natilleras/${natilleraId}/cerrar`, { forzar });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['natilleras'] });
      queryClient.invalidateQueries({ queryKey: ['natilleras', natilleraId] });
    },
  });
}

export function useArchivarNatillera(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post(`/natilleras/${natilleraId}/archivar`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['natilleras'] });
    },
  });
}
