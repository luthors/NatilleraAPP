/**
 * RegisterPage — new user registration form.
 */
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { authApi } from '../authApi'
import useAuthStore from '../hooks/useAuthStore'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [form, setForm] = useState({ nombre: '', email: '', password: '' })

  const mutation = useMutation({
    mutationFn: authApi.registro,
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

  const field = (key, label, type = 'text', placeholder = '') => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        required
        value={form[key]}
        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
        placeholder={placeholder}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
    </div>
  )

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
        <h1 className="text-2xl font-bold text-indigo-600 mb-1">🏦 Natillera App</h1>
        <p className="text-gray-500 text-sm mb-6">Crea tu cuenta</p>

        {mutation.isError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {mutation.error?.response?.data?.detail ?? 'Error al registrarse'}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {field('nombre', 'Nombre completo', 'text', 'Juan Pérez')}
          {field('email', 'Correo electrónico', 'email', 'tu@correo.com')}
          {field('password', 'Contraseña', 'password')}
          <p className="text-xs text-gray-400">
            Mínimo 8 caracteres, una mayúscula, una minúscula, un número y un símbolo.
          </p>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
          >
            {mutation.isPending ? 'Creando cuenta...' : 'Registrarme'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-indigo-600 hover:underline">Inicia sesión</Link>
        </p>
      </div>
    </div>
  )
}
