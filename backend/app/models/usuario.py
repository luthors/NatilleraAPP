"""
Usuario model.

Represents a registered user of the platform.
A user can be an Administrator (Tesorero) of one or more natilleras
and/or a Socio (participant) in one or more natilleras.

Business rules enforced at DB level:
- email must be unique (UNIQUE constraint).
- password_hash is never exposed in API responses (enforced in schemas).
"""
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    foto_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    natilleras_admin = relationship("Natillera", back_populates="admin", foreign_keys="Natillera.admin_id")
    membresias = relationship("Socio", back_populates="usuario")
    refresh_tokens = relationship("RefreshToken", back_populates="usuario", cascade="all, delete-orphan")
    intentos_login = relationship("IntentoLogin", back_populates="usuario", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email}>"
