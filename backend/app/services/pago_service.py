"""
PagoService — register, confirm, reject, revert payments.

Key invariants enforced:
- RN-06: Confirmed payments are never deleted, only REVERTIDO.
- RN-10: Fund balance is the sum of CONFIRMADO payments minus distributions.
- All operations that modify fund balance are atomic (one SQLAlchemy session).

References: HU-04-01 to HU-04-04
"""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional

from app.core.events import emit
from app.core.exceptions import (
    PagoNoEncontradoError,
    PagoYaExisteError,
    PagoYaConfirmadoError,
    PagoNoConfirmadoError,
    MontoIncorrectoError,
    AccesoNoAutorizadoError,
    NatilleraNoEncontradaError,
    SocioNoEncontradoError,
    PeriodoNoEncontradoError,
)
from app.models.pago import Pago, EstadoPago, MetodoPago
from app.repositories.pago_repo import PagoRepository
from app.repositories.natillera_repo import NatilleraRepository, PeriodoRepository
from app.repositories.socio_repo import SocioRepository
from app.repositories.audit_repo import AuditRepository


class PagoService:

    def __init__(
        self,
        pago_repo: PagoRepository,
        natillera_repo: NatilleraRepository,
        periodo_repo: PeriodoRepository,
        socio_repo: SocioRepository,
        audit_repo: AuditRepository,
    ) -> None:
        self.pago_repo = pago_repo
        self.natillera_repo = natillera_repo
        self.periodo_repo = periodo_repo
        self.socio_repo = socio_repo
        self.audit_repo = audit_repo

    # ── Admin registers payment ───────────────────────────────────────────────

    def registrar_por_admin(
        self,
        natillera_id: int,
        socio_id: int,
        periodo_id: int,
        monto: Decimal,
        metodo: MetodoPago,
        admin_id: int,
        referencia: Optional[str] = None,
        forzar: bool = False,
    ) -> Pago:
        """
        Admin confirms a cash payment on behalf of a socio.

        The payment is immediately CONFIRMADO (no pending step).
        If the amount differs from the natillera standard, the admin must
        pass forzar=True to acknowledge the discrepancy.

        All changes (payment + audit log) happen in one SQLAlchemy session
        managed by get_db() — fully atomic (Unit of Work).
        """
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(natillera_id)
        if natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError()

        socio = self.socio_repo.get_by_id(socio_id)
        if socio is None or socio.natillera_id != natillera_id:
            raise SocioNoEncontradoError(socio_id)

        periodo = self.periodo_repo.get_by_id(periodo_id)
        if periodo is None or periodo.natillera_id != natillera_id:
            raise PeriodoNoEncontradoError(periodo_id)

        if self.pago_repo.pago_activo_existe(socio_id, periodo_id):
            raise PagoYaExisteError()

        # Amount check (warn, not block — unless forzar=False)
        if monto != natillera.monto_por_periodo and not forzar:
            raise MontoIncorrectoError(
                str(natillera.monto_por_periodo), str(monto)
            )

        pago = Pago(
            natillera_id=natillera_id,
            socio_id=socio_id,
            periodo_id=periodo_id,
            monto=monto,
            metodo=metodo,
            estado=EstadoPago.CONFIRMADO,
            referencia=referencia,
            gestionado_por_id=admin_id,
            gestionado_at=datetime.now(timezone.utc),
        )
        self.pago_repo.save(pago)

        self.audit_repo.registrar(
            accion="REGISTRAR_PAGO_ADMIN",
            entidad="Pago",
            entidad_id=pago.id,
            usuario_id=admin_id,
            datos_nuevos={"monto": str(monto), "estado": EstadoPago.CONFIRMADO, "socio_id": socio_id},
        )

        emit("pago.confirmado", pago=pago, socio=socio)
        return pago

    # ── Socio submits payment ─────────────────────────────────────────────────

    def registrar_por_socio(
        self,
        natillera_id: int,
        usuario_id: int,
        periodo_id: int,
        metodo: MetodoPago,
        referencia: Optional[str] = None,
        comprobante_url: Optional[str] = None,
    ) -> "Pago":
        """
        Socio submits a payment for admin confirmation.
        Accepts usuario_id and resolves to the Socio record internally.
        State is PENDIENTE_CONFIRMACION.
        """
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(natillera_id)

        # Resolve usuario → socio
        socio = self.socio_repo.get_by_usuario_y_natillera(usuario_id, natillera_id)
        if socio is None or not socio.esta_activo():
            raise SocioNoEncontradoError(usuario_id)

        periodo = self.periodo_repo.get_by_id(periodo_id)
        if periodo is None or periodo.natillera_id != natillera_id:
            raise PeriodoNoEncontradoError(periodo_id)

        if self.pago_repo.pago_activo_existe(socio.id, periodo_id):
            raise PagoYaExisteError()

        pago = Pago(
            natillera_id=natillera_id,
            socio_id=socio.id,
            periodo_id=periodo_id,
            monto=natillera.monto_por_periodo,
            metodo=metodo,
            estado=EstadoPago.PENDIENTE_CONFIRMACION,
            referencia=referencia,
            comprobante_url=comprobante_url,
        )
        self.pago_repo.save(pago)

        emit("pago.pendiente_confirmacion", pago=pago, natillera=natillera)
        return pago

    # ── Admin confirms ────────────────────────────────────────────────────────

    def confirmar(self, pago_id: int, admin_id: int, natillera_id: Optional[int] = None) -> Pago:
        """
        Admin confirms a pending payment.
        Raises PagoYaConfirmadoError if already confirmed (RN-06).
        """
        pago = self._get_pago_for_admin(pago_id, admin_id)

        if natillera_id is not None and pago.natillera_id != natillera_id:
            raise AccesoNoAutorizadoError()

        if pago.estado == EstadoPago.CONFIRMADO:
            raise PagoYaConfirmadoError(pago_id)

        datos_anteriores = {"estado": pago.estado}
        self.pago_repo.update(
            pago,
            estado=EstadoPago.CONFIRMADO,
            gestionado_por_id=admin_id,
            gestionado_at=datetime.now(timezone.utc),
        )

        self.audit_repo.registrar(
            accion="CONFIRMAR_PAGO",
            entidad="Pago",
            entidad_id=pago_id,
            usuario_id=admin_id,
            datos_anteriores=datos_anteriores,
            datos_nuevos={"estado": EstadoPago.CONFIRMADO},
        )

        emit("pago.confirmado", pago=pago, socio=pago.socio)
        return pago

    # ── Admin rejects ─────────────────────────────────────────────────────────

    def rechazar(self, pago_id: int, admin_id: int, razon: str, natillera_id: Optional[int] = None) -> Pago:
        pago = self._get_pago_for_admin(pago_id, admin_id)
        if natillera_id is not None and pago.natillera_id != natillera_id:
            raise AccesoNoAutorizadoError()
        datos_anteriores = {"estado": pago.estado}

        self.pago_repo.update(
            pago,
            estado=EstadoPago.RECHAZADO,
            razon=razon,
            gestionado_por_id=admin_id,
            gestionado_at=datetime.now(timezone.utc),
        )

        self.audit_repo.registrar(
            accion="RECHAZAR_PAGO",
            entidad="Pago",
            entidad_id=pago_id,
            usuario_id=admin_id,
            datos_anteriores=datos_anteriores,
            datos_nuevos={"estado": EstadoPago.RECHAZADO, "razon": razon},
        )

        emit("pago.rechazado", pago=pago, socio=pago.socio, razon=razon)
        return pago

    # ── Admin reverts (RN-06) ─────────────────────────────────────────────────

    def revertir(
        self,
        pago_id: int,
        admin_id: int,
        justificacion: str,
        natillera_id: Optional[int] = None,
    ) -> Pago:
        """
        Mark a confirmed payment as REVERTIDO.
        The record is NEVER deleted — it stays in DB for audit (RN-06).

        If the payment is older than 72 hours, the caller must pass
        password_confirmar verified externally before calling this method.
        """
        pago = self._get_pago_for_admin(pago_id, admin_id)
        if natillera_id is not None and pago.natillera_id != natillera_id:
            raise AccesoNoAutorizadoError()

        if pago.estado != EstadoPago.CONFIRMADO:
            raise PagoNoConfirmadoError()

        datos_anteriores = {
            "estado": pago.estado,
            "monto": str(pago.monto),
        }

        self.pago_repo.update(
            pago,
            estado=EstadoPago.REVERTIDO,
            razon=justificacion,
            gestionado_por_id=admin_id,
            gestionado_at=datetime.now(timezone.utc),
        )

        self.audit_repo.registrar(
            accion="REVERTIR_PAGO",
            entidad="Pago",
            entidad_id=pago_id,
            usuario_id=admin_id,
            datos_anteriores=datos_anteriores,
            datos_nuevos={"estado": EstadoPago.REVERTIDO, "justificacion": justificacion},
        )

        emit("pago.revertido", pago=pago)
        return pago

    def es_mayor_a_72h(self, pago: Pago) -> bool:
        """Return True if the payment was confirmed more than 72 hours ago."""
        if pago.gestionado_at is None:
            return False
        limite = datetime.now(timezone.utc) - timedelta(hours=72)
        gestionado = pago.gestionado_at
        if gestionado.tzinfo is None:
            gestionado = gestionado.replace(tzinfo=timezone.utc)
        return gestionado < limite

    # ── Listing helpers ───────────────────────────────────────────────────────

    def listar_por_socio(self, natillera_id: int, usuario_id: int) -> list[Pago]:
        """Return all payments for the authenticated user within a natillera."""
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(natillera_id)

        socio = self.socio_repo.get_by_usuario_y_natillera(usuario_id, natillera_id)
        if socio is None:
            raise SocioNoEncontradoError(usuario_id)

        items, _ = self.pago_repo.get_by_natillera(natillera_id, socio_id=socio.id)
        return items

    def listar_por_natillera(self, natillera_id: int, admin_id: int) -> list[Pago]:
        """Return all payments for a natillera (admin only)."""
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(natillera_id)
        if natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError()

        items, _ = self.pago_repo.get_by_natillera(natillera_id)
        return items

    def obtener_con_contexto(self, pago_id: int, usuario_id: int):
        """
        Return (pago, socio, natillera, periodo) for the given pago_id.
        The user must be the socio owner OR admin of the natillera.
        """
        pago = self.pago_repo.get_by_id(pago_id)
        if pago is None:
            raise PagoNoEncontradoError(pago_id)

        natillera = self.natillera_repo.get_by_id(pago.natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(pago.natillera_id)

        # Check access: admin or the socio who made the payment
        is_admin = natillera.admin_id == usuario_id
        socio = pago.socio
        is_owner = socio is not None and socio.usuario_id == usuario_id
        if not is_admin and not is_owner:
            raise AccesoNoAutorizadoError()

        periodo = self.periodo_repo.get_by_id(pago.periodo_id)
        return pago, socio, natillera, periodo

    def actualizar_recibo(self, pago: Pago, referencia: str, url: str) -> Pago:
        """Persist the generated receipt reference and URL on the payment record."""
        return self.pago_repo.update(pago, recibo_referencia=referencia, recibo_url=url)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_pago_for_admin(self, pago_id: int, admin_id: int) -> Pago:
        pago = self.pago_repo.get_by_id(pago_id)
        if pago is None:
            raise PagoNoEncontradoError(pago_id)
        natillera = self.natillera_repo.get_by_id(pago.natillera_id)
        if natillera is None or natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError()
        return pago
