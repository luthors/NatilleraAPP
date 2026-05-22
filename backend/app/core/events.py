"""
Lightweight in-process event bus (Observer Pattern).

Services emit domain events via `emit()`. Handlers subscribe via the `@on()`
decorator. This decouples the notification system, audit logging, and other
side effects from the core business logic.

Reference: docs/design/02-patrones-diseno.md — Observer Pattern

Usage:
    # Register a handler
    from app.core.events import on

    @on("pago.confirmado")
    def enviar_email(pago, socio, **kwargs):
        email_service.enviar(socio.email, ...)

    # Emit an event from a service
    from app.core.events import emit

    emit("pago.confirmado", pago=pago, socio=socio, admin_id=admin_id)

Important:
    - Handlers run synchronously in the same thread as the emitter.
    - If a handler raises, the exception is caught and logged so it does
      NOT roll back the main business operation.
    - Critical notifications (mora, distribution) are always sent regardless
      of user preferences (HU-07-04).
"""
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

# Internal registry: event_name -> list of handler callables
_handlers: dict[str, list[Callable]] = {}


def on(event: str) -> Callable:
    """
    Decorator to register a function as a handler for `event`.

    Example:
        @on("pago.confirmado")
        def handler(pago, **kwargs):
            ...
    """
    def decorator(fn: Callable) -> Callable:
        _handlers.setdefault(event, []).append(fn)
        logger.debug("Registered handler '%s' for event '%s'", fn.__name__, event)
        return fn
    return decorator


def emit(event: str, **kwargs: Any) -> None:
    """
    Emit an event, calling all registered handlers.

    Handler exceptions are caught and logged — they never propagate back
    to the caller, so a failed email notification will never roll back a
    payment confirmation.

    Args:
        event: Name of the event (e.g. 'pago.confirmado').
        **kwargs: Arbitrary keyword arguments passed to each handler.
    """
    handlers = _handlers.get(event, [])
    if not handlers:
        logger.debug("Event '%s' emitted with no handlers registered", event)
        return

    for handler in handlers:
        try:
            handler(**kwargs)
        except Exception as exc:  # noqa: BLE001
            # Side effects must never break the main operation
            logger.error(
                "Handler '%s' failed for event '%s': %s",
                handler.__name__, event, exc,
                exc_info=True,
            )


def clear_handlers(event: Optional[str] = None) -> None:
    """
    Remove all handlers for `event`, or all handlers if event is None.
    Intended for use in tests only.
    """
    if event:
        _handlers.pop(event, None)
    else:
        _handlers.clear()


from typing import Optional  # noqa: E402 (after the function that uses it)
