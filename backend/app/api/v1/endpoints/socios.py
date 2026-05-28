"""
Socios endpoints — invite, accept, list, suspend, reactivate, delete.

References:
- HU-03-01 to HU-03-05
- RN-09, RN-12
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import (
    NatilleraNoEncontradaError,
    AccesoNoAutorizadoError,
    SocioNoEncontradoError,
    SocioConPagosError,
    SocioYaExisteError,
    CupoMaximoAlcanzadoError,
    InvitacionInvalidaError,
)
from app.dependencies import CurrentUser, get_socio_service
from app.schemas.socio import (
    SocioResponse,
    InvitarSocioRequest,
    InvitacionResponse,
    SuspenderSocioRequest,
)
from app.services.socio_service import SocioService

router = APIRouter(prefix="/natilleras/{natillera_id}/socios", tags=["socios"])


@router.get(
    "",
    response_model=List[SocioResponse],
    summary="Listar socios de la natillera",
)
def listar_socios(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[SocioService, Depends(get_socio_service)],
):
    try:
        return svc.listar(natillera_id, current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


@router.post(
    "/invitar",
    response_model=InvitacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invitar socio por email",
)
def invitar_socio(
    natillera_id: int,
    body: InvitarSocioRequest,
    current_user: CurrentUser,
    svc: Annotated[SocioService, Depends(get_socio_service)],
):
    try:
        return svc.invitar(
            natillera_id=natillera_id,
            admin_id=current_user.id,
            email_invitado=body.email,
        )
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except CupoMaximoAlcanzadoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except SocioYaExisteError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.post(
    "/aceptar-invitacion/{token}",
    response_model=SocioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Aceptar invitación y unirse a la natillera",
)
def aceptar_invitacion(
    natillera_id: int,
    token: str,
    current_user: CurrentUser,
    svc: Annotated[SocioService, Depends(get_socio_service)],
):
    try:
        return svc.aceptar_invitacion(token=token, usuario_id=current_user.id)
    except InvitacionInvalidaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    except SocioYaExisteError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except CupoMaximoAlcanzadoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.patch(
    "/{socio_id}/suspender",
    response_model=SocioResponse,
    summary="Suspender socio",
)
def suspender_socio(
    natillera_id: int,
    socio_id: int,
    body: SuspenderSocioRequest,
    current_user: CurrentUser,
    svc: Annotated[SocioService, Depends(get_socio_service)],
):
    try:
        return svc.suspender(
            natillera_id=natillera_id,
            socio_id=socio_id,
            admin_id=current_user.id,
            razon=body.razon,
        )
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except SocioNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


@router.patch(
    "/{socio_id}/reactivar",
    response_model=SocioResponse,
    summary="Reactivar socio suspendido",
)
def reactivar_socio(
    natillera_id: int,
    socio_id: int,
    current_user: CurrentUser,
    svc: Annotated[SocioService, Depends(get_socio_service)],
):
    try:
        return svc.reactivar(
            natillera_id=natillera_id,
            socio_id=socio_id,
            admin_id=current_user.id,
        )
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except SocioNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


@router.delete(
    "/{socio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar socio (solo si no tiene aportes)",
)
def eliminar_socio(
    natillera_id: int,
    socio_id: int,
    current_user: CurrentUser,
    svc: Annotated[SocioService, Depends(get_socio_service)],
):
    try:
        svc.eliminar(
            natillera_id=natillera_id,
            socio_id=socio_id,
            admin_id=current_user.id,
        )
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except SocioNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except SocioConPagosError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
