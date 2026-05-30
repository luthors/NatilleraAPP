/**
 * DistribucionPreview — shows the final distribution breakdown before execution.
 *
 * Props:
 *   natilleraId: number
 *   onExecuted: () => void
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'

const distribApi = {
  preview:  (id) => api.get(`/natilleras/${id}/distribuciones/preview`),
  ejecutar: (id) => api.post(`/natilleras/${id}/distribuciones/ejecutar`),
}

const COP = (v) =>
  new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', minimumFractionDigits: 0 }).format(v)

export default function DistribucionPreview({ natilleraId, onExecuted }) {
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['distribucion-preview', natilleraId],
    queryFn: () => distribApi.preview(natilleraId).then((r) => r.data),
  })

  const mutation = useMutation({
    mutationFn: () => distribApi.ejecutar(natilleraId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['natilleras'] })
      onExecuted?.()
    },
  })

  if (isLoading) return <div className="animate-pulse h-40 bg-gray-100 rounded-xl" />
  if (!data) return null

  return (
    <div className="space-y-4">
      <div className="bg-indigo-50 rounded-xl p-4 flex justify-between items-center">
        <span className="text-sm text-indigo-700 font-medium">Fondo total a distribuir</span>
        <span className="text-xl font-bold text-indigo-700">{COP(data.saldo_total)}</span>
      </div>

      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-gray-500 border-b">
            <th className="pb-2">Socio</th>
            <th className="pb-2 text-right">Monto base</th>
            <th className="pb-2 text-right">Total a recibir</th>
          </tr>
        </thead>
        <tbody>
          {data.distribucion.map((row) => (
            <tr key={row.socio_id} className="border-b last:border-0">
              <td className="py-2">{row.nombre_socio}</td>
              <td className="py-2 text-right text-gray-600">{COP(row.monto_base)}</td>
              <td className="py-2 text-right font-semibold text-green-700">{COP(row.total_a_recibir)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {mutation.isError && (
        <p className="text-sm text-red-600">
          {mutation.error?.response?.data?.detail ?? 'Error al ejecutar distribución'}
        </p>
      )}

      <button
        onClick={() => mutation.mutate()}
        disabled={mutation.isPending}
        className="w-full bg-green-600 text-white py-2 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 transition"
      >
        {mutation.isPending ? 'Ejecutando...' : '✅ Confirmar y ejecutar distribución'}
      </button>
    </div>
  )
}
