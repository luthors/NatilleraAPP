"""
NotificacionService — email notifications via aiosmtplib + Observer event handlers.

Registers handlers for domain events and sends email notifications:
  - usuario.registrado          → welcome email
  - usuario.solicito_recuperacion → password reset link
  - pago.confirmado             → payment confirmed
  - pago.rechazado              → payment rejected
  - socio.en_mora               → overdue payment warning
  - invitacion.creada           → invitation link
  - natillera.activada          → natillera is now active
  - distribucion.ejecutada      → final distribution summary

References:
- ISSUE-23: notification service
- HU-01-04: password recovery email
- HU-05-01: payment confirmation email
- RNF-07: email must be sent within 60 seconds of the triggering event
"""
import asyncio
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib

from app.core.config import settings
from app.core.events import on

logger = logging.getLogger(__name__)


# ─── Email sending ────────────────────────────────────────────────────────────

async def _send_email(to: str, subject: str, html_body: str) -> None:
    """Send a single email. Silently logs and returns on failure (never raises)."""
    if not settings.EMAILS_ENABLED:
        logger.info(
            "[email DISABLED] To=%s | Subject=%s", to, subject
        )
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info("[email SENT] To=%s | Subject=%s", to, subject)
    except Exception as exc:  # pragma: no cover
        logger.error("[email FAILED] To=%s | Error=%s", to, exc)


def _run_async(coro) -> None:
    """Run an async coroutine from a synchronous event handler."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(coro)
        else:
            loop.run_until_complete(coro)
    except RuntimeError:
        asyncio.run(coro)


# ─── HTML helpers ─────────────────────────────────────────────────────────────

def _base_template(title: str, body: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8"/>
      <title>{title}</title>
    </head>
    <body style="font-family:Arial,sans-serif;color:#333;max-width:600px;margin:auto;padding:20px;">
      <div style="background:#4f46e5;padding:16px;border-radius:8px 8px 0 0;">
        <h1 style="color:#fff;margin:0;font-size:20px;">🏦 Natillera App</h1>
      </div>
      <div style="border:1px solid #e5e7eb;border-top:none;padding:24px;border-radius:0 0 8px 8px;">
        {body}
      </div>
      <p style="color:#9ca3af;font-size:12px;text-align:center;margin-top:16px;">
        Este mensaje fue enviado automáticamente, por favor no respondas a este correo.
      </p>
    </body>
    </html>
    """


# ─── Event handlers ───────────────────────────────────────────────────────────

@on("usuario.registrado")
def handle_usuario_registrado(usuario, **_):
    body = f"""
    <h2>¡Bienvenido/a, {usuario.nombre}!</h2>
    <p>Tu cuenta en <strong>Natillera App</strong> ha sido creada exitosamente.</p>
    <p>Ya puedes iniciar sesión y crear o unirte a una natillera.</p>
    <p style="margin-top:24px;">
      <a href="{settings.FRONTEND_BASE_URL}/login"
         style="background:#4f46e5;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;">
        Iniciar sesión
      </a>
    </p>
    """
    _run_async(_send_email(
        to=usuario.email,
        subject="¡Bienvenido/a a Natillera App!",
        html_body=_base_template("Bienvenido", body),
    ))


@on("usuario.solicito_recuperacion")
def handle_recuperacion(usuario, token: str, **_):
    link = f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}"
    body = f"""
    <h2>Recuperación de contraseña</h2>
    <p>Hola {usuario.nombre}, recibimos una solicitud para restablecer tu contraseña.</p>
    <p>Haz clic en el botón para crear una nueva contraseña. Este enlace expira en
       <strong>{settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hora(s)</strong>.</p>
    <p style="margin-top:24px;">
      <a href="{link}"
         style="background:#4f46e5;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;">
        Restablecer contraseña
      </a>
    </p>
    <p style="margin-top:16px;color:#6b7280;font-size:13px;">
      Si no solicitaste este cambio, ignora este correo.
    </p>
    """
    _run_async(_send_email(
        to=usuario.email,
        subject="Restablece tu contraseña — Natillera App",
        html_body=_base_template("Recuperación de contraseña", body),
    ))


