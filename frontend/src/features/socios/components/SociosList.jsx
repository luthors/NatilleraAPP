import { useState } from 'react';
import { useSocios, useSuspenderSocio, useReactivarSocio, useEliminarSocio } from '../hooks/useSocios';
import Spinner from '../../../shared/components/Spinner';
import Badge from '../../../shared/components/Badge';
import Modal from '../../../shared/components/Modal';

const ESTADO_VARIANT = { ACTIVO: 'success', SUSPENDIDO: 'warning', RETIRADO: 'gray' };

export default function SociosList({ natilleraId, isAdmin }) {
  const { data: socios, isLoading } = useSocios(natilleraId);
  const { mutate: suspender, isPending: suspendiendo } = useSuspenderSocio(natilleraId);
  const { mutate: reactivar, isPending: reactivando } = useReactivarSocio(natilleraId);
  const { mutate: eliminar, isPending: eliminando } = useEliminarSocio(natilleraId);

  const [suspenderModal, setSuspenderModal] = useState(null); // socio object
  const [razon, setRazon] = useState('');
  const [error, setError] = useState('');

  if (isLoading) return <Spinner />;
  if (!socios?.length) return <p className="text-sm text-gray-500">No hay socios registrados.</p>;

  const handleSuspender = () => {
    if (!razon.trim()) { setError('La razón es obligatoria.'); return; }
    suspender(
      { socioId: suspenderModal.id, razon },
      {
        onSuccess: () => { setSuspenderModal(null); setRazon(''); setError(''); },
        onError: (e) => setError(e?.response?.data?.detail || 'Error al suspender'),
      }
    );
  };

  return (
    <>
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Socio</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Estado</th>
              {isAdmin && <th className="text-right px-4 py-3 font-medium text-gray-600">Acciones</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {socios.map((s) => (
              <tr key={s.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <p className="font-medium text-gray-900">{s.usuario?.nombre || `Socio #${s.id}`}</p>
                  <p className="text-xs text-gray-400">{s.usuario?.email}</p>
                </td>
                <td className="px-4 py-3">
                  <Badge label={s.estado} variant={ESTADO_VARIANT[s.estado] || 'gray'} />
                </td>
                {isAdmin && (
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-2">
                      {s.estado === 'ACTIVO' && (
                        <button
                          onClick={() => { setSuspenderModal(s); setRazon(''); setError(''); }}
                          className="text-xs text-yellow-700 hover:text-yellow-900 font-medium"
                        >
                          Suspender
                        </button>
                      )}
                      {s.estado === 'SUSPENDIDO' && (
                        <button
                          onClick={() => reactivar({ socioId: s.id })}
                          disabled={reactivando}
                          className="text-xs text-green-700 hover:text-green-900 font-medium disabled:opacity-60"
                        >
                          Reactivar
                        </button>
                      )}
                      <button
                        onClick={() => {
                          if (confirm(`¿Eliminar a ${s.usuario?.nombre || 'este socio'}?`)) {
                            eliminar({ socioId: s.id });
                          }
                        }}
                        disabled={eliminando}
                        className="text-xs text-red-600 hover:text-red-800 font-medium disabled:opacity-60"
                      >
                        Eliminar
                      </button>
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal
        isOpen={!!suspenderModal}
        onClose={() => setSuspenderModal(null)}
        title={`Suspender a ${suspenderModal?.usuario?.nombre || 'socio'}`}
      >
        <div className="space-y-3">
          {error && (
            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">{error}</div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Razón *</label>
            <textarea
              value={razon}
              onChange={(e) => setRazon(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none"
              placeholder="Explica el motivo de la suspensión"
            />
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setSuspenderModal(null)}
              className="flex-1 rounded-lg border border-gray-300 text-gray-700 py-2 text-sm font-semibold hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleSuspender}
              disabled={suspendiendo}
              className="flex-1 rounded-lg bg-yellow-600 text-white py-2 text-sm font-semibold hover:bg-yellow-700 disabled:opacity-60"
            >
              {suspendiendo ? 'Suspendiendo…' : 'Suspender'}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
