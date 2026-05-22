"""
AuthRepository — RefreshToken, IntentoLogin, PasswordResetToken access.
"""
from datetime import datetime, timezone
import hashlib
from typing import Optional

from sqlalchemy.orm import Session

from app.models.auth import RefreshToken, IntentoLogin, PasswordResetToken
from app.repositories.base import BaseRepository
from app.core.config import settings


class RefreshTokenRepository(BaseRepository[RefreshToken]):

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id: int) -> Optional[RefreshToken]:
        return self.db.get(RefreshToken, id)

    def get_by_token(self, raw_token: str) -> Optional[RefreshToken]:
        token_hash = self._hash(raw_token)
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash, RefreshToken.revocado == False)  # noqa: E712
            .first()
        )

    def revocar_todos(self, usuario_id: int) -> None:
        """Revoke all active refresh tokens for a user (on password reset or logout-all)."""
        self.db.query(RefreshToken).filter(
            RefreshToken.usuario_id == usuario_id,
            RefreshToken.revocado == False,  # noqa: E712
        ).update({"revocado": True})
        self.db.flush()

    def revocar(self, token: RefreshToken) -> None:
        token.revocado = True
        self.db.flush()

    @staticmethod
    def _hash(raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    def save_token(self, usuario_id: int, raw_token: str, expira_at: datetime) -> RefreshToken:
        rt = RefreshToken(
            usuario_id=usuario_id,
            token_hash=self._hash(raw_token),
            expira_at=expira_at,
        )
        return self.save(rt)


class IntentoLoginRepository(BaseRepository[IntentoLogin]):

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id: int) -> Optional[IntentoLogin]:
        return self.db.get(IntentoLogin, id)

    def contar_fallidos_recientes(self, usuario_id: int, desde: datetime) -> int:
        return (
            self.db.query(IntentoLogin)
            .filter(
                IntentoLogin.usuario_id == usuario_id,
                IntentoLogin.exitoso == False,  # noqa: E712
                IntentoLogin.created_at >= desde,
            )
            .count()
        )

    def registrar(self, usuario_id: int, exitoso: bool, ip: Optional[str] = None) -> IntentoLogin:
        intento = IntentoLogin(usuario_id=usuario_id, exitoso=exitoso, ip=ip)
        return self.save(intento)


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id: int) -> Optional[PasswordResetToken]:
        return self.db.get(PasswordResetToken, id)

    def get_by_token(self, token: str) -> Optional[PasswordResetToken]:
        return (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token == token, PasswordResetToken.usado == False)  # noqa: E712
            .first()
        )

    def marcar_usado(self, prt: PasswordResetToken) -> None:
        prt.usado = True
        self.db.flush()
