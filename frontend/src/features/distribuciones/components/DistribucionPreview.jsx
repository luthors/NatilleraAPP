import { useState } from 'react';
import { useDistribucionPreview } from '../hooks/useDistribucion';
import { useEjecutarDistribucion } from '../hooks/useDistribucion';
import Spinner from '../../../shared/components/Spinner';
import Modal from '../../../shared/components/Modal';
import formatCOP from '../../../shared/utils/formatCurrency';

export default function DistribucionPreview({ natilleraId, natillera }) {
  const puedeDistribuir = natillera?.estado === 'EN_CIERRE';
  const { data: preview, isLoading, error } = useDistribucionPreview(natilleraId, puedeDistribuir);
  const { mutate: ejecutar, isPending: ejecutando } = useEjecutarDistribucion(natilleraId);

  const [showConfirmar, setShowConfirmar] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [execError, setExecError] = useState('');

  const handleEjecutar = () => {
    ejecutar(
      { confirmado: true },
      {
        onSuccess: (data) => { setResultado(data); setShowConfirmar(false); },
        onError: (e) => { setExecError(e?.response?.data?.detail || 'Error al ejecutar'); },
      }
    );
  };

  if (!puedeDistribuir) {
    return (
      <div className="bg-gray-50 rounded-xl border border-gray-200 p-6 text-center">
        <p className="text-gray-500 text-sm">
          La distribución final solo está disponible cuando la natillera está en estado{' '}
          <strong>EN_CIERRE</strong>. Estado actual:{' '}
          <strong>{natillera?.estado}</strong>.
        </p>
      </div>
    );
  }

  if (isLoading) return <Spinner />;

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
        {error?.response?.data?.detail || 'No se pudo cargar el preview.'}
      </div>
    );
  }

  if (resultado) {
    return (
      <div className="space-y-4">
        <div className="rounded-md bg-green-50 border border-green-200 p-4 text-sm text-green-800">
          Distribución ejecutada exitosamente. La natillera está ahora CERRADA.
        </div>
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Socio</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Monto recibido</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {resultado.map((d) => (
                <tr key={d.id}>
                  <td className="px-4 py-3 text-gray-900">{d.socio_nombre || `Socio #${d.socio_id}`}</td>
                  <td className="px-4 py-3 text-right font-semibold text-green-700">{formatCOP(d.monto)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">Preview de distribución final</h3>
          <button
            onClick={() => setShowConfirmar(true)}
            className="rounded-lg bg-green-600 text-white px-4 py-2 text-sm font-semibold hover:bg-green-700 transition-colors"
          >
            Ejecutar distribución
          </button>
        </div>

        {preview && (
          <>
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-sm">
              <p className="font-semibold text-green-800">
                Total a distribuir: {formatCOP(preview.monto_total)}
              </p>
              {preview.saldo_actual && (
                <p className="text-green-700 text-xs mt-1">
                  Saldo actual del fondo: {formatCOP(preview.saldo_actual)}
                </p>
              )}
            </div>

            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Socio</th>
                    <th className="text-right px-4 py-3 font-medium text-gray-600">Monto estimado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {preview.socios?.map((s, i) => (
                    <tr key={i}>
                      <td className="px-4 py-3 text-gray-900">{s.nombre || s.socio_nombre || `Socio #${s.socio_id}`}</td>
                      <td className="px-4 py-3 text-right font-semibold text-gray-900">{formatCOP(s.monto)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>

      <Modal isOpen={showConfirmar} onClose={() => setShowConfirmar(false)} title="Confirmar distribución">
        <div className="space-y-4">
          {execError && (
            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">{execError}</div>
          )}
          <div className="rounded-md bg-yellow-50 border border-yellow-200 p-3 text-sm text-yellow-800">
            Esta acción distribuirá el fondo entre todos los socios y cerrará definitivamente la natillera.
            <strong> Esta operación no se puede deshacer.</strong>
          </div>
          <p className="text-sm text-gray-700">
            Total a distribuir: <strong>{formatCOP(preview?.monto_total)}</strong>
          </p>
          <div className="flex gap-3">
            <button onClick={() => setShowConfirmar(false)} className="flex-1 rounded-lg border border-gray-300 text-gray-700 py-2 text-sm font-semibold hover:bg-gray-50">
              Cancelar
            </button>
            <button
              onClick={handleEjecutar}
              disabled={ejecutando}
              className="flex-1 rounded-lg bg-green-600 text-white py-2 text-sm font-semibold hover:bg-green-700 disabled:opacity-60"
            >
              {ejecutando ? 'Ejecutando…' : 'Confirmar y ejecutar'}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
