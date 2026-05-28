"""
Auth endpoints — register, login, logout, token refresh, password recovery.

References:
- HU-01-01: registro
- HU-01-02: login con bloqueo
- HU-01-03: logout
- HU-01-04: recuperación de contraseña
- RNF-06: JWT rotation
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.exceptions import (
    EmailYaRegistradoError,
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    TokenInvalidoError,
    TokenExpiradoError,
    UsuarioNoEncontradoError,
)
from app.dependencies import (
    get_auth_service,
    CurrentUser,
)
from app.schemas.auth import (
    RegistroRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UsuarioResponse,
    RecuperarPasswordRequest,
    ResetPasswordRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/registro",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
)
def registro(
    body: RegistroRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        _usuario, access, refresh = svc.registrar(
            nombre=body.nombre,
            email=body.email,
            password=body.password,
        )
    except EmailYaRegistradoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
)
def login(
    body: LoginRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
    request: Request,
):
    ip = request.client.host if request.client else None
    try:
        _usuario, access, refresh = svc.login(
            email=body.email,
            password=body.password,
            ip=ip,
        )
    except CuentaBloqueadaError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except CredencialesInvalidasError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar access token con refresh token",
)
def refresh_token(
    body: RefreshRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        access, new_refresh = svc.refresh(body.refresh_token)
    except (TokenInvalidoError, TokenExpiradoError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesión (revoca refresh token)",
)
def logout(
    body: RefreshRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
    current_user: CurrentUser,
):
    svc.logout(current_user.id, body.refresh_token)


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Obtener perfil del usuario autenticado",
)
def me(current_user: CurrentUser):
    return current_user


@router.post(
    "/recuperar-password",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicitar email de recuperación de contraseña",
)
def recuperar_password(
    body: RecuperarPasswordRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
):
    # Always return 202 to avoid email enumeration
    try:
        svc.solicitar_recuperacion(body.email)
    except UsuarioNoEncontradoError:
        pass
    return {"message": "Si el correo existe, recibirás un enlace para restablecer tu contraseña."}


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Restablecer contraseña con token de recuperación",
)
def reset_password(
    body: ResetPasswordRequest,
    svc: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        svc.reset_password(body.token, body.nueva_password)
    except TokenExpiradoError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    except UsuarioNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    return {"message": "Contraseña restablecida exitosamente."}
