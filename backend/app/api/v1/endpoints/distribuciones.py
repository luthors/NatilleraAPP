"""
Distribuciones endpoints — preview y ejecución de distribución final.

References:
- HU-06-02: distribución final
- RN-07: solo cuando natillera está EN_CIERRE
- RN-04: socios en mora
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import (
    NatilleraNoEncontradaError,
    NatilleraEstadoInvalidoError,
    AccesoNoAutorizadoError,
    DistribucionNoPermitidaError,
)
from app.dependencies import CurrentUser, get_distribucion_service
from app.schemas.pago import DistribucionPreviewResponse, DistribucionResponse
from app.services.distribucion_service import DistribucionService

router = APIRouter(prefix="/natilleras/{natillera_id}/distribuciones", tags=["distribuciones"])


@router.get(
    "/preview",
    response_model=DistribucionPreviewResponse,
    summary="Previsualizar distribución final antes de ejecutar",
)
def preview_distribucion(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[DistribucionService, Depends(get_distribucion_service)],
):
    try:
        return svc.preview_distribucion_final(natillera_id, current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except (NatilleraEstadoInvalidoError, DistribucionNoPermitidaError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.post(
    "/ejecutar",
    response_model=List[DistribucionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Ejecutar distribución final (natillera pasa a CERRADA)",
)
def ejecutar_distribucion(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[DistribucionService, Depends(get_distribucion_service)],
):
    try:
        return svc.ejecutar_distribucion_final(natillera_id, current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except (NatilleraEstadoInvalidoError, DistribucionNoPermitidaError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
