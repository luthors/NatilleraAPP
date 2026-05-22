"""
Authentication and User Pydantic schemas.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

from app.core.security import validate_password_strength


# ─── Auth ─────────────────────────────────────────────────────────────────────

class RegistroRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        validate_password_strength(v)
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RecuperarPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    nueva_password: str

    @field_validator("nueva_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        validate_password_strength(v)
        return v


# ─── Usuario ──────────────────────────────────────────────────────────────────

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    telefono: Optional[str] = None
    foto_url: Optional[str] = None
    is_active: bool
    email_verificado: bool

    model_config = {"from_attributes": True}


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    foto_url: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def nombre_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip() if v else v
