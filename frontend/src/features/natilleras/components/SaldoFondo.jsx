import formatCOP from '../../../shared/utils/formatCurrency';

export default function SaldoFondo({ saldo }) {
  if (!saldo) return null;
  const { saldo_total, aportes_periodo_actual, pendientes_periodo, total_distribuido } = saldo;

  return (
    <div className="bg-gradient-to-br from-primary to-primary/80 rounded-xl p-5 text-white">
      <p className="text-sm font-medium text-white/80 mb-1">Saldo del fondo</p>
      <p className="text-3xl font-bold">{formatCOP(saldo_total)}</p>
      <div className="mt-4 grid grid-cols-3 gap-3 text-center text-xs">
        <div>
          <p className="text-white/70">Recibidos hoy</p>
          <p className="font-semibold">{formatCOP(aportes_periodo_actual)}</p>
        </div>
        <div>
          <p className="text-white/70">Pendientes</p>
          <p className="font-semibold">{formatCOP(pendientes_periodo)}</p>
        </div>
        <div>
          <p className="text-white/70">Distribuido</p>
          <p className="font-semibold">{formatCOP(total_distribuido)}</p>
        </div>
      </div>
    </div>
  );
}
