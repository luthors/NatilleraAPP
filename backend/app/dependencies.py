"""
FastAPI dependency injection wiring.

All `Depends(...)` factories are defined here.
Endpoint modules import from this file — never instantiate services directly.

Pattern:
  - get_db()            → SQLAlchemy Session  (Unit of Work)
  - get_current_user()  → authenticated Usuario model instance
  - get_*_service()     → service factory, using get_db()

References:
- docs/design/01-arquitectura-capas.md (DI layer)
- RNF-06: JWT Bearer token validation
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.core.exceptions import TokenInvalidoError
from app.database import get_db

from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.auth_repo import (
    RefreshTokenRepository,
    IntentoLoginRepository,
    PasswordResetTokenRepository,
)
from app.repositories.natillera_repo import NatilleraRepository, PeriodoRepository
from app.repositories.socio_repo import SocioRepository, InvitacionRepository
from app.repositories.pago_repo import PagoRepository
from app.repositories.audit_repo import AuditRepository

from app.services.auth_service import AuthService
from app.services.natillera_service import NatilleraService
from app.services.socio_service import SocioService
from app.services.pago_service import PagoService
from app.services.saldo_service import SaldoService
from app.services.distribucion_service import DistribucionService
from app.services.comprobante_service import ComprobanteService

from app.models.usuario import Usuario

# ─── OAuth2 ───────────────────────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# ─── Current user ─────────────────────────────────────────────────────────────

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    """
    Decode JWT access token and return the authenticated user.

    Raises HTTP 401 if the token is invalid, expired, or the user no longer exists.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except TokenInvalidoError:
        raise credentials_exc

    sub: str | None = payload.get("sub")
    token_type: str | None = payload.get("type")
    if sub is None or token_type != "access":
        raise credentials_exc

    usuario_repo = UsuarioRepository(db)
    try:
        usuario_id = int(sub)
    except (ValueError, TypeError):
        raise credentials_exc

    usuario = usuario_repo.get_by_id(usuario_id)
    if usuario is None:
        raise credentials_exc

    return usuario


CurrentUser = Annotated[Usuario, Depends(get_current_user)]

# ─── Repository factories ─────────────────────────────────────────────────────

def get_usuario_repo(db: Annotated[Session, Depends(get_db)]) -> UsuarioRepository:
    return UsuarioRepository(db)


def get_refresh_repo(db: Annotated[Session, Depends(get_db)]) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)


def get_intento_repo(db: Annotated[Session, Depends(get_db)]) -> IntentoLoginRepository:
    return IntentoLoginRepository(db)


def get_reset_repo(db: Annotated[Session, Depends(get_db)]) -> PasswordResetTokenRepository:
    return PasswordResetTokenRepository(db)


def get_natillera_repo(db: Annotated[Session, Depends(get_db)]) -> NatilleraRepository:
    return NatilleraRepository(db)


def get_periodo_repo(db: Annotated[Session, Depends(get_db)]) -> PeriodoRepository:
    return PeriodoRepository(db)


def get_socio_repo(db: Annotated[Session, Depends(get_db)]) -> SocioRepository:
    return SocioRepository(db)


def get_invitacion_repo(db: Annotated[Session, Depends(get_db)]) -> InvitacionRepository:
    return InvitacionRepository(db)


def get_pago_repo(db: Annotated[Session, Depends(get_db)]) -> PagoRepository:
    return PagoRepository(db)


def get_audit_repo(db: Annotated[Session, Depends(get_db)]) -> AuditRepository:
    return AuditRepository(db)


# ─── Service factories ────────────────────────────────────────────────────────

def get_auth_service(
    usuario_repo: Annotated[UsuarioRepository, Depends(get_usuario_repo)],
    refresh_repo: Annotated[RefreshTokenRepository, Depends(get_refresh_repo)],
    intento_repo: Annotated[IntentoLoginRepository, Depends(get_intento_repo)],
    reset_repo: Annotated[PasswordResetTokenRepository, Depends(get_reset_repo)],
) -> AuthService:
    return AuthService(
        usuario_repo=usuario_repo,
        refresh_repo=refresh_repo,
        intento_repo=intento_repo,
        reset_repo=reset_repo,
    )


