import { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useResetPassword } from '../features/auth/hooks/useRecuperarPassword';

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const { mutate, isPending, error, isSuccess } = useResetPassword();
  const [form, setForm] = useState({ nueva_password: '', confirmar: '' });
  const [clientError, setClientError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setClientError('');
    if (form.nueva_password !== form.confirmar) {
      setClientError('Las contraseñas no coinciden.');
      return;
    }
    mutate(
      { token, nueva_password: form.nueva_password },
      { onSuccess: () => setTimeout(() => navigate('/login'), 2000) }
    );
  };

  const serverError = error?.response?.data?.detail || error?.message || null;

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-5">Nueva contraseña</h2>

          {isSuccess ? (
            <div className="rounded-md bg-green-50 border border-green-200 p-4 text-sm text-green-800">
              Contraseña actualizada. Redirigiendo al inicio de sesión…
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              {(clientError || serverError) && (
                <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                  {clientError || serverError}
                </div>
              )}
              {[
                { name: 'nueva_password', label: 'Nueva contraseña' },
                { name: 'confirmar', label: 'Confirmar contraseña' },
              ].map(({ name, label }) => (
                <div key={name}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                  <input
                    type="password"
                    required
                    value={form[name]}
                    onChange={(e) => setForm((p) => ({ ...p, [name]: e.target.value }))}
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                    placeholder="••••••••"
                  />
                </div>
              ))}
              <button
                type="submit"
                disabled={isPending || !token}
                className="w-full rounded-lg bg-primary text-white py-2 px-4 text-sm font-semibold hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
              >
                {isPending ? 'Guardando…' : 'Guardar contraseña'}
              </button>
              <p className="text-center text-sm">
                <Link to="/login" className="text-primary hover:underline">Volver al inicio</Link>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
