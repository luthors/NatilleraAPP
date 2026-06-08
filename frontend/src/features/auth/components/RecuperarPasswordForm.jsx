import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useRecuperarPassword } from '../hooks/useRecuperarPassword';

export default function RecuperarPasswordForm() {
  const { mutate, isPending, isSuccess, error } = useRecuperarPassword();
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate({ email });
  };

  if (isSuccess) {
    return (
      <div className="rounded-md bg-green-50 border border-green-200 p-4 text-sm text-green-800">
        Si ese correo está registrado, recibirás un enlace para restablecer tu contraseña.
        Revisa tu bandeja de entrada.
      </div>
    );
  }

  const serverError = error?.response?.data?.detail || error?.message || null;

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      {serverError && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {serverError}
        </div>
      )}

      <p className="text-sm text-gray-600">
        Ingresa tu correo y te enviaremos un enlace para restablecer tu contraseña.
      </p>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Correo electrónico
        </label>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
          placeholder="tucorreo@ejemplo.com"
        />
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-lg bg-primary text-white py-2 px-4 text-sm font-semibold hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
      >
        {isPending ? 'Enviando…' : 'Enviar enlace'}
      </button>

      <p className="text-center text-sm">
        <Link to="/login" className="text-primary hover:underline">
          Volver al inicio de sesión
        </Link>
      </p>
    </form>
  );
}