def get_natillera_service(
    natillera_repo: Annotated[NatilleraRepository, Depends(get_natillera_repo)],
    periodo_repo: Annotated[PeriodoRepository, Depends(get_periodo_repo)],
    socio_repo: Annotated[SocioRepository, Depends(get_socio_repo)],
    audit_repo: Annotated[AuditRepository, Depends(get_audit_repo)],
) -> NatilleraService:
    return NatilleraService(
        natillera_repo=natillera_repo,
        periodo_repo=periodo_repo,
        socio_repo=socio_repo,
        audit_repo=audit_repo,
    )


def get_socio_service(
    natillera_repo: Annotated[NatilleraRepository, Depends(get_natillera_repo)],
    socio_repo: Annotated[SocioRepository, Depends(get_socio_repo)],
    invitacion_repo: Annotated[InvitacionRepository, Depends(get_invitacion_repo)],
    usuario_repo: Annotated[UsuarioRepository, Depends(get_usuario_repo)],
    audit_repo: Annotated[AuditRepository, Depends(get_audit_repo)],
) -> SocioService:
    return SocioService(
        natillera_repo=natillera_repo,
        socio_repo=socio_repo,
        invitacion_repo=invitacion_repo,
        usuario_repo=usuario_repo,
        audit_repo=audit_repo,
    )


def get_pago_service(
    pago_repo: Annotated[PagoRepository, Depends(get_pago_repo)],
    natillera_repo: Annotated[NatilleraRepository, Depends(get_natillera_repo)],
    periodo_repo: Annotated[PeriodoRepository, Depends(get_periodo_repo)],
    socio_repo: Annotated[SocioRepository, Depends(get_socio_repo)],
    audit_repo: Annotated[AuditRepository, Depends(get_audit_repo)],
) -> PagoService:
    return PagoService(
        pago_repo=pago_repo,
        natillera_repo=natillera_repo,
        periodo_repo=periodo_repo,
        socio_repo=socio_repo,
        audit_repo=audit_repo,
    )


def get_saldo_service(
    natillera_repo: Annotated[NatilleraRepository, Depends(get_natillera_repo)],
    periodo_repo: Annotated[PeriodoRepository, Depends(get_periodo_repo)],
    socio_repo: Annotated[SocioRepository, Depends(get_socio_repo)],
    pago_repo: Annotated[PagoRepository, Depends(get_pago_repo)],
    db: Annotated[Session, Depends(get_db)],
) -> SaldoService:
    return SaldoService(
        natillera_repo=natillera_repo,
        periodo_repo=periodo_repo,
        socio_repo=socio_repo,
        pago_repo=pago_repo,
        db=db,
    )


def get_distribucion_service(
    natillera_repo: Annotated[NatilleraRepository, Depends(get_natillera_repo)],
    socio_repo: Annotated[SocioRepository, Depends(get_socio_repo)],
    pago_repo: Annotated[PagoRepository, Depends(get_pago_repo)],
    audit_repo: Annotated[AuditRepository, Depends(get_audit_repo)],
    saldo_service: Annotated[SaldoService, Depends(get_saldo_service)],
) -> DistribucionService:
    return DistribucionService(
        natillera_repo=natillera_repo,
        socio_repo=socio_repo,
        pago_repo=pago_repo,
        audit_repo=audit_repo,
        saldo_service=saldo_service,
    )


def get_comprobante_service() -> ComprobanteService:
    return ComprobanteService(
        upload_dir=settings.UPLOAD_DIR,
        app_base_url=settings.APP_BASE_URL,
        frontend_base_url=settings.FRONTEND_BASE_URL,
    )
