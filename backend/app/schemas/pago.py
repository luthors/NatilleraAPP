"""
Pago and Distribucion Pydantic schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

from app.models.pago import EstadoPago, MetodoPago
from app.models.distribucion import TipoDistribucion


class RegistrarPagoAdminRequest(BaseModel):
    socio_id: int
    periodo_id: int
    monto: Decimal
    metodo: MetodoPago
    referencia: Optional[str] = None
    forzar: bool = False   # allow amount mismatch


class RegistrarPagoSocioRequest(BaseModel):
    periodo_id: int
    metodo: MetodoPago
    referencia: Optional[str] = None
    comprobante_url: Optional[str] = None


class GestionarPagoRequest(BaseModel):
    """Used for confirm and reject actions."""
    razon: Optional[str] = None   # mandatory for rejection


class RevertirPagoRequest(BaseModel):
    justificacion: str
    password_confirmar: Optional[str] = None  # required if payment > 72h old


class PagoResponse(BaseModel):
    id: int
    natillera_id: int
    socio_id: int
    periodo_id: int
    monto: Decimal
    metodo: MetodoPago
    estado: EstadoPago
    referencia: Optional[str]
    comprobante_url: Optional[str]
    razon: Optional[str]
    recibo_referencia: Optional[str]
    recibo_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Saldos ───────────────────────────────────────────────────────────────────

class SaldoFondoResponse(BaseModel):
    natillera_id: int
    saldo_total: Decimal
    aportes_periodo_actual: Decimal
    aportes_pendientes_periodo: Decimal
    total_distribuido: Decimal


class EstadoSocioResponse(BaseModel):
    socio_id: int
    natillera_id: int
    total_aportado: Decimal
    periodos_pagados: int
    periodos_pendientes: int
    monto_en_mora: Decimal
    tiene_mora: bool
    proximo_pago_fecha: Optional[str]
    proximo_pago_monto: Optional[Decimal]


# ─── Distribuciones ───────────────────────────────────────────────────────────

class DistribucionSocioPreview(BaseModel):
    socio_id: int
    nombre_socio: str
    monto_base: Decimal
    total_a_recibir: Decimal


class DistribucionPreviewResponse(BaseModel):
    natillera_id: int
    saldo_total: Decimal
    total_socios_activos: int
    distribucion: list[DistribucionSocioPreview]


class DistribucionResponse(BaseModel):
    id: int
    natillera_id: int
    socio_id: int
    monto: Decimal
    tipo: TipoDistribucion

    model_config = {"from_attributes": True}
