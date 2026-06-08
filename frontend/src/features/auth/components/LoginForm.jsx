import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useLogin } from '../hooks/useLogin';

export default function LoginForm() {
  const navigate = useNavigate();
  const { mutate: login, isPending, error } = useLogin();
  const [form, setForm] = useState({ email: '', password: '' });

  const handleChange = (e) =>
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    login(form, {
      onSuccess: () => navigate('/dashboard'),
    });
  };

  const serverError =
    error?.response?.data?.detail || error?.message || null;

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      {serverError && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {serverError}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Correo electrónico
        </label>
        <input
          type="email"
          name="email"
          autoComplete="email"
          required
          value={form.email}
          onChange={handleChange}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
          placeholder="tucorreo@ejemplo.com"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Contraseña
        </label>
        <input
          type="password"
          name="password"
          autoComplete="current-password"
          required
          value={form.password}
          onChange={handleChange}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
          placeholder="••••••••"
        />
      </div>

      <div className="flex items-center justify-between text-sm">
        <Link to="/recuperar-password" className="text-primary hover:underline">
          ¿Olvidaste tu contraseña?
        </Link>
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-lg bg-primary text-white py-2 px-4 text-sm font-semibold hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
      >
        {isPending ? 'Ingresando…' : 'Iniciar sesión'}
      </button>

      <p className="text-center text-sm text-gray-600">
        ¿No tienes cuenta?{' '}
        <Link to="/register" className="text-primary hover:underline font-medium">
          Regístrate
        </Link>
      </p>
    </form>
  );
}
