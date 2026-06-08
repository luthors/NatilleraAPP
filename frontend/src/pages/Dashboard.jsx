import { useState } from 'react';
import AppLayout from '../shared/components/AppLayout';
import { useNatilleras } from '../features/natilleras/hooks/useNatilleras';
import NatilleraCard from '../features/natilleras/components/NatilleraCard';
import Spinner from '../shared/components/Spinner';
import Modal from '../shared/components/Modal';
import CrearNatilleraForm from '../features/natilleras/components/CrearNatilleraForm';
import useAuthStore from '../store/authStore';

export default function Dashboard() {
  const { usuario } = useAuthStore();
  const { data: natilleras, isLoading, error } = useNatilleras();
  const [showCrear, setShowCrear] = useState(false);

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            Hola, {usuario?.nombre?.split(' ')[0]}
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">Tus natilleras activas</p>
        </div>
        <button
          onClick={() => setShowCrear(true)}
          className="rounded-lg bg-primary text-white px-4 py-2 text-sm font-semibold hover:bg-primary/90 transition-colors"
        >
          + Nueva natillera
        </button>
      </div>

      {isLoading && <Spinner className="mt-10" />}

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
          No se pudieron cargar las natilleras. Intenta de nuevo.
        </div>
      )}

      {!isLoading && !error && natilleras?.length === 0 && (
        <div className="text-center py-16">
          <p className="text-4xl mb-3">🏦</p>
          <p className="text-gray-700 font-medium">Aún no tienes natilleras</p>
          <p className="text-gray-500 text-sm mt-1">
            Crea una nueva o pide que te inviten a una existente.
          </p>
          <button
            onClick={() => setShowCrear(true)}
            className="mt-4 rounded-lg bg-primary text-white px-6 py-2 text-sm font-semibold hover:bg-primary/90 transition-colors"
          >
            Crear natillera
          </button>
        </div>
      )}

      {!isLoading && natilleras?.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {natilleras.map((n) => (
            <NatilleraCard key={n.id} natillera={n} />
          ))}
        </div>
      )}

      <Modal
        isOpen={showCrear}
        onClose={() => setShowCrear(false)}
        title="Nueva Natillera"
        size="lg"
      >
        <CrearNatilleraForm onSuccess={() => setShowCrear(false)} />
      </Modal>
    </AppLayout>
  );
}
