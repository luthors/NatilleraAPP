/**
 * PagoForm — socio self-registers a payment for a period.
 *
 * Props:
 *   natilleraId: number
 *   periodos: PeriodoResponse[]
 *   onSuccess: () => void
 */
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { pagosApi } from '../pagosApi'

const METODOS = ['EFECTIVO', 'TRANSFERENCIA', 'PSE']

export default function PagoForm({ natilleraId, periodos = [], onSuccess }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({ periodo_id: '', metodo: 'TRANSFERENCIA', referencia: '' })

  const mutation = useMutation({
    mutationFn: (data) => pagosApi.registrarSocio(natilleraId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['mis-pagos', natilleraId] })
      qc.invalidateQueries({ queryKey: ['mi-estado', natilleraId] })
      onSuccess?.()
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    mutation.mutate({ ...form, periodo_id: Number(form.periodo_id) })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Período</label>
        <select
          required
          value={form.periodo_id}
          onChange={(e) => setForm({ ...form, periodo_id: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">-- Selecciona un período --</option>
          {periodos.map((p) => (
            <option key={p.id} value={p.id} disabled={p.estado === 'CERRADO'}>
              {p.nombre} ({p.estado})
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Método de pago</label>
        <select
          value={form.metodo}
          onChange={(e) => setForm({ ...form, metodo: e.target.value })}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          {METODOS.map((m) => <option key={m}>{m}</option>)}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Referencia / No. de transacción <span className="text-gray-400">(opcional)</span>
        </label>
        <input
          type="text"
          value={form.referencia}
          onChange={(e) => setForm({ ...form, referencia: e.target.value })}
          placeholder="Ej. TRX-20260527-001"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {mutation.isError && (
        <p className="text-sm text-red-600">
          {mutation.error?.response?.data?.detail ?? 'Error al registrar pago'}
        </p>
      )}

      <button
        type="submit"
        disabled={mutation.isPending}
        className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
      >
        {mutation.isPending ? 'Registrando...' : 'Registrar pago'}
      </button>
    </form>
  )
}
