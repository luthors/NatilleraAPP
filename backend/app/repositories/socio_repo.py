"""
SocioRepository and InvitacionRepository.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.models.socio import Socio, EstadoSocio
from app.models.invitacion import Invitacion
from app.repositories.base import BaseRepository


class SocioRepository(BaseRepository[Socio]):

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id: int) -> Optional[Socio]:
        return self.db.get(Socio, id)

    def get_by_natillera(self, natillera_id: int, solo_activos: bool = False) -> list[Socio]:
        query = self.db.query(Socio).filter(Socio.natillera_id == natillera_id)
        if solo_activos:
            query = query.filter(Socio.estado == EstadoSocio.ACTIVO)
        return query.all()

    def get_by_usuario_y_natillera(self, usuario_id: int, natillera_id: int) -> Optional[Socio]:
        return (
            self.db.query(Socio)
            .filter(Socio.usuario_id == usuario_id, Socio.natillera_id == natillera_id)
            .first()
        )

    def count_activos(self, natillera_id: int) -> int:
        return (
            self.db.query(Socio)
            .filter(Socio.natillera_id == natillera_id, Socio.estado == EstadoSocio.ACTIVO)
            .count()
        )

    def tiene_pagos(self, socio_id: int) -> bool:
        """Return True if the socio has at least one non-rejected payment (RN-09)."""
        from app.models.pago import Pago, EstadoPago
        return (
            self.db.query(Pago)
            .filter(
                Pago.socio_id == socio_id,
                Pago.estado != EstadoPago.RECHAZADO,
            )
            .count() > 0
        )

    def tiene_mora(self, socio_id: int, natillera_id: int) -> bool:
        """
        Return True if the socio has any OPEN period without a CONFIRMADO payment.
        Used to enforce RN-04.
        """
        from app.models.pago import Pago, EstadoPago
        from app.models.socio import Periodo, EstadoPeriodo
        from sqlalchemy import exists, and_

        subq = (
            self.db.query(Pago.id)
            .filter(
                Pago.socio_id == socio_id,
                Pago.periodo_id == Periodo.id,
                Pago.estado == EstadoPago.CONFIRMADO,
            )
            .correlate(Periodo)
            .exists()
        )

        return (
            self.db.query(Periodo)
            .filter(
                Periodo.natillera_id == natillera_id,
                Periodo.estado == EstadoPeriodo.ABIERTO,
                ~subq,
            )
            .count() > 0
        )

    def update_estado(self, socio: Socio, estado: EstadoSocio, **extra) -> Socio:
        socio.estado = estado
        for k, v in extra.items():
            setattr(socio, k, v)
        self.db.flush()
        return socio


class InvitacionRepository(BaseRepository[Invitacion]):

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id: int) -> Optional[Invitacion]:
        return self.db.get(Invitacion, id)

    def get_by_token(self, token: str) -> Optional[Invitacion]:
        return (
            self.db.query(Invitacion)
            .filter(Invitacion.token == token)
            .first()
        )

    def get_pendientes_by_natillera(self, natillera_id: int) -> list[Invitacion]:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(Invitacion)
            .filter(
                Invitacion.natillera_id == natillera_id,
                Invitacion.aceptada == False,  # noqa: E712
                Invitacion.revocada == False,  # noqa: E712
                Invitacion.expira_at > now,
            )
            .all()
        )

    def revocar(self, invitacion: Invitacion) -> Invitacion:
        invitacion.revocada = True
        self.db.flush()
        return invitacion

    def marcar_aceptada(self, invitacion: Invitacion) -> Invitacion:
        invitacion.aceptada = True
        self.db.flush()
        return invitacion
