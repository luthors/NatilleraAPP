"""
Natillera model.

A natillera is a community savings group with a fixed period, contribution
amount and lifecycle (CONFIGURACION → ACTIVA → EN_CIERRE → CERRADA → ARCHIVADA).

Business rules enforced:
- RN-01: Exactly one admin_id (NOT NULL FK to usuarios).
- RN-02: monto_por_periodo is fixed; services must reject changes once ACTIVA.
- RN-03: periodicidad is fixed; same enforcement.
- RN-12: max_socios >= 2.
"""
import enum
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class EstadoNatillera(str, enum.Enum):
    CONFIGURACION = "CONFIGURACION"
    ACTIVA        = "ACTIVA"
    EN_CIERRE     = "EN_CIERRE"
    CERRADA       = "CERRADA"
    ARCHIVADA     = "ARCHIVADA"


class Periodicidad(str, enum.Enum):
    SEMANAL    = "SEMANAL"
    QUINCENAL  = "QUINCENAL"
    MENSUAL    = "MENSUAL"


class Natillera(Base, TimestampMixin):
    __tablename__ = "natilleras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Identity
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Admin (RN-01: exactly one, never null)
    admin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Financial parameters — immutable once ACTIVA (RN-02, RN-03)
    monto_por_periodo: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    periodicidad: Mapped[Periodicidad] = mapped_column(SAEnum(Periodicidad), nullable=False)

    # Dates
    fecha_inicio: Mapped[str] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[str] = mapped_column(Date, nullable=False)

    # Capacity (RN-12: min 2)
    max_socios: Mapped[int] = mapped_column(Integer, default=20, nullable=False)

    # Lifecycle
    estado: Mapped[EstadoNatillera] = mapped_column(
        SAEnum(EstadoNatillera), default=EstadoNatillera.CONFIGURACION, nullable=False, index=True
    )

    # Relationships
    admin = relationship("Usuario", back_populates="natilleras_admin", foreign_keys=[admin_id])
    socios = relationship("Socio", back_populates="natillera", cascade="all, delete-orphan")
    periodos = relationship("Periodo", back_populates="natillera", cascade="all, delete-orphan", order_by="Periodo.numero")
    pagos = relationship("Pago", back_populates="natillera")
    distribuciones = relationship("Distribucion", back_populates="natillera")
    invitaciones = relationship("Invitacion", back_populates="natillera", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Natillera id={self.id} nombre={self.nombre!r} estado={self.estado}>"
