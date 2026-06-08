import { useMutation } from '@tanstack/react-query';
import apiClient from '../../../lib/apiClient';
import useAuthStore from '../../../store/authStore';

export function useRegister() {
  const setAuth = useAuthStore((s) => s.setAuth);

  return useMutation({
    mutationFn: async ({ nombre, email, password }) => {
      const { data } = await apiClient.post('/auth/registro', { nombre, email, password });
      return data;
    },
    onSuccess: (data) => {
      setAuth({
        usuario: data.usuario,
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
      });
    },
  });
}
