import { useState } from 'react';
import { useCrearNatillera } from '../hooks/useNatilleraMutations';

const PERIODICIDADES = ['SEMANAL', 'QUINCENAL', 'MENSUAL'];

export default function CrearNatilleraForm({ onSuccess }) {
  const { mutate, isPending, error } = useCrearNatillera();
  const [form, setForm] = useState({
    nombre: '',
    descripcion: '',
    monto_por_periodo: '',
    periodicidad: 'MENSUAL',
    fecha_inicio: '',
    fecha_fin: '',
    max_socios: '20',
  });

  const set = (e) => setForm((p) => ({ ...p, [e.target.name]: e.target.value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate(
      {
        ...form,
        monto_por_periodo: parseFloat(form.monto_por_periodo),
        max_socios: parseInt(form.max_socios),
      },
      { onSuccess }
    );
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
        <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
        <input
          name="nombre"
          required
          value={form.nombre}
          onChange={set}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          placeholder="Natillera familiar 2026"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
        <textarea
          name="descripcion"
          value={form.descripcion}
          onChange={set}
          rows={2}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none"
          placeholder="Descripción opcional"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Monto / período (COP) *</label>
          <input
            type="number"
            name="monto_por_periodo"
            required
            min="1"
            value={form.monto_por_periodo}
            onChange={set}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            placeholder="50000"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Periodicidad *</label>
          <select
            name="periodicidad"
            value={form.periodicidad}
            onChange={set}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            {PERIODICIDADES.map((p) => (
              <option key={p} value={p}>{p.charAt(0) + p.slice(1).toLowerCase()}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Fecha inicio *</label>
          <input
            type="date"
            name="fecha_inicio"
            required
            value={form.fecha_inicio}
            onChange={set}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Fecha fin *</label>
          <input
            type="date"
            name="fecha_fin"
            required
            value={form.fecha_fin}
            onChange={set}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Máximo de socios</label>
        <input
          type="number"
          name="max_socios"
          min="2"
          max="100"
          value={form.max_socios}
          onChange={set}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
      </div>

      <div className="flex gap-3 pt-2">
        <button
          type="submit"
          disabled={isPending}
          className="flex-1 rounded-lg bg-primary text-white py-2 text-sm font-semibold hover:bg-primary/90 disabled:opacity-60 transition-colors"
        >
          {isPending ? 'Creando…' : 'Crear natillera'}
        </button>
      </div>
    </form>
  );
}
