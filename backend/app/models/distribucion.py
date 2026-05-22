"""
Distribucion model.

Records a distribution of funds to a Socio.

Types:
- PARCIAL: internal loan with interest (Phase 3, HU-06-01).
- FINAL: end-of-cycle full distribution (HU-06-02).

Business rules:
- RN-04: Socios in mora cannot receive PARCIAL distributions.
- RN-07: FINAL distribution only when natillera is EN_CIERRE.
- RN-11: Interest from PARCIAL loans is added to the fund and benefits all socios.

Monetary amounts use Numeric(14,2) — never Float.
"""
import enum
from decimal import Decimal
from datetime import date
from sqlalchemy import Integer, Numeric, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class TipoDistribucion(str, enum.Enum):
    PARCIAL = "PARCIAL"   # internal loan
    FINAL   = "FINAL"     # end-of-cycle payout


class Distribucion(Base, TimestampMixin):
    __tablename__ = "distribuciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    natillera_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("natilleras.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    socio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("socios.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    tipo: Mapped[TipoDistribucion] = mapped_column(SAEnum(TipoDistribucion), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    natillera = relationship("Natillera", back_populates="distribuciones")
    socio = relationship("Socio")

    def __repr__(self) -> str:
        return f"<Distribucion id={self.id} socio_id={self.socio_id} monto={self.monto} tipo={self.tipo}>"
