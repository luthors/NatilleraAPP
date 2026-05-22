"""
Invitacion model.

Represents a pending invitation from an admin to join a natillera.
- Token is a single-use UUID valid for 48 hours (HU-03-01).
- If the invited email has no account, the user is redirected to
  registration and auto-joined after completing it.
"""
from datetime import datetime
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Invitacion(Base):
    __tablename__ = "invitaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    natillera_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("natilleras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    invitado_por_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )

    email_invitado: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    expira_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    aceptada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revocada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    natillera = relationship("Natillera", back_populates="invitaciones")
    invitado_por = relationship("Usuario", foreign_keys=[invitado_por_id])

    def esta_vigente(self) -> bool:
        from datetime import timezone
        return (
            not self.aceptada
            and not self.revocada
            and self.expira_at > datetime.now(timezone.utc)
        )

    def __repr__(self) -> str:
        return f"<Invitacion id={self.id} email={self.email_invitado!r} natillera_id={self.natillera_id}>"
