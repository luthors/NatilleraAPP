import { useQuery } from '@tanstack/react-query';
import apiClient from '../../../lib/apiClient';

export function useNatilleras() {
  return useQuery({
    queryKey: ['natilleras'],
    queryFn: async () => {
      const { data } = await apiClient.get('/natilleras');
      return data;
    },
  });
}

export function useNatilleraDetalle(id) {
  return useQuery({
    queryKey: ['natilleras', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/natilleras/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function usePeriodos(natilleraId) {
  return useQuery({
    queryKey: ['natilleras', natilleraId, 'periodos'],
    queryFn: async () => {
      const { data } = await apiClient.get(`/natilleras/${natilleraId}/periodos`);
      return data;
    },
    enabled: !!natilleraId,
  });
}
