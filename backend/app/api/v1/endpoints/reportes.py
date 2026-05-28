"""
Reportes endpoints — PDF comprobantes and natillera summary report.

References:
- ISSUE-25: PDF comprobantes
- HU-05-03: estado de cuenta PDF
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

import os

from app.core.config import settings
from app.core.exceptions import (
    PagoNoEncontradoError,
    AccesoNoAutorizadoError,
    NatilleraNoEncontradaError,
)
from app.dependencies import (
    CurrentUser,
    get_pago_service,
    get_comprobante_service,
    get_natillera_service,
)
from app.repositories.pago_repo import PagoRepository
from app.services.pago_service import PagoService
from app.services.comprobante_service import ComprobanteService
from app.services.natillera_service import NatilleraService

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get(
    "/comprobante/{pago_id}",
    summary="Descargar comprobante PDF de un pago confirmado",
)
def descargar_comprobante(
    pago_id: int,
    current_user: CurrentUser,
    pago_svc: Annotated[PagoService, Depends(get_pago_service)],
    comprobante_svc: Annotated[ComprobanteService, Depends(get_comprobante_service)],
):
    try:
        pago, socio, natillera, periodo = pago_svc.obtener_con_contexto(
            pago_id=pago_id,
            usuario_id=current_user.id,
        )
    except PagoNoEncontradoError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except AccesoNoAutorizadoError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)

    from app.models.pago import EstadoPago
    if pago.estado != EstadoPago.CONFIRMADO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede generar comprobante de pagos confirmados.",
        )

    referencia, relative_url = comprobante_svc.generar(pago, socio, natillera, periodo)

    # Update pago record if new receipt generated
    if not pago.recibo_referencia:
        pago_svc.actualizar_recibo(pago, referencia, relative_url)

    filepath = os.path.join(
        settings.UPLOAD_DIR, "comprobantes", f"{referencia}.pdf"
    )
    if not os.path.exists(filepath):
        # Fallback to .txt
        filepath = filepath.replace(".pdf", ".txt")
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo generar el comprobante.",
        )

    return FileResponse(
        path=filepath,
        filename=os.path.basename(filepath),
        media_type="application/pdf" if filepath.endswith(".pdf") else "text/plain",
    )
