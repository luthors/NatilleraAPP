/**
 * LoginPage — email + password form with error feedback.
 *
 * Uses TanStack Query mutation → authApi.login → setAuth → redirect /natilleras
 */
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { authApi } from '../authApi'
import useAuthStore from '../hooks/useAuthStore'

export default function LoginPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [form, setForm] = useState({ email: '', password: '' })

  const mutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: async (res) => {
      const { access_token, refresh_token } = res.data
      const meRes = await authApi.me()
      setAuth({ user: meRes.data, access_token, refresh_token })
      navigate('/natilleras')
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    mutation.mutate(form)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-2xl font-bold text-indigo-600 mb-1">🏦 Natillera App</h1>
        <p className="text-gray-500 text-sm mb-6">Inicia sesión en tu cuenta</p>

        {mutation.isError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {mutation.error?.response?.data?.detail ?? 'Error al iniciar sesión'}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Correo</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="tu@correo.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input
              type="password"
              required
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
          >
            {mutation.isPending ? 'Entrando...' : 'Iniciar sesión'}
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-500 space-y-2">
          <p>
            <Link to="/recuperar-password" className="text-indigo-600 hover:underline">
              ¿Olvidaste tu contraseña?
            </Link>
          </p>
          <p>
            ¿No tienes cuenta?{' '}
            <Link to="/registro" className="text-indigo-600 hover:underline">
              Regístrate
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
