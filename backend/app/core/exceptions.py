"""
Domain exceptions for Natillera App.

Services raise these exceptions instead of HTTPException.
A global handler in main.py converts them to the correct HTTP response.

This keeps services free of HTTP concerns and fully testable without
running a FastAPI server.

Reference: docs/design/01-arquitectura-capas.md
"""
from typing import Optional


# ─── Base ─────────────────────────────────────────────────────────────────────

class NatilleraAppError(Exception):
    """Base class for all domain exceptions."""

    def __init__(self, message: str = "An unexpected error occurred"):
        self.message = message
        super().__init__(self.message)


# ─── Authentication ───────────────────────────────────────────────────────────

class CredencialesInvalidasError(NatilleraAppError):
    """Raised when login credentials are wrong (generic — do not reveal which)."""
    def __init__(self):
        super().__init__("Credenciales incorrectas")


class CuentaBloqueadaError(NatilleraAppError):
    """Raised when account is locked due to too many failed login attempts."""
    def __init__(self, minutos: int = 15):
        self.minutos = minutos
        super().__init__(
            f"Cuenta bloqueada por {minutos} minutos debido a múltiples intentos fallidos"
        )


class TokenInvalidoError(NatilleraAppError):
    """Raised when a JWT or reset token is invalid or expired."""
    def __init__(self, detalle: str = "Token inválido o expirado"):
        super().__init__(detalle)


class TokenExpiradoError(NatilleraAppError):
    """Raised specifically when a reset / invitation token has expired."""
    def __init__(self):
        super().__init__("Enlace expirado, solicita uno nuevo")


class AccesoNoAutorizadoError(NatilleraAppError):
    """Raised when a user tries to access a resource they don't own."""
    def __init__(self, detalle: str = "No tienes permisos para realizar esta acción"):
        super().__init__(detalle)


# ─── Users ────────────────────────────────────────────────────────────────────

class EmailYaRegistradoError(NatilleraAppError):
    """Raised when trying to register with an already-existing email."""
    def __init__(self, email: str = ""):
        self.email = email
        super().__init__("Este correo ya está registrado")


class UsuarioNoEncontradoError(NatilleraAppError):
    def __init__(self, usuario_id: Optional[int] = None):
        self.usuario_id = usuario_id
        msg = f"Usuario {usuario_id} no encontrado" if usuario_id else "Usuario no encontrado"
        super().__init__(msg)


class ArchivoInvalidoError(NatilleraAppError):
    """Raised when uploaded file exceeds size or has invalid format."""
    def __init__(self, detalle: str = "Archivo inválido"):
        super().__init__(detalle)


# ─── Natilleras ───────────────────────────────────────────────────────────────

class NatilleraNoEncontradaError(NatilleraAppError):
    def __init__(self, natillera_id: Optional[int] = None):
        self.natillera_id = natillera_id
        msg = f"Natillera {natillera_id} no encontrada" if natillera_id else "Natillera no encontrada"
        super().__init__(msg)


class NatilleraEstadoInvalidoError(NatilleraAppError):
    """Raised when an operation is not allowed in the current natillera state."""
    def __init__(self, operacion: str, estado_actual: str):
        super().__init__(
            f"No se puede '{operacion}' una natillera en estado '{estado_actual}'"
        )


class CambioParametrosFinancierosError(NatilleraAppError):
    """Raised when trying to change financial params of an active natillera (RN-02, RN-03)."""
    def __init__(self):
        super().__init__(
            "No se pueden cambiar parámetros financieros de una natillera activa"
        )


class SociosInsuficientesError(NatilleraAppError):
    """Raised when activating a natillera with fewer than 2 active socios (RN-12)."""
    def __init__(self, minimo: int = 2):
        super().__init__(f"Se requieren al menos {minimo} socios para activar la natillera")


class CupoMaximoAlcanzadoError(NatilleraAppError):
    """Raised when trying to add more socios than max_socios (RN-12)."""
    def __init__(self):
        super().__init__("Cupo máximo de socios alcanzado")


# ─── Socios ───────────────────────────────────────────────────────────────────

class SocioNoEncontradoError(NatilleraAppError):
    def __init__(self, socio_id: Optional[int] = None):
        self.socio_id = socio_id
        msg = f"Socio {socio_id} no encontrado" if socio_id else "Socio no encontrado"
        super().__init__(msg)


class SocioEnMoraError(NatilleraAppError):
    """Raised when an operation is blocked because the socio has unpaid overdue periods (RN-04)."""
    def __init__(self):
        super().__init__(
            "El socio tiene pagos en mora. Debe ponerse al día antes de realizar esta operación"
        )


class SocioConPagosError(NatilleraAppError):
    """Raised when trying to delete a socio who already has payments (RN-09)."""
    def __init__(self):
        super().__init__(
            "El socio tiene aportes registrados. Usa 'Suspender' en su lugar"
        )


class SocioYaExisteError(NatilleraAppError):
    """Raised when a user is already a socio in the natillera."""
    def __init__(self):
        super().__init__("Este usuario ya es socio de la natillera")


class InvitacionInvalidaError(NatilleraAppError):
    def __init__(self, detalle: str = "Invitación inválida o ya utilizada"):
        super().__init__(detalle)


# ─── Pagos ────────────────────────────────────────────────────────────────────

class PagoNoEncontradoError(NatilleraAppError):
    def __init__(self, pago_id: Optional[int] = None):
        self.pago_id = pago_id
        msg = f"Pago {pago_id} no encontrado" if pago_id else "Pago no encontrado"
        super().__init__(msg)


class PagoYaExisteError(NatilleraAppError):
    """Raised when a socio already has an active (non-rejected) payment for the same period."""
    def __init__(self):
        super().__init__("Ya existe un pago registrado para este período")


class PagoYaConfirmadoError(NatilleraAppError):
    """Raised when trying to confirm an already confirmed payment (RN-06)."""
    def __init__(self, pago_id: Optional[int] = None):
        self.pago_id = pago_id
        super().__init__("El pago ya está confirmado")


class PagoNoConfirmadoError(NatilleraAppError):
    """Raised when trying to revert a payment that isn't confirmed."""
    def __init__(self):
        super().__init__("Solo se pueden revertir pagos confirmados")


class MontoIncorrectoError(NatilleraAppError):
    """Raised when payment amount differs from the natillera standard (warning, not block)."""
    def __init__(self, esperado: str, recibido: str):
        self.esperado = esperado
        self.recibido = recibido
        super().__init__(
            f"El monto ${recibido} no corresponde al aporte estándar ${esperado}. "
            "Envía 'forzar: true' para confirmar de todas formas"
        )


class PeriodoNoEncontradoError(NatilleraAppError):
    def __init__(self, periodo_id: Optional[int] = None):
        super().__init__(f"Período {periodo_id} no encontrado" if periodo_id else "Período no encontrado")


# ─── Distribuciones ───────────────────────────────────────────────────────────

class FondosInsuficientesError(NatilleraAppError):
    """Raised when trying to create a loan that exceeds the available fund balance."""
    def __init__(self, disponible: str = "", solicitado: str = ""):
        msg = "Fondos insuficientes en el fondo"
        if disponible and solicitado:
            msg += f". Disponible: ${disponible}, Solicitado: ${solicitado}"
        super().__init__(msg)


class DistribucionNoPermitidaError(NatilleraAppError):
    """Raised when trying to distribute before the natillera is closed (RN-07)."""
    def __init__(self):
        super().__init__(
            "La distribución final solo puede ejecutarse cuando el ciclo ha cerrado (RN-07)"
        )
