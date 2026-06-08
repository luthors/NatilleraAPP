import { useState } from 'react';
import { usePagosPendientes, useConfirmarPago, useRechazarPago } from '../hooks/usePagos';
import Spinner from '../../../shared/components/Spinner';
import Modal from '../../../shared/components/Modal';
import formatCOP from '../../../shared/utils/formatCurrency';

export default function PagosPendientesConfirmacion({ natilleraId }) {
  const { data: pendientes, isLoading } = usePagosPendientes(natilleraId);
  const { mutate: confirmar, isPending: confirmando } = useConfirmarPago(natilleraId);
  const { mutate: rechazar, isPending: rechazando } = useRechazarPago(natilleraId);

  const [rechazarModal, setRechazarModal] = useState(null);
  const [razon, setRazon] = useState('');
  const [modalError, setModalError] = useState('');

  if (isLoading) return <Spinner size="sm" />;
  if (!pendientes?.length) return null;

  const handleRechazar = () => {
    if (!razon.trim()) { setModalError('La razón es obligatoria.'); return; }
    rechazar(
      { pagoId: rechazarModal.id, razon },
      {
        onSuccess: () => { setRechazarModal(null); setRazon(''); setModalError(''); },
        onError: (e) => setModalError(e?.response?.data?.detail || 'Error'),
      }
    );
  };

  return (
    <>
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">
          Pagos pendientes de confirmación ({pendientes.length})
        </h3>
        <div className="space-y-2">
          {pendientes.map((p) => (
            <div
              key={p.id}
              className="flex items-center justify-between bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-3"
            >
              <div className="text-sm">
                <p className="font-medium text-gray-900">
                  {p.socio?.usuario?.nombre || `Socio #${p.socio_id}`}
                </p>
                <p className="text-gray-500 text-xs">
                  {formatCOP(p.monto)} — {p.metodo}
                  {p.referencia && ` — Ref: ${p.referencia}`}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => confirmar({ pagoId: p.id })}
                  disabled={confirmando}
                  className="text-xs rounded bg-green-600 text-white px-3 py-1.5 font-semibold hover:bg-green-700 disabled:opacity-60 transition-colors"
                >
                  Confirmar
                </button>
                <button
                  onClick={() => { setRechazarModal(p); setRazon(''); setModalError(''); }}
                  className="text-xs rounded bg-red-100 text-red-700 px-3 py-1.5 font-semibold hover:bg-red-200 transition-colors"
                >
                  Rechazar
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <Modal
        isOpen={!!rechazarModal}
        onClose={() => setRechazarModal(null)}
        title="Rechazar pago"
      >
        <div className="space-y-3">
          {modalError && (
            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">{modalError}</div>
          )}
          <p className="text-sm text-gray-600">
            Pago de <strong>{rechazarModal?.socio?.usuario?.nombre}</strong> por{' '}
            <strong>{formatCOP(rechazarModal?.monto)}</strong>
          </p>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Razón del rechazo *</label>
            <textarea
              value={razon}
              onChange={(e) => setRazon(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none"
              placeholder="Explica por qué se rechaza el pago"
            />
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setRechazarModal(null)}
              className="flex-1 rounded-lg border border-gray-300 text-gray-700 py-2 text-sm font-semibold hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              onClick={handleRechazar}
              disabled={rechazando}
              className="flex-1 rounded-lg bg-red-600 text-white py-2 text-sm font-semibold hover:bg-red-700 disabled:opacity-60"
            >
              {rechazando ? 'Rechazando…' : 'Rechazar pago'}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
