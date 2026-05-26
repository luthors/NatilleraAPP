"""
PagoRepository — all database access for the Pago model.
"""
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.pago import Pago, EstadoPago
from app.repositories.base import BaseRepository


class PagoRepository(BaseRepository[Pago]):

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id: int) -> Optional[Pago]:
        return self.db.get(Pago, id)

    def get_by_referencia(self, referencia: str) -> Optional[Pago]:
        return (
            self.db.query(Pago)
            .filter(Pago.recibo_referencia == referencia)
            .first()
        )

    def get_by_recibo_referencia(self, referencia: str) -> Optional[Pago]:
        """Alias for get_by_referencia — used by the public QR verification endpoint."""
        return self.get_by_referencia(referencia)

    def get_by_natillera(
        self,
        natillera_id: int,
        socio_id: Optional[int] = None,
        estado: Optional[EstadoPago] = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Pago], int]:
        """Return paginated payments with optional filters. Returns (items, total)."""
        query = self.db.query(Pago).filter(Pago.natillera_id == natillera_id)
        if socio_id:
            query = query.filter(Pago.socio_id == socio_id)
        if estado:
            query = query.filter(Pago.estado == estado)
        total = query.count()
        items = (
            query.order_by(Pago.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return items, total

    def pago_activo_existe(self, socio_id: int, periodo_id: int) -> bool:
        """
        Return True if there is already a non-rejected payment for this socio/period.
        Used to enforce the 'no duplicate payment' rule.
        """
        return (
            self.db.query(Pago)
            .filter(
                Pago.socio_id == socio_id,
                Pago.periodo_id == periodo_id,
                Pago.estado != EstadoPago.RECHAZADO,
            )
            .count() > 0
        )

    def get_pendientes_confirmacion(self, natillera_id: int) -> list[Pago]:
        return (
            self.db.query(Pago)
            .filter(
                Pago.natillera_id == natillera_id,
                Pago.estado == EstadoPago.PENDIENTE_CONFIRMACION,
            )
            .order_by(Pago.created_at)
            .all()
        )

    def sum_confirmados(self, natillera_id: int) -> Decimal:
        """Return the total of all CONFIRMADO payments for this natillera."""
        result = (
            self.db.query(func.coalesce(func.sum(Pago.monto), 0))
            .filter(
                Pago.natillera_id == natillera_id,
                Pago.estado == EstadoPago.CONFIRMADO,
            )
            .scalar()
        )
        return Decimal(str(result))

    def sum_confirmados_por_socio(self, socio_id: int, natillera_id: int) -> Decimal:
        result = (
            self.db.query(func.coalesce(func.sum(Pago.monto), 0))
            .filter(
                Pago.socio_id == socio_id,
                Pago.natillera_id == natillera_id,
                Pago.estado == EstadoPago.CONFIRMADO,
            )
            .scalar()
        )
        return Decimal(str(result))

    def update(self, pago: Pago, **fields) -> Pago:
        for key, value in fields.items():
            setattr(pago, key, value)
        self.db.flush()
        self.db.refresh(pago)
        return pago
