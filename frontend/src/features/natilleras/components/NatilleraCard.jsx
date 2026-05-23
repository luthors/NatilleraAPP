/**
 * NatilleraCard — summary card shown on the dashboard.
 *
 * Props:
 *   natillera: NatilleraResponse
 *   onClick: () => void
 */
const ESTADO_COLOR = {
  CONFIGURACION: 'bg-gray-100 text-gray-700',
  ACTIVA:        'bg-green-100 text-green-700',
  EN_CIERRE:     'bg-yellow-100 text-yellow-700',
  CERRADA:       'bg-red-100 text-red-700',
  ARCHIVADA:     'bg-slate-100 text-slate-500',
}

const PERIODICIDAD_LABEL = {
  SEMANAL:   'Semanal',
  QUINCENAL: 'Quincenal',
  MENSUAL:   'Mensual',
  BIMESTRAL: 'Bimestral',
}

export default function NatilleraCard({ natillera, onClick }) {
  const estadoClass = ESTADO_COLOR[natillera.estado] ?? 'bg-gray-100 text-gray-600'
  const monto = new Intl.NumberFormat('es-CO', {
    style: 'currency', currency: 'COP', minimumFractionDigits: 0,
  }).format(natillera.monto_por_periodo)

  return (
    <button
      onClick={onClick}
      className="w-full text-left bg-white rounded-2xl shadow hover:shadow-md transition p-5 border border-gray-100"
    >
      <div className="flex items-start justify-between mb-3">
        <h2 className="font-semibold text-gray-900 truncate pr-2">{natillera.nombre}</h2>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap ${estadoClass}`}>
          {natillera.estado}
        </span>
      </div>

      <div className="text-2xl font-bold text-indigo-600 mb-1">{monto}</div>
      <p className="text-xs text-gray-400">{PERIODICIDAD_LABEL[natillera.periodicidad]}</p>

      <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
        <span>📅 {natillera.fecha_inicio} → {natillera.fecha_fin}</span>
        <span>👥 max {natillera.max_socios}</span>
      </div>
    </button>
  )
}
