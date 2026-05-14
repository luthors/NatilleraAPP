import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import AppLayout from '../shared/components/AppLayout';
import Spinner from '../shared/components/Spinner';
import Modal from '../shared/components/Modal';
import Badge from '../shared/components/Badge';
import { useNatilleraDetalle } from '../features/natilleras/hooks/useNatilleras';
import { useActivarNatillera, useCerrarNatillera, useArchivarNatillera } from '../features/natilleras/hooks/useNatilleraMutations';
import SaldoFondo from '../features/natilleras/components/SaldoFondo';
import EstadoSocio from '../features/natilleras/components/EstadoSocio';
import SociosList from '../features/socios/components/SociosList';
import InvitarSocioForm from '../features/socios/components/InvitarSocioForm';
import HistorialPagos from '../features/pagos/components/HistorialPagos';
import RegistrarPagoForm from '../features/pagos/components/RegistrarPagoForm';
import PagosPendientesConfirmacion from '../features/pagos/components/PagosPendientesConfirmacion';
import DistribucionPreview from '../features/distribuciones/components/DistribucionPreview';
import useAuthStore from '../store/authStore';
import { useSaldoFondo, useEstadoSocio } from '../features/pagos/hooks/usePagos';
import formatCOP from '../shared/utils/formatCurrency';

const TABS = ['Resumen', 'Socios', 'Pagos', 'Reportes'];

const ESTADO_LABEL = {
  CONFIGURACION: 'Configuración',
  ACTIVA: 'Activa',
  EN_CIERRE: 'En cierre',
  CERRADA: 'Cerrada',
  ARCHIVADA: 'Archivada',
};
const ESTADO_VARIANT = {
  CONFIGURACION: 'gray',
  ACTIVA: 'success',
  EN_CIERRE: 'warning',
  CERRADA: 'error',
  ARCHIVADA: 'gray',
};

