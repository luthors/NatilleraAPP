"""
Models package — imports all models so Alembic can discover them via Base.metadata.

When adding a new model, import it here so:
1. Alembic autogenerate picks it up.
2. SQLAlchemy resolves all relationships at startup.
"""
from app.models.base import TimestampMixin  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401
from app.models.auth import RefreshToken, IntentoLogin, PasswordResetToken  # noqa: F401
from app.models.natillera import Natillera, EstadoNatillera, Periodicidad  # noqa: F401
from app.models.socio import Socio, Periodo, EstadoSocio, EstadoPeriodo  # noqa: F401
from app.models.pago import Pago, EstadoPago, MetodoPago  # noqa: F401
from app.models.distribucion import Distribucion, TipoDistribucion  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.invitacion import Invitacion  # noqa: F401

__all__ = [
    "TimestampMixin",
    "Usuario",
    "RefreshToken", "IntentoLogin", "PasswordResetToken",
    "Natillera", "EstadoNatillera", "Periodicidad",
    "Socio", "Periodo", "EstadoSocio", "EstadoPeriodo",
    "Pago", "EstadoPago", "MetodoPago",
    "Distribucion", "TipoDistribucion",
    "AuditLog",
    "Invitacion",
]
