/**
 * Auth store (Zustand).
 *
 * Persists access_token and refresh_token in localStorage.
 * Exposes: user, tokens, setAuth(), logout(), isAuthenticated
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,

      setAuth: ({ user, access_token, refresh_token }) => {
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        set({ user, accessToken: access_token, refreshToken: refresh_token })
      },

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, accessToken: null, refreshToken: null })
      },

      isAuthenticated: () => Boolean(get().accessToken),
    }),
    {
      name: 'natillera-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    },
  ),
)

export default useAuthStore