@on("invitacion.creada")
def handle_invitacion_creada(invitacion, natillera, invitado_email: str, **_):
    link = f"{settings.FRONTEND_BASE_URL}/invitacion/{invitacion.token}"
    body = f"""
    <h2>Has sido invitado/a a una Natillera</h2>
    <p>Te invitaron a unirte a <strong>{natillera.nombre}</strong>.</p>
    <p>Haz clic en el botón para aceptar la invitación. El enlace expira en 48 horas.</p>
    <p style="margin-top:24px;">
      <a href="{link}"
         style="background:#4f46e5;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;">
        Aceptar invitación
      </a>
    </p>
    """
    _run_async(_send_email(
        to=invitado_email,
        subject=f"Invitación a la Natillera '{natillera.nombre}'",
        html_body=_base_template("Invitación a Natillera", body),
    ))


@on("pago.confirmado")
def handle_pago_confirmado(pago, socio, natillera, **_):
    body = f"""
    <h2>Pago confirmado ✅</h2>
    <p>Hola {socio.usuario.nombre},</p>
    <p>Tu aporte de <strong>${pago.monto}</strong> para el período
       <strong>{pago.periodo.nombre}</strong> de la natillera
       <strong>{natillera.nombre}</strong> fue confirmado.</p>
    <p>Gracias por mantenerte al día.</p>
    """
    _run_async(_send_email(
        to=socio.usuario.email,
        subject=f"Pago confirmado — {natillera.nombre}",
        html_body=_base_template("Pago confirmado", body),
    ))


@on("pago.rechazado")
def handle_pago_rechazado(pago, socio, natillera, motivo: Optional[str] = None, **_):
    motivo_text = f"<p><strong>Motivo:</strong> {motivo}</p>" if motivo else ""
    body = f"""
    <h2>Pago rechazado ❌</h2>
    <p>Hola {socio.usuario.nombre},</p>
    <p>Tu pago registrado para el período <strong>{pago.periodo.nombre}</strong> de la
       natillera <strong>{natillera.nombre}</strong> fue rechazado.</p>
    {motivo_text}
    <p>Por favor comunícate con el administrador para más información.</p>
    """
    _run_async(_send_email(
        to=socio.usuario.email,
        subject=f"Pago rechazado — {natillera.nombre}",
        html_body=_base_template("Pago rechazado", body),
    ))


@on("socio.en_mora")
def handle_socio_en_mora(socio, natillera, periodos_mora: int, **_):
    body = f"""
    <h2>Aviso de mora ⚠️</h2>
    <p>Hola {socio.usuario.nombre},</p>
    <p>Tienes <strong>{periodos_mora} período(s) vencido(s)</strong> sin pago en la natillera
       <strong>{natillera.nombre}</strong>.</p>
    <p>Por favor realiza tus pagos a la brevedad para evitar la suspensión de tu membresía.</p>
    <p style="margin-top:24px;">
      <a href="{settings.FRONTEND_BASE_URL}/natilleras/{natillera.id}"
         style="background:#dc2626;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;">
        Ver mis pagos
      </a>
    </p>
    """
    _run_async(_send_email(
        to=socio.usuario.email,
        subject=f"Aviso de mora — {natillera.nombre}",
        html_body=_base_template("Aviso de mora", body),
    ))


@on("natillera.activada")
def handle_natillera_activada(natillera, admin, **_):
    body = f"""
    <h2>Natillera activada 🎉</h2>
    <p>Hola {admin.nombre},</p>
    <p>La natillera <strong>{natillera.nombre}</strong> ha sido activada exitosamente.</p>
    <p>El primer período de aportes ya está abierto.</p>
    <p style="margin-top:24px;">
      <a href="{settings.FRONTEND_BASE_URL}/natilleras/{natillera.id}"
         style="background:#4f46e5;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;">
        Ver natillera
      </a>
    </p>
    """
    _run_async(_send_email(
        to=admin.email,
        subject=f"Natillera '{natillera.nombre}' activada",
        html_body=_base_template("Natillera activada", body),
    ))


@on("distribucion.ejecutada")
def handle_distribucion_ejecutada(distribucion, natillera, admin, **_):
    body = f"""
    <h2>Distribución final ejecutada 💰</h2>
    <p>Hola {admin.nombre},</p>
    <p>La distribución final de la natillera <strong>{natillera.nombre}</strong>
       se ejecutó correctamente.</p>
    <p>Monto total distribuido: <strong>${distribucion.monto_total}</strong></p>
    <p>Descarga el reporte desde el panel de administración.</p>
    """
    _run_async(_send_email(
        to=admin.email,
        subject=f"Distribución final ejecutada — {natillera.nombre}",
        html_body=_base_template("Distribución ejecutada", body),
    ))
