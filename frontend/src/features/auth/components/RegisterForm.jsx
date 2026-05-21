import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useRegister } from '../hooks/useRegister';

export default function RegisterForm() {
  const navigate = useNavigate();
  const { mutate: register, isPending, error } = useRegister();
  const [form, setForm] = useState({
    nombre: '',
    email: '',
    password: '',
    confirmar: '',
  });
  const [clientError, setClientError] = useState('');

  const handleChange = (e) =>
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    setClientError('');
    if (form.password !== form.confirmar) {
      setClientError('Las contraseñas no coinciden.');
      return;
    }
    if (form.password.length < 8) {
      setClientError('La contraseña debe tener al menos 8 caracteres.');
      return;
    }
    if (!/[A-Z]/.test(form.password)) {
      setClientError('La contraseña debe contener al menos una letra mayúscula.');
      return;
    }
    if (!/\d/.test(form.password)) {
      setClientError('La contraseña debe contener al menos un número.');
      return;
    }
    register(
      { nombre: form.nombre, email: form.email, password: form.password },
      { onSuccess: () => navigate('/dashboard') }
    );
  };

  const serverError =
    error?.response?.data?.detail || error?.message || null;
  const displayError = clientError || serverError;

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      {displayError && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {displayError}
        </div>
      )}

      {[
        { name: 'nombre', label: 'Nombre completo', type: 'text', placeholder: 'Tu nombre', autoComplete: 'name' },
        { name: 'email', label: 'Correo electrónico', type: 'email', placeholder: 'tucorreo@ejemplo.com', autoComplete: 'email' },
        { name: 'password', label: 'Contraseña', type: 'password', placeholder: '••••••••', autoComplete: 'new-password' },
        { name: 'confirmar', label: 'Confirmar contraseña', type: 'password', placeholder: '••••••••', autoComplete: 'new-password' },
      ].map(({ name, label, type, placeholder, autoComplete }) => (
        <div key={name}>
          <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
          <input
            type={type}
            name={name}
            autoComplete={autoComplete}
            required
            value={form[name]}
            onChange={handleChange}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
            placeholder={placeholder}
          />
        </div>
      ))}

      <p className="text-xs text-gray-500">
        La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número.
      </p>

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-lg bg-primary text-white py-2 px-4 text-sm font-semibold hover:bg-primary/90 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
      >
        {isPending ? 'Registrando…' : 'Crear cuenta'}
      </button>

      <p className="text-center text-sm text-gray-600">
        ¿Ya tienes cuenta?{' '}
        <Link to="/login" className="text-primary hover:underline font-medium">
          Inicia sesión
        </Link>
      </p>
    </form>
  );
}
