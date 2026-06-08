"""
Tests for AuthService — registration, login, token management, password recovery.

Covers:
- ISSUE-41: Tests unitarios — autenticación y servicios core
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from app.services.auth_service import AuthService
from app.core.exceptions import (
    EmailYaRegistradoError,
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    TokenInvalidoError,
    TokenExpiradoError,
)
from app.core.config import settings


@pytest.mark.auth
class TestRegistro:
    """Tests for user registration."""

    def test_registro_exitoso(self, db):
        """Successful registration returns user, access_token, and refresh_token."""
        from app.repositories.usuario_repo import UsuarioRepository
        from app.repositories.auth_repo import (
            RefreshTokenRepository,
            IntentoLoginRepository,
            PasswordResetTokenRepository,
        )

        service = AuthService(
            usuario_repo=UsuarioRepository(db),
            refresh_repo=RefreshTokenRepository(db),
            intento_repo=IntentoLoginRepository(db),
            reset_repo=PasswordResetTokenRepository(db),
        )

        usuario, access, refresh = service.registrar(
            nombre="Test User",
            email="new@example.com",
            password="Passw0rd!",
        )

        assert usuario.email == "new@example.com"
        assert usuario.nombre == "Test User"
        assert usuario.password_hash != "Passw0rd!"
        assert access is not None
        assert refresh is not None

    def test_registro_email_duplicado(self, db):
        """Registration with existing email raises EmailYaRegistradoError."""
        from app.repositories.usuario_repo import UsuarioRepository
        from app.repositories.auth_repo import (
            RefreshTokenRepository,
            IntentoLoginRepository,
            PasswordResetTokenRepository,
        )

        service = AuthService(
            usuario_repo=UsuarioRepository(db),
            refresh_repo=RefreshTokenRepository(db),
            intento_repo=IntentoLoginRepository(db),
            reset_repo=PasswordResetTokenRepository(db),
        )

        service.registrar("User 1", "dup@example.com", "Passw0rd!")

        with pytest.raises(EmailYaRegistradoError):
            service.registrar("User 2", "dup@example.com", "Passw0rd!")

    def test_registro_normaliza_email(self, db):
        """Email is normalized to lowercase and stripped."""
        from app.repositories.usuario_repo import UsuarioRepository
        from app.repositories.auth_repo import (
            RefreshTokenRepository,
            IntentoLoginRepository,
            PasswordResetTokenRepository,
        )

        service = AuthService(
            usuario_repo=UsuarioRepository(db),
            refresh_repo=RefreshTokenRepository(db),
            intento_repo=IntentoLoginRepository(db),
            reset_repo=PasswordResetTokenRepository(db),
        )

        usuario, _, _ = service.registrar(
            "Test", "  UPPER@Example.COM  ", "Passw0rd!"
        )
        assert usuario.email == "upper@example.com"


@pytest.mark.auth
class TestLogin:
    """Tests for login flow."""

    def _create_service(self, db):
        from app.repositories.usuario_repo import UsuarioRepository
        from app.repositories.auth_repo import (
            RefreshTokenRepository,
            IntentoLoginRepository,
            PasswordResetTokenRepository,
        )
        return AuthService(
            usuario_repo=UsuarioRepository(db),
            refresh_repo=RefreshTokenRepository(db),
            intento_repo=IntentoLoginRepository(db),
            reset_repo=PasswordResetTokenRepository(db),
        )

    def test_login_exitoso(self, db):
        """Valid credentials return tokens."""
        service = self._create_service(db)
        service.registrar("Test", "login@test.com", "Passw0rd!")

        usuario, access, refresh = service.login("login@test.com", "Passw0rd!")
        assert usuario.email == "login@test.com"
        assert access is not None
        assert refresh is not None

    def test_login_password_incorrecta(self, db):
        """Wrong password raises CredencialesInvalidasError."""
        service = self._create_service(db)
        service.registrar("Test", "login2@test.com", "Passw0rd!")

        with pytest.raises(CredencialesInvalidasError):
            service.login("login2@test.com", "WrongPassword1!")

    def test_login_email_no_existe(self, db):
        """Non-existent email raises CredencialesInvalidasError (same error as wrong password)."""
        service = self._create_service(db)

        with pytest.raises(CredencialesInvalidasError):
            service.login("nonexistent@test.com", "Passw0rd!")

    def test_login_bloqueo_cuenta(self, db):
        """After MAX_LOGIN_ATTEMPTS failures, account is locked."""
        service = self._create_service(db)
        service.registrar("Test", "lock@test.com", "Passw0rd!")

        for _ in range(settings.MAX_LOGIN_ATTEMPTS):
            with pytest.raises(CredencialesInvalidasError):
                service.login("lock@test.com", "WrongPassword1!")

        with pytest.raises(CuentaBloqueadaError):
            service.login("lock@test.com", "Passw0rd!")


@pytest.mark.auth
class TestRefreshToken:
    """Tests for token refresh."""

    def _create_service(self, db):
        from app.repositories.usuario_repo import UsuarioRepository
        from app.repositories.auth_repo import (
            RefreshTokenRepository,
            IntentoLoginRepository,
            PasswordResetTokenRepository,
        )
        return AuthService(
            usuario_repo=UsuarioRepository(db),
            refresh_repo=RefreshTokenRepository(db),
            intento_repo=IntentoLoginRepository(db),
            reset_repo=PasswordResetTokenRepository(db),
        )

    def test_refresh_exitoso(self, db):
        """Valid refresh token returns new token pair."""
        service = self._create_service(db)
        _, _, refresh = service.registrar("Test", "refresh@test.com", "Passw0rd!")

        new_access, new_refresh = service.refresh(refresh)
        assert new_access is not None
        assert new_refresh is not None
        assert new_refresh != refresh

    def test_refresh_token_invalido(self, db):
        """Invalid refresh token raises TokenInvalidoError."""
        service = self._create_service(db)
        service.registrar("Test", "refresh2@test.com", "Passw0rd!")

        with pytest.raises(TokenInvalidoError):
            service.refresh("invalid-token-12345")

    def test_refresh_token_reusado(self, db):
        """Reusing a consumed refresh token raises TokenInvalidoError."""
        service = self._create_service(db)
        _, _, refresh = service.registrar("Test", "refresh3@test.com", "Passw0rd!")

        service.refresh(refresh)

        with pytest.raises(TokenInvalidoError):
            service.refresh(refresh)


@pytest.mark.auth
class TestLogout:
    """Tests for logout."""

    def _create_service(self, db):
        from app.repositories.usuario_repo import UsuarioRepository
        from app.repositories.auth_repo import (
            RefreshTokenRepository,
            IntentoLoginRepository,
            PasswordResetTokenRepository,
        )
        return AuthService(
            usuario_repo=UsuarioRepository(db),
            refresh_repo=RefreshTokenRepository(db),
            intento_repo=IntentoLoginRepository(db),
            reset_repo=PasswordResetTokenRepository(db),
        )

    def test_logout_invalida_token(self, db):
        """Logout revokes the refresh token."""
        service = self._create_service(db)
        _, _, refresh = service.registrar("Test", "logout@test.com", "Passw0rd!")

        service.logout(refresh)

        with pytest.raises(TokenInvalidoError):
            service.refresh(refresh)


@pytest.mark.auth
class TestPasswordRecovery:
    """Tests for password recovery flow."""

    def _create_service(self, db):
        from app.repositories.usuario_repo import UsuarioRepository
        from app.repositories.auth_repo import (
            RefreshTokenRepository,
            IntentoLoginRepository,
            PasswordResetTokenRepository,
        )
        return AuthService(
            usuario_repo=UsuarioRepository(db),
            refresh_repo=RefreshTokenRepository(db),
            intento_repo=IntentoLoginRepository(db),
            reset_repo=PasswordResetTokenRepository(db),
        )

    def test_solicitar_recuperacion_exitosa(self, db):
        """Requesting recovery for existing email returns a token."""
        service = self._create_service(db)
        service.registrar("Test", "recover@test.com", "Passw0rd!")

        token = service.solicitar_recuperacion("recover@test.com")
        assert token is not None

    def test_solicitar_recuperacion_email_no_existe(self, db):
        """Requesting recovery for non-existent email returns None (no info leak)."""
        service = self._create_service(db)
        token = service.solicitar_recuperacion("noexist@test.com")
        assert token is None

    def test_reset_password_exitoso(self, db):
        """Valid reset token allows password change."""
        service = self._create_service(db)
        service.registrar("Test", "reset@test.com", "OldPassword1!")

        token = service.solicitar_recuperacion("reset@test.com")
        service.reset_password(token, "NewPassword2!")

        usuario, _, _ = service.login("reset@test.com", "NewPassword2!")
        assert usuario.email == "reset@test.com"

    def test_reset_password_token_invalido(self, db):
        """Invalid reset token raises TokenExpiradoError."""
        service = self._create_service(db)

        with pytest.raises(TokenExpiradoError):
            service.reset_password("invalid-token", "NewPassword1!")

    def test_reset_password_invalida_tokens_previos(self, db):
        """After reset, all previous refresh tokens are revoked."""
        service = self._create_service(db)
        _, _, refresh = service.registrar("Test", "reset2@test.com", "Passw0rd!")

        token = service.solicitar_recuperacion("reset2@test.com")
        service.reset_password(token, "NewPassword3!")

        with pytest.raises(TokenInvalidoError):
            service.refresh(refresh)