export default function NatilleraDetalle() {
  const { id } = useParams();
  const natilleraId = parseInt(id);
  const { usuario } = useAuthStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [tab, setTab] = useState('Resumen');
  const [showCerrarModal, setShowCerrarModal] = useState(false);
  const [cerrarData, setCerrarData] = useState(null);
  const [showInvitar, setShowInvitar] = useState(false);
  const [showRegistrarPago, setShowRegistrarPago] = useState(false);
  const [toast, setToast] = useState('');

  const { data: natillera, isLoading, error } = useNatilleraDetalle(natilleraId);
  const isAdmin = natillera?.admin_id === usuario?.id;

  const { data: saldo } = useSaldoFondo(natilleraId, isAdmin);
  const { data: estadoSocio } = useEstadoSocio(natilleraId, !isAdmin);

  const { mutate: activar, isPending: activando } = useActivarNatillera(natilleraId);
  const { mutate: cerrar, isPending: cerrando } = useCerrarNatillera(natilleraId);
  const { mutate: archivar, isPending: archivando } = useArchivarNatillera(natilleraId);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 4000);
  };

  const handleActivar = () => {
    activar(undefined, {
      onSuccess: () => showToast('Natillera activada correctamente'),
      onError: (e) => showToast(e?.response?.data?.detail || 'Error al activar'),
    });
  };

  const handleCerrar = (forzar = false) => {
    cerrar(
      { forzar },
      {
        onSuccess: (data) => {
          if (data?.requiere_confirmacion) {
            setCerrarData(data);
            setShowCerrarModal(true);
          } else {
            setShowCerrarModal(false);
            showToast('Natillera en proceso de cierre');
          }
        },
        onError: (e) => showToast(e?.response?.data?.detail || 'Error al cerrar'),
      }
    );
  };

  const handleArchivar = () => {
    archivar(undefined, {
      onSuccess: () => navigate('/dashboard'),
      onError: (e) => showToast(e?.response?.data?.detail || 'Error al archivar'),
    });
  };

  if (isLoading) return <AppLayout><Spinner className="mt-20" /></AppLayout>;
  if (error) return (
    <AppLayout>
      <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
        No se pudo cargar la natillera.
      </div>
    </AppLayout>
  );

  return (
    <AppLayout>
      {/* Toast */}
      {toast && (
        <div className="fixed bottom-4 right-4 z-50 bg-gray-900 text-white text-sm px-4 py-3 rounded-lg shadow-lg">
          {toast}
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-gray-900">{natillera.nombre}</h1>
            <Badge
              label={ESTADO_LABEL[natillera.estado] || natillera.estado}
              variant={ESTADO_VARIANT[natillera.estado] || 'gray'}
            />
          </div>
          {natillera.descripcion && (
            <p className="text-sm text-gray-500">{natillera.descripcion}</p>
          )}
          <p className="text-sm text-gray-600 mt-1">
            {formatCOP(natillera.monto_por_periodo)}{' '}
            <span className="capitalize">{natillera.periodicidad?.toLowerCase()}</span>
          </p>
        </div>

        {/* Admin actions */}
        {isAdmin && (
          <div className="flex flex-wrap gap-2">
            {natillera.estado === 'CONFIGURACION' && (
              <button
                onClick={handleActivar}
                disabled={activando}
                className="rounded-lg bg-green-600 text-white px-3 py-1.5 text-xs font-semibold hover:bg-green-700 disabled:opacity-60 transition-colors"
              >
                {activando ? 'Activando…' : 'Activar'}
              </button>
            )}
            {natillera.estado === 'ACTIVA' && (
              <>
                <button
                  onClick={() => setShowRegistrarPago(true)}
                  className="rounded-lg bg-primary text-white px-3 py-1.5 text-xs font-semibold hover:bg-primary/90 transition-colors"
                >
                  Registrar pago
                </button>
                <button
                  onClick={() => handleCerrar(false)}
                  disabled={cerrando}
                  className="rounded-lg bg-yellow-600 text-white px-3 py-1.5 text-xs font-semibold hover:bg-yellow-700 disabled:opacity-60 transition-colors"
                >
                  {cerrando ? 'Cerrando…' : 'Cerrar'}
                </button>
              </>
            )}
            {natillera.estado === 'CERRADA' && (
              <button
                onClick={handleArchivar}
                disabled={archivando}
                className="rounded-lg bg-gray-600 text-white px-3 py-1.5 text-xs font-semibold hover:bg-gray-700 disabled:opacity-60 transition-colors"
              >
                {archivando ? 'Archivando…' : 'Archivar'}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-5">
        <div className="flex gap-0">
          {TABS.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                tab === t
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      {tab === 'Resumen' && (
        <div className="space-y-4">
          {isAdmin && saldo && <SaldoFondo saldo={saldo} />}
          {!isAdmin && estadoSocio && <EstadoSocio estado={estadoSocio} />}
          <div className="bg-white rounded-xl border border-gray-200 p-5 grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-500 text-xs">Inicio</p>
              <p className="font-medium">{natillera.fecha_inicio}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Fin</p>
              <p className="font-medium">{natillera.fecha_fin}</p>
            </div>
            <div>
              <p className="text-gray-500 text-xs">Max socios</p>
              <p className="font-medium">{natillera.max_socios}</p>
            </div>
          </div>
        </div>
      )}

      {tab === 'Socios' && (
        <div className="space-y-4">
          {isAdmin && (
            <div className="flex justify-end">
              <button
                onClick={() => setShowInvitar(true)}
                className="rounded-lg bg-primary text-white px-4 py-2 text-sm font-semibold hover:bg-primary/90 transition-colors"
              >
                Invitar socio
              </button>
            </div>
          )}
          <SociosList natilleraId={natilleraId} isAdmin={isAdmin} />
        </div>
      )}

      {tab === 'Pagos' && (
        <div className="space-y-5">
          {isAdmin && (
            <>
              <PagosPendientesConfirmacion natilleraId={natilleraId} />
              <div className="flex justify-end">
                <button
                  onClick={() => setShowRegistrarPago(true)}
                  className="rounded-lg bg-primary text-white px-4 py-2 text-sm font-semibold hover:bg-primary/90 transition-colors"
                >
                  Registrar pago
                </button>
              </div>
            </>
          )}
          <HistorialPagos natilleraId={natilleraId} isAdmin={isAdmin} />
        </div>
      )}

      {tab === 'Reportes' && isAdmin && (
        <DistribucionPreview natilleraId={natilleraId} natillera={natillera} />
      )}
      {tab === 'Reportes' && !isAdmin && (
        <div className="text-sm text-gray-500">Los reportes están disponibles para el administrador.</div>
      )}

      {/* Cerrar modal */}
      <Modal isOpen={showCerrarModal} onClose={() => setShowCerrarModal(false)} title="Confirmar cierre">
        {cerrarData && (
          <div className="space-y-4">
            <div className="rounded-md bg-yellow-50 border border-yellow-200 p-3 text-sm text-yellow-800">
              {cerrarData.mensaje}
            </div>
            {cerrarData.socios_en_mora?.length > 0 && (
              <p className="text-sm text-gray-600">
                Socios con pagos pendientes: <strong>{cerrarData.socios_en_mora.length}</strong>
              </p>
            )}
            <div className="flex gap-3">
              <button
                onClick={() => setShowCerrarModal(false)}
                className="flex-1 rounded-lg border border-gray-300 text-gray-700 py-2 text-sm font-semibold hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => handleCerrar(true)}
                disabled={cerrando}
                className="flex-1 rounded-lg bg-yellow-600 text-white py-2 text-sm font-semibold hover:bg-yellow-700 disabled:opacity-60 transition-colors"
              >
                {cerrando ? 'Cerrando…' : 'Confirmar cierre'}
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Invitar modal */}
      <Modal isOpen={showInvitar} onClose={() => setShowInvitar(false)} title="Invitar socio">
        <InvitarSocioForm
          natilleraId={natilleraId}
          onSuccess={() => { setShowInvitar(false); showToast('Invitación enviada'); }}
        />
      </Modal>

      {/* Registrar pago modal */}
      <Modal isOpen={showRegistrarPago} onClose={() => setShowRegistrarPago(false)} title="Registrar pago">
        <RegistrarPagoForm
          natilleraId={natilleraId}
          isAdmin={isAdmin}
          onSuccess={() => { setShowRegistrarPago(false); showToast('Pago registrado'); queryClient.invalidateQueries({ queryKey: ['pagos', natilleraId] }); }}
        />
      </Modal>
    </AppLayout>
  );
}
