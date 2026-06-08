"""
Socio and Periodo models.

Socio: membership of a Usuario in a Natillera.
- One user can be a socio in multiple natilleras.
- UNIQUE(natillera_id, usuario_id) prevents duplicates (enforced at DB level).
- RN-09: a socio with confirmed payments cannot be deleted, only suspended.

Periodo: one payment cycle within a natillera.
- Generated automatically when the natillera is activated (HU-02-06).
- Each socio must pay once per open period.
"""
import enum
from datetime import date
from sqlalchemy import Integer, Date, ForeignKey, Enum as SAEnum, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class EstadoSocio(str, enum.Enum):
    ACTIVO    = "ACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    RETIRADO  = "RETIRADO"


class EstadoPeriodo(str, enum.Enum):
    PENDIENTE = "PENDIENTE"   # not yet open
    ABIERTO   = "ABIERTO"     # current, accepting payments
    CERRADO   = "CERRADO"     # past, no more payments accepted


class Socio(Base, TimestampMixin):
    __tablename__ = "socios"
    __table_args__ = (
        UniqueConstraint("natillera_id", "usuario_id", name="uq_socio_natillera_usuario"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    natillera_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("natilleras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    estado: Mapped[EstadoSocio] = mapped_column(
        SAEnum(EstadoSocio), default=EstadoSocio.ACTIVO, nullable=False
    )
    razon_suspension: Mapped[str | None] = mapped_column(String(500), nullable=True)
    removed_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    natillera = relationship("Natillera", back_populates="socios")
    usuario = relationship("Usuario", back_populates="membresias")
    pagos = relationship("Pago", back_populates="socio")

    def esta_activo(self) -> bool:
        return self.estado == EstadoSocio.ACTIVO

    def __repr__(self) -> str:
        return f"<Socio id={self.id} natillera_id={self.natillera_id} usuario_id={self.usuario_id} estado={self.estado}>"


class Periodo(Base):
    __tablename__ = "periodos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    natillera_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("natilleras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    numero: Mapped[int] = mapped_column(Integer, nullable=False)   # 1-based sequence
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[EstadoPeriodo] = mapped_column(
        SAEnum(EstadoPeriodo), default=EstadoPeriodo.PENDIENTE, nullable=False, index=True
    )

    # Relationships
    natillera = relationship("Natillera", back_populates="periodos")
    pagos = relationship("Pago", back_populates="periodo")

    def __repr__(self) -> str:
        return f"<Periodo id={self.id} natillera_id={self.natillera_id} numero={self.numero} estado={self.estado}>"

    @property
    def nombre(self) -> str:
        """Human-readable period label, e.g. 'Período 3 (01/06/2026 – 30/06/2026)'."""
        inicio = self.fecha_inicio.strftime("%d/%m/%Y") if self.fecha_inicio else "?"
        fin = self.fecha_fin.strftime("%d/%m/%Y") if self.fecha_fin else "?"
        return f"Período {self.numero} ({inicio} – {fin})"
