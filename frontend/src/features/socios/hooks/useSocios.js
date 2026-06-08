import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../../lib/apiClient';

export function useSocios(natilleraId) {
  return useQuery({
    queryKey: ['socios', natilleraId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/natilleras/${natilleraId}/socios`);
      return data;
    },
    enabled: !!natilleraId,
  });
}

export function useInvitarSocio(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ email }) => {
      const { data } = await apiClient.post(`/natilleras/${natilleraId}/socios/invitar`, { email });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['socios', natilleraId] });
    },
  });
}

export function useSuspenderSocio(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ socioId, razon }) => {
      const { data } = await apiClient.patch(
        `/natilleras/${natilleraId}/socios/${socioId}/suspender`,
        { razon }
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['socios', natilleraId] });
    },
  });
}

export function useReactivarSocio(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ socioId }) => {
      const { data } = await apiClient.patch(
        `/natilleras/${natilleraId}/socios/${socioId}/reactivar`
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['socios', natilleraId] });
    },
  });
}

export function useEliminarSocio(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ socioId }) => {
      await apiClient.delete(`/natilleras/${natilleraId}/socios/${socioId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['socios', natilleraId] });
    },
  });
}
