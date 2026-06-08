"""
SaldoService — fund balance calculation and mora detection.

References:
- HU-05-01: saldo del fondo (admin)
- HU-05-02: estado de cuenta personal (socio)
- HU-05-04: alerta automática de mora (scheduler)
- RN-10: saldo = aportes CONFIRMADOS − distribuciones
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.events import emit
from app.models.pago import Pago, EstadoPago
from app.models.socio import Periodo, EstadoPeriodo, Socio, EstadoSocio
from app.models.distribucion import Distribucion
from app.repositories.natillera_repo import NatilleraRepository, PeriodoRepository
from app.repositories.socio_repo import SocioRepository
from app.repositories.pago_repo import PagoRepository
from app.core.exceptions import NatilleraNoEncontradaError


class SaldoService:

    def __init__(
        self,
        natillera_repo: NatilleraRepository,
        periodo_repo: PeriodoRepository,
        socio_repo: SocioRepository,
        pago_repo: PagoRepository,
        db: Session,
    ) -> None:
        self.natillera_repo = natillera_repo
        self.periodo_repo = periodo_repo
        self.socio_repo = socio_repo
        self.pago_repo = pago_repo
        self.db = db

    # ── Saldo del fondo ───────────────────────────────────────────────────────

    def calcular_saldo_fondo(self, natillera_id: int) -> dict:
        """
        Return the fund balance breakdown for a natillera.

        RN-10: saldo = sum(CONFIRMADO) − sum(distribuciones)
        """
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(natillera_id)

        total_confirmado = self.pago_repo.sum_confirmados(natillera_id)

        total_distribuido = self.db.query(
            func.coalesce(func.sum(Distribucion.monto), 0)
        ).filter(Distribucion.natillera_id == natillera_id).scalar()
        total_distribuido = Decimal(str(total_distribuido))

        saldo_total = total_confirmado - total_distribuido

        # Current period stats
        periodo_actual = self.periodo_repo.get_periodo_actual(natillera_id)
        aportes_periodo_actual = Decimal("0")
        socios_activos = self.socio_repo.count_activos(natillera_id)
        aportes_pendientes = Decimal("0")

        if periodo_actual:
            aportes_periodo_actual = Decimal(str(
                self.db.query(func.coalesce(func.sum(Pago.monto), 0))
                .filter(
                    Pago.natillera_id == natillera_id,
                    Pago.periodo_id == periodo_actual.id,
                    Pago.estado == EstadoPago.CONFIRMADO,
                )
                .scalar()
            ))
            aportes_pendientes = (
                natillera.monto_por_periodo * socios_activos
            ) - aportes_periodo_actual

        return {
            "natillera_id": natillera_id,
            "saldo_total": saldo_total,
            "aportes_periodo_actual": aportes_periodo_actual,
            "aportes_pendientes_periodo": max(aportes_pendientes, Decimal("0")),
            "total_distribuido": total_distribuido,
        }

    # ── Estado personal del socio ─────────────────────────────────────────────

    def calcular_estado_socio(self, socio_id: int, natillera_id: int) -> dict:
        """Return the personal account status for a socio."""
        total_aportado = self.pago_repo.sum_confirmados_por_socio(socio_id, natillera_id)
        tiene_mora = self.socio_repo.tiene_mora(socio_id, natillera_id)

        # Count paid and pending periods
        periodos = self.periodo_repo.get_by_natillera(natillera_id)
        periodos_pagados = 0
        monto_en_mora = Decimal("0")

        natillera = self.natillera_repo.get_by_id(natillera_id)

        for p in periodos:
            if p.estado in (EstadoPeriodo.ABIERTO, EstadoPeriodo.CERRADO):
                tiene_pago = self.db.query(Pago).filter(
                    Pago.socio_id == socio_id,
                    Pago.periodo_id == p.id,
                    Pago.estado == EstadoPago.CONFIRMADO,
                ).count() > 0

                if tiene_pago:
                    periodos_pagados += 1
                elif p.fecha_fin < date.today():
                    monto_en_mora += natillera.monto_por_periodo

        periodos_con_pago_obligatorio = sum(
            1 for p in periodos if p.estado in (EstadoPeriodo.ABIERTO, EstadoPeriodo.CERRADO)
        )
        periodos_pendientes = periodos_con_pago_obligatorio - periodos_pagados

        periodo_actual = self.periodo_repo.get_periodo_actual(natillera_id)

        return {
            "socio_id": socio_id,
            "natillera_id": natillera_id,
            "total_aportado": total_aportado,
            "periodos_pagados": periodos_pagados,
            "periodos_pendientes": max(periodos_pendientes, 0),
            "monto_en_mora": monto_en_mora,
            "tiene_mora": tiene_mora,
            "proximo_pago_fecha": str(periodo_actual.fecha_fin) if periodo_actual else None,
            "proximo_pago_monto": natillera.monto_por_periodo if periodo_actual else None,
        }

    # ── Detección de mora (llamada por el scheduler) ──────────────────────────

    def detectar_y_notificar_mora(self, natillera_id: int) -> list[int]:
        """
        Find socios with overdue periods (more than 3 days past fecha_fin without payment).
        Emit 'socio.en_mora' for each one.

        Returns a list of socio_ids that are now in mora.
        """
        from datetime import timedelta
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            return []

        periodos_vencidos = self.periodo_repo.get_periodos_vencidos_sin_pago(natillera_id)
        en_mora: list[int] = []
        mora_counts: dict[int, int] = {}

        socios = self.socio_repo.get_by_natillera(natillera_id, solo_activos=True)

        for periodo in periodos_vencidos:
            dias_vencido = (date.today() - periodo.fecha_fin).days
            if dias_vencido < 3:
                continue

            for socio in socios:
                tiene_pago = self.db.query(Pago).filter(
                    Pago.socio_id == socio.id,
                    Pago.periodo_id == periodo.id,
                    Pago.estado == EstadoPago.CONFIRMADO,
                ).count() > 0

                if not tiene_pago:
                    if socio.id not in mora_counts:
                        mora_counts[socio.id] = 0
                        en_mora.append(socio.id)
                    mora_counts[socio.id] += 1

        for socio_id in en_mora:
            socio = next((s for s in socios if s.id == socio_id), None)
            if socio:
                emit("socio.en_mora", socio=socio, natillera=natillera, periodos_mora=mora_counts[socio_id])

        return en_mora
