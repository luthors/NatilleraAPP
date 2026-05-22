"""
Pago model.

Records a payment (aporte) from a Socio for a specific Periodo.

Business rules enforced:
- RN-06: Confirmed payments are never deleted; they can only be REVERTIDO.
- RN-10: Fund balance = sum of CONFIRMADO payments - distributions.
- Monetary amount uses Numeric(14,2) — never Float.

State machine:
    PENDIENTE_CONFIRMACION  (socio submits)
           ↓           ↓
       CONFIRMADO    RECHAZADO   (admin decides)
           ↓
       REVERTIDO                 (admin corrects error, RN-06)
"""
import enum
from decimal import Decimal
from datetime import datetime
from sqlalchemy import Integer, Numeric, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class EstadoPago(str, enum.Enum):
    PENDIENTE_CONFIRMACION = "PENDIENTE_CONFIRMACION"
    CONFIRMADO             = "CONFIRMADO"
    RECHAZADO              = "RECHAZADO"
    REVERTIDO              = "REVERTIDO"


class MetodoPago(str, enum.Enum):
    EFECTIVO      = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    STRIPE        = "STRIPE"
    PSE           = "PSE"


class Pago(Base, TimestampMixin):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    natillera_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("natilleras.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    socio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("socios.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    periodo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("periodos.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Monetary amount — Numeric, never Float (RNF)
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    metodo: Mapped[MetodoPago] = mapped_column(SAEnum(MetodoPago), nullable=False)
    estado: Mapped[EstadoPago] = mapped_column(
        SAEnum(EstadoPago), default=EstadoPago.PENDIENTE_CONFIRMACION, nullable=False, index=True
    )

    # Optional reference / receipt provided by socio
    referencia: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comprobante_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Who confirmed / rejected / reverted, and when
    gestionado_por_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=True
    )
    gestionado_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Rejection / reversal reason (mandatory for RECHAZADO and REVERTIDO)
    razon: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # PDF receipt reference (generated after confirmation)
    recibo_referencia: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    recibo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    natillera = relationship("Natillera", back_populates="pagos")
    socio = relationship("Socio", back_populates="pagos")
    periodo = relationship("Periodo", back_populates="pagos")
    gestionado_por = relationship("Usuario", foreign_keys=[gestionado_por_id])

    def esta_confirmado(self) -> bool:
        return self.estado == EstadoPago.CONFIRMADO

    def __repr__(self) -> str:
        return f"<Pago id={self.id} socio_id={self.socio_id} monto={self.monto} estado={self.estado}>"
