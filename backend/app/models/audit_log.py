"""
AuditLog model — IMMUTABLE, insert-only.

Records every critical operation with a full before/after diff.
No UPDATE or DELETE methods are implemented in AuditRepository.
A PostgreSQL trigger provides a second line of defence at the DB level.

Tracked operations (HU-09-01):
- confirmar_pago, rechazar_pago, revertir_pago
- crear_natillera, activar_natillera, cerrar_natillera
- ejecutar_distribucion
- suspender_socio, eliminar_socio
- cambiar_admin

Retention: minimum 3 years (RNF-10).
"""
from datetime import datetime
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AuditLog(Base):
    """
    Immutable audit trail record.

    Once inserted this record must never be modified or deleted.
    The AuditRepository intentionally exposes no update() or delete() methods.
    """
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # What happened
    accion: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # On which entity
    entidad: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entidad_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # Who did it
    usuario_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Diff
    datos_anteriores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    datos_nuevos: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # When
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} accion={self.accion!r} entidad={self.entidad} entidad_id={self.entidad_id}>"
