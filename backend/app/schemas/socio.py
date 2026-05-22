"""
Socio and Invitacion Pydantic schemas.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.socio import EstadoSocio
from app.schemas.auth import UsuarioResponse


class SocioResponse(BaseModel):
    id: int
    natillera_id: int
    usuario_id: int
    estado: EstadoSocio
    usuario: UsuarioResponse

    model_config = {"from_attributes": True}


class SocioConEstadoPagoResponse(SocioResponse):
    """Admin view: includes payment status for current period."""
    total_aportado: Optional[str] = None       # formatted Decimal
    estado_periodo_actual: Optional[str] = None  # pagado / pendiente / en_mora
    tiene_mora: bool = False


class SuspenderSocioRequest(BaseModel):
    razon: str

    class Config:
        json_schema_extra = {
            "example": {"razon": "Incumplimiento en pagos durante 3 períodos consecutivos"}
        }


class InvitarSocioRequest(BaseModel):
    email: EmailStr


class InvitacionResponse(BaseModel):
    id: int
    natillera_id: int
    email_invitado: str
    expira_at: datetime
    aceptada: bool
    revocada: bool

    model_config = {"from_attributes": True}


class TransferirAdminRequest(BaseModel):
    nuevo_admin_usuario_id: int
    password: str
