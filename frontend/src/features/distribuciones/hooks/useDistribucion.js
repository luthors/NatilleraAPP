import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../../lib/apiClient';

export function useDistribucionPreview(natilleraId, enabled = true) {
  return useQuery({
    queryKey: ['distribucion-preview', natilleraId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/natilleras/${natilleraId}/distribuciones/preview`);
      return data;
    },
    enabled: !!natilleraId && enabled,
    retry: false,
  });
}

export function useEjecutarDistribucion(natilleraId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ confirmado }) => {
      const { data } = await apiClient.post(`/natilleras/${natilleraId}/distribuciones/ejecutar`, {
        confirmado,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['natilleras', natilleraId] });
      queryClient.invalidateQueries({ queryKey: ['natilleras'] });
      queryClient.invalidateQueries({ queryKey: ['saldo', natilleraId] });
      queryClient.invalidateQueries({ queryKey: ['distribucion-preview', natilleraId] });
    },
  });
}
