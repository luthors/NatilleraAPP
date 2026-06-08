/**
 * NatillerasDashboard — main page listing all natilleras for the current user.
 *
 * - Shows admin and member natilleras
 * - Empty state with CTA to create a new one
 * - Click on card → navigate to /natilleras/:id
 */
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { natillerasApi } from '../natillerasApi'
import NatilleraCard from './NatilleraCard'

export default function NatillerasDashboard() {
  const navigate = useNavigate()
  const { data, isLoading, isError } = useQuery({
    queryKey: ['natilleras'],
    queryFn: () => natillerasApi.listar().then((r) => r.data),
  })

  if (isLoading) {
    return (
      <div className="p-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((n) => (
          <div key={n} className="h-36 rounded-2xl bg-gray-100 animate-pulse" />
        ))}
      </div>
    )
  }

  if (isError) {
    return (
      <div className="p-6 text-red-600">Error al cargar las natilleras. Intenta de nuevo.</div>
    )
  }

  const natilleras = data ?? []

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-gray-900">Mis Natilleras</h1>
        <button
          onClick={() => navigate('/natilleras/nueva')}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
        >
          + Nueva
        </button>
      </div>

      {natilleras.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-4xl mb-3">🏦</p>
          <p className="font-medium text-gray-600">Aún no tienes natilleras</p>
          <p className="text-sm mt-1">Crea una nueva o espera una invitación.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {natilleras.map((n) => (
            <NatilleraCard
              key={n.id}
              natillera={n}
              onClick={() => navigate(`/natilleras/${n.id}`)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
