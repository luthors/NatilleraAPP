"""
Pagos endpoints — register, confirm, reject, revert + saldo + estado socio.

References:
- HU-04-01 to HU-04-04
- HU-05-01 to HU-05-03
- RN-06, RN-10
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import (
    NatilleraNoEncontradaError,
    AccesoNoAutorizadoError,
    SocioNoEncontradoError,
    PagoNoEncontradoError,
    PagoYaExisteError,
    PagoYaConfirmadoError,
    PagoNoConfirmadoError,
    MontoIncorrectoError,
    PeriodoNoEncontradoError,
)
from app.dependencies import CurrentUser, get_pago_service, get_saldo_service
from app.schemas.pago import (
    RegistrarPagoAdminRequest,
    RegistrarPagoSocioRequest,
    GestionarPagoRequest,
    RevertirPagoRequest,
    PagoResponse,
    SaldoFondoResponse,
    EstadoSocioResponse,
)
from app.services.pago_service import PagoService
from app.services.saldo_service import SaldoService

router = APIRouter(prefix="/natilleras/{natillera_id}", tags=["pagos"])


# ─── Admin actions ────────────────────────────────────────────────────────────

@router.post(
    "/pagos/admin",
    response_model=PagoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin registra pago de un socio",
)
def registrar_pago_admin(
    natillera_id: int,
    body: RegistrarPagoAdminRequest,
    current_user: CurrentUser,
    svc: Annotated[PagoService, Depends(get_pago_service)],
):
    try:
        return svc.registrar_por_admin(
            natillera_id=natillera_id,
            admin_id=current_user.id,
            socio_id=body.socio_id,
            periodo_id=body.periodo_id,
            monto=body.monto,
            metodo=body.metodo,
            referencia=body.referencia,
            forzar=body.forzar,
        )
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except (SocioNoEncontradoError, PeriodoNoEncontradoError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except PagoYaExisteError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except MontoIncorrectoError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message)


@router.post(
    "/pagos/confirmar/{pago_id}",
    response_model=PagoResponse,
    summary="Admin confirma pago pendiente",
)
def confirmar_pago(
    natillera_id: int,
    pago_id: int,
    body: GestionarPagoRequest,
    current_user: CurrentUser,
    svc: Annotated[PagoService, Depends(get_pago_service)],
):
    try:
        return svc.confirmar(
            pago_id=pago_id,
            admin_id=current_user.id,
            natillera_id=natillera_id,
        )
    except PagoNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except PagoYaConfirmadoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.post(
    "/pagos/rechazar/{pago_id}",
    response_model=PagoResponse,
    summary="Admin rechaza pago pendiente",
)
def rechazar_pago(
    natillera_id: int,
    pago_id: int,
    body: GestionarPagoRequest,
    current_user: CurrentUser,
    svc: Annotated[PagoService, Depends(get_pago_service)],
):
    try:
        return svc.rechazar(
            pago_id=pago_id,
            admin_id=current_user.id,
            natillera_id=natillera_id,
            razon=body.razon,
        )
    except PagoNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except PagoYaConfirmadoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


@router.post(
    "/pagos/revertir/{pago_id}",
    response_model=PagoResponse,
    summary="Admin revierte pago confirmado (RN-06)",
)
def revertir_pago(
    natillera_id: int,
    pago_id: int,
    body: RevertirPagoRequest,
    current_user: CurrentUser,
    svc: Annotated[PagoService, Depends(get_pago_service)],
):
    try:
        return svc.revertir(
            pago_id=pago_id,
            admin_id=current_user.id,
            natillera_id=natillera_id,
            justificacion=body.justificacion,
        )
    except PagoNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except PagoNoConfirmadoError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)


# ─── Socio self-register ──────────────────────────────────────────────────────

@router.post(
    "/mis-pagos",
    response_model=PagoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Socio registra su propio pago (pendiente de confirmación)",
)
def registrar_pago_socio(
    natillera_id: int,
    body: RegistrarPagoSocioRequest,
    current_user: CurrentUser,
    svc: Annotated[PagoService, Depends(get_pago_service)],
):
    try:
        return svc.registrar_por_socio(
            natillera_id=natillera_id,
            usuario_id=current_user.id,
            periodo_id=body.periodo_id,
            metodo=body.metodo,
            referencia=body.referencia,
            comprobante_url=body.comprobante_url,
        )
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except SocioNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    except (PagoYaExisteError,) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except PeriodoNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(
    "/mis-pagos",
    response_model=List[PagoResponse],
    summary="Socio ve su historial de pagos en la natillera",
)
def mis_pagos(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[PagoService, Depends(get_pago_service)],
):
    try:
        return svc.listar_por_socio(natillera_id=natillera_id, usuario_id=current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except SocioNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


@router.get(
    "/pagos",
    response_model=List[PagoResponse],
    summary="Admin lista todos los pagos de la natillera",
)
def listar_pagos(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[PagoService, Depends(get_pago_service)],
):
    try:
        return svc.listar_por_natillera(natillera_id=natillera_id, admin_id=current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


# ─── Saldo / estado ───────────────────────────────────────────────────────────

@router.get(
    "/saldo",
    response_model=SaldoFondoResponse,
    summary="Saldo del fondo (admin)",
)
def saldo_fondo(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[SaldoService, Depends(get_saldo_service)],
):
    try:
        return svc.calcular_saldo_fondo(natillera_id, current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


@router.get(
    "/mi-estado",
    response_model=EstadoSocioResponse,
    summary="Estado de cuenta personal del socio",
)
def mi_estado(
    natillera_id: int,
    current_user: CurrentUser,
    svc: Annotated[SaldoService, Depends(get_saldo_service)],
):
    try:
        return svc.calcular_estado_socio(natillera_id, current_user.id)
    except NatilleraNoEncontradaError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except SocioNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
