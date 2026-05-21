import { useMutation } from '@tanstack/react-query';
import apiClient from '../../../lib/apiClient';

export function useRecuperarPassword() {
  return useMutation({
    mutationFn: async ({ email }) => {
      const { data } = await apiClient.post('/auth/recuperar-password', { email });
      return data;
    },
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: async ({ token, nueva_password }) => {
      const { data } = await apiClient.post('/auth/reset-password', {
        token,
        nueva_password,
      });
      return data;
    },
  });
}
