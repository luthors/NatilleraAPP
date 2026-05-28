import { useState } from 'react';
import { usePagos, useRevertirPago } from '../hooks/usePagos';
import Spinner from '../../../shared/components/Spinner';
import Badge from '../../../shared/components/Badge';
import Modal from '../../../shared/components/Modal';
import formatCOP from '../../../shared/utils/formatCurrency';

const ESTADO_VARIANT = {
  CONFIRMADO: 'success',
  PENDIENTE_CONFIRMACION: 'warning',
  RECHAZADO: 'error',
  REVERTIDO: 'gray',
};

export default function HistorialPagos({ natilleraId, isAdmin }) {
  const { data: pagos, isLoading } = usePagos(natilleraId, isAdmin);
  const { mutate: revertir, isPending: revirtiendo } = useRevertirPago(natilleraId);

  const [revertirModal, setRevertirModal] = useState(null);
  const [justificacion, setJustificacion] = useState('');
  const [modalError, setModalError] = useState('');

  if (isLoading) return <Spinner />;
  if (!pagos?.length) return <p className="text-sm text-gray-500 py-4">No hay pagos registrados.</p>;

  const handleRevertir = () => {
    if (!justificacion.trim()) { setModalError('La justificación es obligatoria.'); return; }
    revertir(
      { pagoId: revertirModal.id, justificacion },
      {
        onSuccess: () => { setRevertirModal(null); setJustificacion(''); setModalError(''); },
        onError: (e) => setModalError(e?.response?.data?.detail || 'Error'),
      }
    );
  };

  return (
    <>
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {isAdmin && <th className="text-left px-4 py-3 font-medium text-gray-600">Socio</th>}
              <th className="text-left px-4 py-3 font-medium text-gray-600">Período</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Monto</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Estado</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Método</th>
              {isAdmin && <th className="text-right px-4 py-3 font-medium text-gray-600">Acciones</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {pagos.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50">
                {isAdmin && (
                  <td className="px-4 py-3 text-gray-900 font-medium">
                    {p.socio?.usuario?.nombre || `Socio #${p.socio_id}`}
                  </td>
                )}
                <td className="px-4 py-3 text-gray-700">
                  {p.periodo?.nombre || `Período #${p.periodo_id}`}
                </td>
                <td className="px-4 py-3 font-semibold text-gray-900">{formatCOP(p.monto)}</td>
                <td className="px-4 py-3">
                  <Badge label={p.estado} variant={ESTADO_VARIANT[p.estado] || 'gray'} />
                </td>
                <td className="px-4 py-3 text-gray-500 capitalize">{p.metodo?.toLowerCase()}</td>
                {isAdmin && (
                  <td className="px-4 py-3 text-right">
                    {p.estado === 'CONFIRMADO' && (
                      <button
                        onClick={() => { setRevertirModal(p); setJustificacion(''); setModalError(''); }}
                        className="text-xs text-red-600 hover:text-red-800 font-medium"
                      >
                        Revertir
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal isOpen={!!revertirModal} onClose={() => setRevertirModal(null)} title="Revertir pago">
        <div className="space-y-3">
          {modalError && (
            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">{modalError}</div>
          )}
          <p className="text-sm text-gray-600">
            Pago de <strong>{revertirModal?.socio?.usuario?.nombre}</strong> por{' '}
            <strong>{formatCOP(revertirModal?.monto)}</strong>. Esta acción no se puede deshacer.
          </p>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Justificación *</label>
            <textarea
              value={justificacion}
              onChange={(e) => setJustificacion(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none"
              placeholder="Explica por qué se revierte este pago"
            />
          </div>
          <div className="flex gap-3">
            <button onClick={() => setRevertirModal(null)} className="flex-1 rounded-lg border border-gray-300 text-gray-700 py-2 text-sm font-semibold hover:bg-gray-50">
              Cancelar
            </button>
            <button
              onClick={handleRevertir}
              disabled={revirtiendo}
              className="flex-1 rounded-lg bg-red-600 text-white py-2 text-sm font-semibold hover:bg-red-700 disabled:opacity-60"
            >
              {revirtiendo ? 'Revirtiendo…' : 'Revertir pago'}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
