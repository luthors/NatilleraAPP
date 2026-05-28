"""
Natilleras endpoints — CRUD + lifecycle (activar, cerrar, archivar).

References:
- HU-02-01 to HU-02-08
- RN-01, RN-02, RN-03, RN-07, RN-12
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import (
    NatilleraNoEncontradaError,
    NatilleraEstadoInvalidoError,
    CambioParametrosFinancierosError,
    SociosInsuficientesError,
    AccesoNoAutorizadoError,
)
from app.dependencies import CurrentUser, get_natillera_service
from app.schemas.common import MessageResponse
from app.schemas.natillera import (
    NatilleraCreate,
    NatilleraUpdate,
    NatilleraResponse,
    PeriodoResponse,
    CerrarNatilleraRequest,
)
from app.services.natillera_service import NatilleraService

router = APIRouter(prefix="/natilleras", tags=["natilleras"])


def _natillera_svc(svc: Annotated[NatilleraService, Depends(get_natillera_service)]) -> NatilleraService:
    return svc


@router.post(
    "",
    response_model=NatilleraResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear natillera",
)
def crear_natillera(
    body: NatilleraCreate,
    current_user: CurrentUser,
    svc: Annotated[NatilleraService, Depends(get_natillera_service)],
):
    natillera = svc.crear(
        admin_id=current_user.id,
        nombre=body.nombre,
        descripcion=body.descripcion,
        monto_por_periodo=body.monto_por_periodo,
        periodicidad=body.periodicidad,
        fecha_inicio=body.fecha_inicio,
        fecha_fin=body.fecha_fin,
        max_socios=body.max_socios,
    )
    return natillera


@router.get(
    "",
    response_model=List[NatilleraResponse],
    summary="Listar mis natilleras (admin + socio)",
)
def listar_natilleras(
    current_user: CurrentUser,
    svc: Annotated[NatilleraService, Depends(get_natillera_service)],
):
    return svc.listar_por_usuario(current_user.id)


@router.get(
    "/{natillera_id}",
    response_model=NatilleraResponse,
    summary="Obtener detalle de natillera",
)
def obtener_natillera(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[NatilleraService, Depends(get_natillera_service)],
):
    try:
        return svc.obtener(natillera_id, current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


@router.patch(
    "/{natillera_id}",
    response_model=NatilleraResponse,
    summary="Editar nombre/descripción de natillera",
)
def editar_natillera(
    natillera_id: int,
    body: NatilleraUpdate,
    current_user: CurrentUser,
    svc: Annotated[NatilleraService, Depends(get_natillera_service)],
):
    try:
        return svc.editar(
            natillera_id=natillera_id,
            admin_id=current_user.id,
            nombre=body.nombre,
            descripcion=body.descripcion,
        )
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except CambioParametrosFinancierosError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.post(
    "/{natillera_id}/activar",
    response_model=NatilleraResponse,
    summary="Activar natillera y generar calendario de períodos",
)
def activar_natillera(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[NatilleraService, Depends(get_natillera_service)],
):
    try:
        return svc.activar(natillera_id, current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except NatilleraEstadoInvalidoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except SociosInsuficientesError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.post(
    "/{natillera_id}/cerrar",
    response_model=NatilleraResponse,
    summary="Cerrar natillera (no acepta más pagos)",
)
def cerrar_natillera(
    natillera_id: int,
    body: CerrarNatilleraRequest,
    current_user: CurrentUser,
    svc: Annotated[NatilleraService, Depends(get_natillera_service)],
):
    try:
        return svc.cerrar(natillera_id, current_user.id, forzar=body.forzar)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except NatilleraEstadoInvalidoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.post(
    "/{natillera_id}/archivar",
    response_model=NatilleraResponse,
    summary="Archivar natillera cerrada",
)
def archivar_natillera(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[NatilleraService, Depends(get_natillera_service)],
):
    try:
        return svc.archivar(natillera_id, current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except NatilleraEstadoInvalidoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.get(
    "/{natillera_id}/periodos",
    response_model=List[PeriodoResponse],
    summary="Listar períodos de la natillera",
)
def listar_periodos(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[NatilleraService, Depends(get_natillera_service)],
):
    try:
        return svc.listar_periodos(natillera_id, current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
