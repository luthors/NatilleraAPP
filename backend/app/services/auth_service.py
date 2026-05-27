"""
AuthService — registration, login, token management, password recovery.

All business logic lives here. This service:
- Raises domain exceptions (never HTTPException).
- Does NOT call db.commit() — that is the Unit of Work's responsibility.
- Uses repositories for all DB access.

References:
- HU-01-01: registro
- HU-01-02: login con bloqueo
- HU-01-03: logout
- HU-01-04: recuperación de contraseña
- RNF-04: bcrypt cost >= 12
- RNF-06: access 15 min, refresh 7 days with rotation
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    decode_token,
)
from app.core.exceptions import (
    EmailYaRegistradoError,
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    TokenInvalidoError,
    TokenExpiradoError,
    UsuarioNoEncontradoError,
)
from app.core.events import emit
from app.models.usuario import Usuario
from app.models.auth import RefreshToken, PasswordResetToken
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.auth_repo import (
    RefreshTokenRepository,
    IntentoLoginRepository,
    PasswordResetTokenRepository,
)


class AuthService:
    def __init__(
        self,
        usuario_repo: UsuarioRepository,
        refresh_repo: RefreshTokenRepository,
        intento_repo: IntentoLoginRepository,
        reset_repo: PasswordResetTokenRepository,
    ) -> None:
        self.usuario_repo = usuario_repo
        self.refresh_repo = refresh_repo
        self.intento_repo = intento_repo
        self.reset_repo = reset_repo

    # ── Registro ──────────────────────────────────────────────────────────────

    def registrar(self, nombre: str, email: str, password: str) -> tuple[Usuario, str, str]:
        """
        Register a new user.

        Returns:
            (usuario, access_token, refresh_token)

        Raises:
            EmailYaRegistradoError: If the email is already taken.
        """
        email_lower = email.lower().strip()
        if self.usuario_repo.email_exists(email_lower):
            raise EmailYaRegistradoError(email_lower)

        usuario = Usuario(
            nombre=nombre.strip(),
            email=email_lower,
            password_hash=hash_password(password),
        )
        self.usuario_repo.save(usuario)

        access_token = create_access_token(str(usuario.id))
        refresh_token = create_refresh_token(str(usuario.id))
        expira_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.refresh_repo.save_token(usuario.id, refresh_token, expira_at)

        emit("usuario.registrado", usuario=usuario)
        return usuario, access_token, refresh_token

    # ── Login ─────────────────────────────────────────────────────────────────

    def login(self, email: str, password: str, ip: Optional[str] = None) -> tuple[Usuario, str, str]:
        """
        Authenticate a user and return a token pair.

        Security:
        - Returns a generic error that does NOT reveal whether email or password failed.
        - Locks the account for LOGIN_LOCKOUT_MINUTES after MAX_LOGIN_ATTEMPTS failures.

        Returns:
            (usuario, access_token, refresh_token)

        Raises:
            CredencialesInvalidasError
            CuentaBloqueadaError
        """
        usuario = self.usuario_repo.get_by_email(email.lower().strip())
        if usuario is None:
            raise CredencialesInvalidasError()

        # Check lockout window
        lockout_since = datetime.now(timezone.utc) - timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
        failed_count = self.intento_repo.contar_fallidos_recientes(usuario.id, lockout_since)
        if failed_count >= settings.MAX_LOGIN_ATTEMPTS:
            raise CuentaBloqueadaError(settings.LOGIN_LOCKOUT_MINUTES)

        if not verify_password(password, usuario.password_hash):
            self.intento_repo.registrar(usuario.id, exitoso=False, ip=ip)
            raise CredencialesInvalidasError()

        self.intento_repo.registrar(usuario.id, exitoso=True, ip=ip)

        access_token = create_access_token(str(usuario.id))
        refresh_token = create_refresh_token(str(usuario.id))
        expira_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.refresh_repo.save_token(usuario.id, refresh_token, expira_at)

        return usuario, access_token, refresh_token

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh(self, raw_refresh_token: str) -> tuple[str, str]:
        """
        Rotate refresh token: invalidate the old one, issue a new pair.

        Returns:
            (new_access_token, new_refresh_token)

        Raises:
            TokenInvalidoError
        """
        subject = decode_token(raw_refresh_token, expected_type="refresh")
        stored = self.refresh_repo.get_by_token(raw_refresh_token)
        if stored is None or stored.revocado:
            raise TokenInvalidoError("Refresh token inválido o ya usado")

        self.refresh_repo.revocar(stored)

        new_access = create_access_token(subject)
        new_refresh = create_refresh_token(subject)
        expira_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.refresh_repo.save_token(int(subject), new_refresh, expira_at)

        return new_access, new_refresh

    # ── Logout ────────────────────────────────────────────────────────────────

    def logout(self, raw_refresh_token: str) -> None:
        """Revoke the given refresh token (HU-01-03)."""
        stored = self.refresh_repo.get_by_token(raw_refresh_token)
        if stored:
            self.refresh_repo.revocar(stored)

    # ── Password recovery ─────────────────────────────────────────────────────

    def solicitar_recuperacion(self, email: str) -> Optional[str]:
        """
        Create a single-use password reset token.

        Returns the token (so the email service can include it in the link).
        Returns None if the email is not registered — the API always responds
        the same way to avoid revealing whether the email exists.
        """
        usuario = self.usuario_repo.get_by_email(email.lower().strip())
        if usuario is None:
            return None

        token = create_password_reset_token(str(usuario.id))
        expira_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )
        prt = PasswordResetToken(
            usuario_id=usuario.id,
            token=token,
            expira_at=expira_at,
            usado=False,
            created_at=datetime.now(timezone.utc),
        )
        self.reset_repo.save(prt)
        emit("usuario.solicito_recuperacion", usuario=usuario, token=token)
        return token

    def reset_password(self, token: str, nueva_password: str) -> None:
        """
        Reset a user's password using a valid reset token.

        Raises:
            TokenExpiradoError: If the token is expired or already used.
        """
        prt = self.reset_repo.get_by_token(token)
        if prt is None:
            raise TokenExpiradoError()

        if datetime.now(timezone.utc) > prt.expira_at.replace(tzinfo=timezone.utc):
            raise TokenExpiradoError()

        usuario = self.usuario_repo.get_by_id(prt.usuario_id)
        if usuario is None:
            raise UsuarioNoEncontradoError()

        self.usuario_repo.update(usuario, password_hash=hash_password(nueva_password))
        self.reset_repo.marcar_usado(prt)
        self.refresh_repo.revocar_todos(usuario.id)
