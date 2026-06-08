import formatCOP from '../../../shared/utils/formatCurrency';
import Badge from '../../../shared/components/Badge';

export default function EstadoSocio({ estado }) {
  if (!estado) return null;
  const { total_aportado, periodos_al_dia, periodos_en_mora, monto_en_mora } = estado;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-3">
      <h3 className="font-semibold text-gray-900">Mi estado de cuenta</h3>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <p className="text-gray-500 text-xs mb-1">Total aportado</p>
          <p className="font-bold text-gray-900">{formatCOP(total_aportado)}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <p className="text-gray-500 text-xs mb-1">Períodos al día</p>
          <p className="font-bold text-green-700">{periodos_al_dia}</p>
        </div>
        {periodos_en_mora > 0 && (
          <div className="col-span-2 bg-red-50 rounded-lg p-3 flex items-center justify-between">
            <span className="text-red-700 text-sm font-medium">
              {periodos_en_mora} período{periodos_en_mora > 1 ? 's' : ''} en mora
            </span>
            <Badge label={formatCOP(monto_en_mora)} variant="error" />
          </div>
        )}
      </div>
    </div>
  );
}
