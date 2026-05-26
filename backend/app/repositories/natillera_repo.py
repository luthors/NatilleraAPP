"""
NatilleraRepository — all database access for Natillera and Periodo models.
"""
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from app.models.natillera import Natillera, EstadoNatillera
from app.models.socio import Periodo, EstadoPeriodo
from app.repositories.base import BaseRepository


class NatilleraRepository(BaseRepository[Natillera]):

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id: int) -> Optional[Natillera]:
        return self.db.get(Natillera, id)

    def get_by_admin(self, admin_id: int) -> list[Natillera]:
        return (
            self.db.query(Natillera)
            .filter(Natillera.admin_id == admin_id)
            .order_by(Natillera.created_at.desc())
            .all()
        )

    def get_by_usuario(self, usuario_id: int, incluir_archivadas: bool = False) -> list[Natillera]:
        """Return all natilleras where the user is admin or socio."""
        from app.models.socio import Socio
        query = (
            self.db.query(Natillera)
            .outerjoin(Socio, (Socio.natillera_id == Natillera.id) & (Socio.usuario_id == usuario_id))
            .filter(
                (Natillera.admin_id == usuario_id) | (Socio.usuario_id == usuario_id)
            )
        )
        if not incluir_archivadas:
            query = query.filter(Natillera.estado != EstadoNatillera.ARCHIVADA)
        return query.distinct().order_by(Natillera.created_at.desc()).all()

    def update_estado(self, natillera: Natillera, estado: EstadoNatillera) -> Natillera:
        natillera.estado = estado
        self.db.flush()
        return natillera

    def get_all_by_estado(self, estado: EstadoNatillera) -> list[Natillera]:
        """Return all natilleras in the given state. Used by the mora detection scheduler."""
        return (
            self.db.query(Natillera)
            .filter(Natillera.estado == estado)
            .all()
        )

    def update(self, natillera: Natillera, **fields) -> Natillera:
        for key, value in fields.items():
            setattr(natillera, key, value)
        self.db.flush()
        self.db.refresh(natillera)
        return natillera


class PeriodoRepository(BaseRepository[Periodo]):

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id: int) -> Optional[Periodo]:
        return self.db.get(Periodo, id)

    def get_by_natillera(self, natillera_id: int) -> list[Periodo]:
        return (
            self.db.query(Periodo)
            .filter(Periodo.natillera_id == natillera_id)
            .order_by(Periodo.numero)
            .all()
        )

    def get_periodo_actual(self, natillera_id: int) -> Optional[Periodo]:
        return (
            self.db.query(Periodo)
            .filter(
                Periodo.natillera_id == natillera_id,
                Periodo.estado == EstadoPeriodo.ABIERTO,
            )
            .first()
        )

    def get_periodos_vencidos_sin_pago(self, natillera_id: int):
        """
        Return periods that are ABIERTO and past their fecha_fin.
        Used by the mora detection scheduler.
        """
        from datetime import date
        return (
            self.db.query(Periodo)
            .filter(
                Periodo.natillera_id == natillera_id,
                Periodo.estado == EstadoPeriodo.ABIERTO,
                Periodo.fecha_fin < date.today(),
            )
            .all()
        )
