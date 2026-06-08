/**
 * authStore — Zustand store with localStorage persistence.
 *
 * Stores: usuario (profile object), accessToken, refreshToken.
 * Actions: setAuth, clearAuth, setUsuario.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set) => ({
      usuario: null,
      accessToken: null,
      refreshToken: null,

      setAuth: ({ usuario, accessToken, refreshToken }) =>
        set({ usuario, accessToken, refreshToken }),

      setUsuario: (usuario) => set({ usuario }),

      clearAuth: () =>
        set({ usuario: null, accessToken: null, refreshToken: null }),
    }),
    {
      name: 'natillera-auth',
    }
  )
);

export default useAuthStore;
