"""
Security utilities: password hashing, JWT creation/decoding.

- Passwords use bcrypt with configurable cost (default 12 rounds, RNF-04).
- Access tokens expire in 15 minutes (RNF-06).
- Refresh tokens expire in 7 days with rotation on use.
- All token errors raise TokenInvalidoError (domain exception, not HTTPException).
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import re

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import TokenInvalidoError

# ─── Password ─────────────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)

# Regex: min 8 chars, 1 uppercase, 1 digit
_PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Z])(?=.*\d).{8,}$")


def hash_password(plain: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if the plain password matches the hash."""
    return pwd_context.verify(plain, hashed)


def validate_password_strength(password: str) -> None:
    """
    Raise ValueError with a descriptive message if password does not meet requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 digit
    """
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if not re.search(r"[A-Z]", password):
        raise ValueError("La contraseña debe contener al menos una letra mayúscula")
    if not re.search(r"\d", password):
        raise ValueError("La contraseña debe contener al menos un número")


# ─── JWT ──────────────────────────────────────────────────────────────────────

def create_access_token(subject: str, extra: Optional[dict] = None) -> str:
    """
    Create a short-lived JWT access token.

    Args:
        subject: The user ID (as string) to encode as the token subject.
        extra: Optional additional claims to include in the payload.

    Returns:
        Signed JWT string valid for ACCESS_TOKEN_EXPIRE_MINUTES minutes.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire, "type": "access"}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """
    Create a long-lived JWT refresh token.

    Returns:
        Signed JWT string valid for REFRESH_TOKEN_EXPIRE_DAYS days.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_password_reset_token(subject: str) -> str:
    """Create a single-use password reset token valid for 1 hour."""
    expire = datetime.now(timezone.utc) + timedelta(
        hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
    )
    payload = {"sub": subject, "exp": expire, "type": "password_reset"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str, expected_type: str = "access") -> str:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT string to decode.
        expected_type: The expected token type ('access', 'refresh', 'password_reset').

    Returns:
        The subject (user ID as string) from the token payload.

    Raises:
        TokenInvalidoError: If the token is expired, malformed, or has wrong type.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")

        if subject is None:
            raise TokenInvalidoError("Token sin sujeto")
        if token_type != expected_type:
            raise TokenInvalidoError(f"Tipo de token incorrecto: se esperaba '{expected_type}'")

        return subject
    except JWTError:
        raise TokenInvalidoError()
