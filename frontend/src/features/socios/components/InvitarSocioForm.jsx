import { useState } from 'react';
import { useInvitarSocio } from '../hooks/useSocios';

export default function InvitarSocioForm({ natilleraId, onSuccess }) {
  const { mutate, isPending, error } = useInvitarSocio(natilleraId);
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate({ email }, { onSuccess: () => { setEmail(''); onSuccess?.(); } });
  };

  const serverError = error?.response?.data?.detail || error?.message;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {serverError && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {serverError}
        </div>
      )}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Correo del invitado *
        </label>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          placeholder="amigo@ejemplo.com"
        />
      </div>
      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-lg bg-primary text-white py-2 text-sm font-semibold hover:bg-primary/90 disabled:opacity-60 transition-colors"
      >
        {isPending ? 'Enviando invitación…' : 'Enviar invitación'}
      </button>
    </form>
  );
}
