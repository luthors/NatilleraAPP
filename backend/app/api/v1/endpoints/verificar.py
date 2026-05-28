"""
Verificar endpoint — public QR code validation for payment receipts.

References:
- ISSUE-28: QR verification
- HU-05-03: comprobante verification
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.dependencies import get_pago_repo
from app.repositories.pago_repo import PagoRepository

router = APIRouter(prefix="/verificar", tags=["verificar"])


class VerificacionResponse(BaseModel):
    valido: bool
    referencia: str
    natillera: str
    socio_nombre: str
    periodo: str
    monto: str
    estado: str
    fecha_confirmacion: str | None


@router.get(
    "/{referencia}",
    response_model=VerificacionResponse,
    summary="Verificar autenticidad de comprobante por referencia (endpoint público)",
)
def verificar_comprobante(
    referencia: str,
    pago_repo: Annotated[PagoRepository, Depends(get_pago_repo)],
):
    pago = pago_repo.get_by_recibo_referencia(referencia)
    if pago is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comprobante no encontrado o referencia inválida.",
        )

    from app.models.pago import EstadoPago
    socio_nombre = (
        pago.socio.usuario.nombre
        if pago.socio and pago.socio.usuario
        else f"Socio #{pago.socio_id}"
    )
    fecha_str = (
        pago.gestionado_at.strftime("%d/%m/%Y %H:%M UTC")
        if pago.gestionado_at
        else None
    )

    return VerificacionResponse(
        valido=pago.estado == EstadoPago.CONFIRMADO,
        referencia=referencia,
        natillera=pago.natillera.nombre if pago.natillera else str(pago.natillera_id),
        socio_nombre=socio_nombre,
        periodo=pago.periodo.nombre if pago.periodo else str(pago.periodo_id),
        monto=f"${pago.monto:,.2f}",
        estado=pago.estado.value,
        fecha_confirmacion=fecha_str,
    )
