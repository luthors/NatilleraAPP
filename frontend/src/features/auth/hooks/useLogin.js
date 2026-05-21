import { useMutation } from '@tanstack/react-query';
import apiClient from '../../../lib/apiClient';
import useAuthStore from '../../../store/authStore';

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth);

  return useMutation({
    mutationFn: async ({ email, password }) => {
      const { data } = await apiClient.post('/auth/login', { email, password });
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
