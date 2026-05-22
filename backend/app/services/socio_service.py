"""
SocioService — invite, accept, suspend, delete socios.

References:
- HU-03-01: invitar
- HU-03-02: aceptar
- HU-03-03: listar
- HU-03-04: suspender
- HU-03-05: eliminar
- RN-09: socio con pagos no puede eliminarse
- RN-12: cupo máximo
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.events import emit
from app.core.exceptions import (
    NatilleraNoEncontradaError,
    AccesoNoAutorizadoError,
    CupoMaximoAlcanzadoError,
    SocioYaExisteError,
    SocioNoEncontradoError,
    SocioConPagosError,
    InvitacionInvalidaError,
)
from app.models.invitacion import Invitacion
from app.models.socio import Socio, EstadoSocio
from app.repositories.natillera_repo import NatilleraRepository
from app.repositories.socio_repo import SocioRepository, InvitacionRepository
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.audit_repo import AuditRepository


class SocioService:

    def __init__(
        self,
        natillera_repo: NatilleraRepository,
        socio_repo: SocioRepository,
        invitacion_repo: InvitacionRepository,
        usuario_repo: UsuarioRepository,
        audit_repo: AuditRepository,
    ) -> None:
        self.natillera_repo = natillera_repo
        self.socio_repo = socio_repo
        self.invitacion_repo = invitacion_repo
        self.usuario_repo = usuario_repo
        self.audit_repo = audit_repo

    # ── Invitar ───────────────────────────────────────────────────────────────

    def invitar(self, natillera_id: int, admin_id: int, email_invitado: str) -> Invitacion:
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(natillera_id)
        if natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError()

        activos = self.socio_repo.count_activos(natillera_id)
        if activos >= natillera.max_socios:
            raise CupoMaximoAlcanzadoError()

        invitacion = Invitacion(
            natillera_id=natillera_id,
            invitado_por_id=admin_id,
            email_invitado=email_invitado.lower().strip(),
            token=str(uuid.uuid4()),
            expira_at=datetime.now(timezone.utc) + timedelta(hours=48),
            created_at=datetime.now(timezone.utc),
        )
        self.invitacion_repo.save(invitacion)
        emit("invitacion.creada", invitacion=invitacion, natillera=natillera)
        return invitacion

    # ── Aceptar ───────────────────────────────────────────────────────────────

    def aceptar_invitacion(self, token: str, usuario_id: int) -> Socio:
        invitacion = self.invitacion_repo.get_by_token(token)
        if invitacion is None or not invitacion.esta_vigente():
            raise InvitacionInvalidaError(
                "Invitación inválida o expirada. Pide al administrador una nueva."
            )

        natillera_id = invitacion.natillera_id
        existe = self.socio_repo.get_by_usuario_y_natillera(usuario_id, natillera_id)
        if existe is not None:
            raise SocioYaExisteError()

        socio = Socio(
            natillera_id=natillera_id,
            usuario_id=usuario_id,
            estado=EstadoSocio.ACTIVO,
        )
        self.socio_repo.save(socio)
        self.invitacion_repo.marcar_aceptada(invitacion)

        emit("socio.unido", socio=socio, natillera=invitacion.natillera)
        return socio

    # ── Listar ────────────────────────────────────────────────────────────────

    def listar(self, natillera_id: int, admin_id: int) -> list[Socio]:
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(natillera_id)
        if natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError()
        return self.socio_repo.get_by_natillera(natillera_id)

    # ── Suspender ────────────────────────────────────────────────────────────

    def suspender(self, socio_id: int, admin_id: int, razon: str) -> Socio:
        socio = self.socio_repo.get_by_id(socio_id)
        if socio is None:
            raise SocioNoEncontradoError(socio_id)
        natillera = self.natillera_repo.get_by_id(socio.natillera_id)
        if natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError()

        datos_anteriores = {"estado": socio.estado}
        socio = self.socio_repo.update_estado(
            socio, EstadoSocio.SUSPENDIDO, razon_suspension=razon
        )
        self.audit_repo.registrar(
            accion="SUSPENDER_SOCIO",
            entidad="Socio",
            entidad_id=socio_id,
            usuario_id=admin_id,
            datos_anteriores=datos_anteriores,
            datos_nuevos={"estado": EstadoSocio.SUSPENDIDO, "razon": razon},
        )
        emit("socio.suspendido", socio=socio, razon=razon)
        return socio

    def reactivar(self, socio_id: int, admin_id: int) -> Socio:
        socio = self.socio_repo.get_by_id(socio_id)
        if socio is None:
            raise SocioNoEncontradoError(socio_id)
        natillera = self.natillera_repo.get_by_id(socio.natillera_id)
        if natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError()
        return self.socio_repo.update_estado(socio, EstadoSocio.ACTIVO, razon_suspension=None)

    # ── Eliminar ─────────────────────────────────────────────────────────────

    def eliminar(self, socio_id: int, admin_id: int) -> None:
        """
        Remove a socio from a natillera.
        Blocked if the socio has any confirmed payments (RN-09).
        """
        socio = self.socio_repo.get_by_id(socio_id)
        if socio is None:
            raise SocioNoEncontradoError(socio_id)
        natillera = self.natillera_repo.get_by_id(socio.natillera_id)
        if natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError()

        if self.socio_repo.tiene_pagos(socio_id):
            raise SocioConPagosError()

        self.audit_repo.registrar(
            accion="ELIMINAR_SOCIO",
            entidad="Socio",
            entidad_id=socio_id,
            usuario_id=admin_id,
            datos_anteriores={"usuario_id": socio.usuario_id, "natillera_id": socio.natillera_id},
        )
        self.socio_repo.delete(socio)
