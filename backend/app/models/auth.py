"""
RefreshToken and IntentoLogin models for authentication security.

RefreshToken:
- Stored in DB to allow invalidation on logout (RNF-06).
- Token rotation: each use generates a new token and invalidates the old one.

IntentoLogin:
- Tracks failed login attempts per email.
- Account is locked for LOGIN_LOCKOUT_MINUTES after MAX_LOGIN_ATTEMPTS failures (HU-01-02).
"""
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    expira_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revocado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    usuario = relationship("Usuario", back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken usuario_id={self.usuario_id} revocado={self.revocado}>"


class IntentoLogin(Base, TimestampMixin):
    __tablename__ = "intentos_login"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    exitoso: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    usuario = relationship("Usuario", back_populates="intentos_login")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expira_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
