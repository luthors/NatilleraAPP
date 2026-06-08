import { useState } from 'react';
import { usePeriodos } from '../../natilleras/hooks/useNatilleras';
import { useRegistrarPagoAdmin, useRegistrarPagoSocio } from '../hooks/usePagos';
import Spinner from '../../../shared/components/Spinner';

const METODOS = ['EFECTIVO', 'TRANSFERENCIA', 'PSE'];

export default function RegistrarPagoForm({ natilleraId, isAdmin, onSuccess }) {
  const { data: periodos, isLoading: loadingPeriodos } = usePeriodos(natilleraId);
  const { mutate: registrarAdmin, isPending: pendingAdmin, error: errorAdmin } = useRegistrarPagoAdmin(natilleraId);
  const { mutate: registrarSocio, isPending: pendingSocio, error: errorSocio } = useRegistrarPagoSocio(natilleraId);

  const [form, setForm] = useState({
    socio_id: '',
    periodo_id: '',
    monto: '',
    metodo: 'EFECTIVO',
    referencia: '',
    forzar: false,
  });

  const set = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((p) => ({ ...p, [name]: type === 'checkbox' ? checked : value }));
  };

  const isPending = pendingAdmin || pendingSocio;
  const error = errorAdmin || errorSocio;
  const serverError = error?.response?.data?.detail || error?.message;

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      periodo_id: parseInt(form.periodo_id),
      metodo: form.metodo,
      referencia: form.referencia || undefined,
    };

    if (isAdmin) {
      registrarAdmin(
        {
          ...payload,
          socio_id: parseInt(form.socio_id),
          monto: parseFloat(form.monto),
          forzar: form.forzar,
        },
        { onSuccess }
      );
    } else {
      registrarSocio(payload, { onSuccess });
    }
  };

  if (loadingPeriodos) return <Spinner />;

  const periodoActual = periodos?.find((p) => p.estado === 'ABIERTO');
  const opcionesPeriodo = periodos || [];

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {serverError && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {serverError}
        </div>
      )}

      {isAdmin && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">ID del socio *</label>
          <input
            type="number"
            name="socio_id"
            required
            value={form.socio_id}
            onChange={set}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            placeholder="ID del socio"
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Período *</label>
        <select
          name="periodo_id"
          required
          value={form.periodo_id}
          onChange={set}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        >
          <option value="">Selecciona un período</option>
          {opcionesPeriodo.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nombre || `Período ${p.numero}`} — {p.estado}
            </option>
          ))}
        </select>
        {periodoActual && !form.periodo_id && (
          <p className="text-xs text-gray-400 mt-1">
            Período actual: {periodoActual.nombre || `Período ${periodoActual.numero}`}
          </p>
        )}
      </div>

      {isAdmin && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Monto (COP) *</label>
          <input
            type="number"
            name="monto"
            required
            min="1"
            value={form.monto}
            onChange={set}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            placeholder="Monto del pago"
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Método de pago *</label>
        <select
          name="metodo"
          value={form.metodo}
          onChange={set}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        >
          {METODOS.map((m) => (
            <option key={m} value={m}>{m.charAt(0) + m.slice(1).toLowerCase()}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Referencia (opcional)</label>
        <input
          type="text"
          name="referencia"
          value={form.referencia}
          onChange={set}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          placeholder="Número de transacción"
        />
      </div>

      {isAdmin && (
        <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
          <input
            type="checkbox"
            name="forzar"
            checked={form.forzar}
            onChange={set}
            className="rounded"
          />
          Forzar si el monto difiere del estándar
        </label>
      )}

      <button
        type="submit"
        disabled={isPending}
        className="w-full rounded-lg bg-primary text-white py-2 text-sm font-semibold hover:bg-primary/90 disabled:opacity-60 transition-colors"
      >
        {isPending ? 'Registrando…' : 'Registrar pago'}
      </button>
    </form>
  );
}
