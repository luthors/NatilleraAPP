"""
Natillera and Periodo Pydantic schemas.
"""
from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator

from app.models.natillera import EstadoNatillera, Periodicidad


class NatilleraCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    monto_por_periodo: Decimal
    periodicidad: Periodicidad
    fecha_inicio: date
    fecha_fin: date
    max_socios: int = 20

    @field_validator("monto_por_periodo")
    @classmethod
    def monto_positivo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        return v

    @field_validator("max_socios")
    @classmethod
    def max_socios_minimo(cls, v: int) -> int:
        if v < 2:
            raise ValueError("max_socios debe ser al menos 2")
        return v

    @model_validator(mode="after")
    def fechas_coherentes(self) -> "NatilleraCreate":
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return self


class NatilleraUpdate(BaseModel):
    """Only name and description can be updated after creation (RN-02, RN-03)."""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class NatilleraResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    admin_id: int
    monto_por_periodo: Decimal
    periodicidad: Periodicidad
    fecha_inicio: date
    fecha_fin: date
    max_socios: int
    estado: EstadoNatillera

    model_config = {"from_attributes": True}


class PeriodoResponse(BaseModel):
    id: int
    natillera_id: int
    numero: int
    fecha_inicio: date
    fecha_fin: date
    estado: str

    model_config = {"from_attributes": True}


class CerrarNatilleraRequest(BaseModel):
    """Used to close a natillera even if there are socios in mora."""
    forzar: bool = False
