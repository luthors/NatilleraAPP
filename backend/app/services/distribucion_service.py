"""
DistribucionService — final fund distribution.

References:
- HU-06-02: distribución final
- RN-04: socios en mora no reciben distribuciones parciales
- RN-07: distribución final solo cuando estado = EN_CIERRE
- RN-10: saldo = aportes CONFIRMADOS − distribuciones
"""
from datetime import date
from decimal import Decimal, ROUND_DOWN

from app.core.events import emit
from app.core.exceptions import (
    NatilleraNoEncontradaError,
    NatilleraEstadoInvalidoError,
    AccesoNoAutorizadoError,
    DistribucionNoPermitidaError,
)
from app.models.distribucion import Distribucion, TipoDistribucion
from app.models.natillera import EstadoNatillera
from app.repositories.natillera_repo import NatilleraRepository
from app.repositories.socio_repo import SocioRepository
from app.repositories.pago_repo import PagoRepository
from app.repositories.audit_repo import AuditRepository
from app.services.saldo_service import SaldoService


class DistribucionService:

    def __init__(
        self,
        natillera_repo: NatilleraRepository,
        socio_repo: SocioRepository,
        pago_repo: PagoRepository,
        audit_repo: AuditRepository,
        saldo_service: SaldoService,
    ) -> None:
        self.natillera_repo = natillera_repo
        self.socio_repo = socio_repo
        self.pago_repo = pago_repo
        self.audit_repo = audit_repo
        self.saldo_service = saldo_service

    # ── Preview ───────────────────────────────────────────────────────────────

    def preview_distribucion_final(self, natillera_id: int, admin_id: int) -> dict:
        """
        Calculate and return the distribution plan without executing it.
        Admin must review this before calling ejecutar_distribucion_final.
        """
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(natillera_id)
        if natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError()
        if natillera.estado != EstadoNatillera.EN_CIERRE:
            raise DistribucionNoPermitidaError()

        saldo_info = self.saldo_service.calcular_saldo_fondo(natillera_id)
        saldo_total: Decimal = saldo_info["saldo_total"]

        socios_activos = self.socio_repo.get_by_natillera(natillera_id, solo_activos=True)
        if not socios_activos:
            return {"natillera_id": natillera_id, "saldo_total": saldo_total, "total_socios_activos": 0, "distribucion": []}

        monto_por_socio = (saldo_total / len(socios_activos)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

        distribucion = []
        for socio in socios_activos:
            distribucion.append({
                "socio_id": socio.id,
                "nombre_socio": socio.usuario.nombre if socio.usuario else f"Socio {socio.id}",
                "monto_base": monto_por_socio,
                "total_a_recibir": monto_por_socio,
            })

        return {
            "natillera_id": natillera_id,
            "saldo_total": saldo_total,
            "total_socios_activos": len(socios_activos),
            "distribucion": distribucion,
        }

    # ── Ejecutar ──────────────────────────────────────────────────────────────

    def ejecutar_distribucion_final(self, natillera_id: int, admin_id: int) -> list[Distribucion]:
        """
        Execute the final distribution.
        - natillera must be in EN_CIERRE (RN-07).
        - Divides fund equally among active socios.
        - Moves natillera to CERRADA.
        - Emits distribucion.ejecutada for each socio notification.
        """
        preview = self.preview_distribucion_final(natillera_id, admin_id)
        natillera = self.natillera_repo.get_by_id(natillera_id)

        distribuciones: list[Distribucion] = []

        for item in preview["distribucion"]:
            dist = Distribucion(
                natillera_id=natillera_id,
                socio_id=item["socio_id"],
                monto=item["total_a_recibir"],
                tipo=TipoDistribucion.FINAL,
                fecha=date.today(),
            )
            self.natillera_repo.db.add(dist)
            self.natillera_repo.db.flush()
            distribuciones.append(dist)

        # Move natillera to CERRADA
        self.natillera_repo.update_estado(natillera, EstadoNatillera.CERRADA)

        self.audit_repo.registrar(
            accion="EJECUTAR_DISTRIBUCION_FINAL",
            entidad="Natillera",
            entidad_id=natillera_id,
            usuario_id=admin_id,
            datos_nuevos={
                "total_distribuido": str(preview["saldo_total"]),
                "socios": len(distribuciones),
            },
        )

        emit("distribucion.ejecutada", natillera=natillera, distribuciones=distribuciones)
        return distribuciones
