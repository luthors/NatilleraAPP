"""
Natillera API — Application entry point.

Responsibilities:
- Create FastAPI app with Swagger/OpenAPI config
- Register CORS middleware
- Register exception handlers (domain → HTTP)
- Include API v1 router
- Configure lifespan: start/stop APScheduler for mora detection

References:
- RNF-01: CORS only from ALLOWED_ORIGINS
- RNF-07: nightly mora detection scheduler
- docs/design/01-arquitectura-capas.md
"""
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.exceptions import NatilleraAppError
from app.api.v1.router import api_router

# Import notification handlers so they register on startup
import app.services.notificacion_service  # noqa: F401

logger = logging.getLogger(__name__)

# ─── Scheduler ────────────────────────────────────────────────────────────────

scheduler = AsyncIOScheduler()


async def _run_mora_detection() -> None:
    """
    Nightly job: detect socios in mora and emit 'socio.en_mora' events.
    Runs inside its own DB session (independent UoW).
    """
    from app.database import SessionLocal
    from app.repositories.natillera_repo import NatilleraRepository, PeriodoRepository
    from app.repositories.socio_repo import SocioRepository
    from app.repositories.pago_repo import PagoRepository
    from app.services.saldo_service import SaldoService
    from app.models.natillera import EstadoNatillera

    db = SessionLocal()
    try:
        natillera_repo = NatilleraRepository(db)
        periodo_repo = PeriodoRepository(db)
        socio_repo = SocioRepository(db)
        pago_repo = PagoRepository(db)

        saldo_svc = SaldoService(
            natillera_repo=natillera_repo,
            periodo_repo=periodo_repo,
            socio_repo=socio_repo,
            pago_repo=pago_repo,
            db=db,
        )
        # Fetch all active natilleras
        natilleras = natillera_repo.get_all_by_estado(EstadoNatillera.ACTIVA)
        for natillera in natilleras:
            try:
                saldo_svc.detectar_y_notificar_mora(natillera.id)
            except Exception as exc:
                logger.error(
                    "[mora-detection] natillera_id=%s error=%s", natillera.id, exc
                )
        db.commit()
        logger.info("[mora-detection] Completed for %d natilleras.", len(natilleras))
    except Exception as exc:
        db.rollback()
        logger.error("[mora-detection] Fatal error: %s", exc)
    finally:
        db.close()


# ─── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/avatars", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/comprobantes", exist_ok=True)

    scheduler.add_job(
        _run_mora_detection,
        CronTrigger(hour=2, minute=0),  # 2:00 AM daily
        id="mora_detection",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started — mora detection job scheduled at 02:00 daily.")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("APScheduler stopped.")


# ─── App factory ──────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API REST para **Natillera App** — plataforma de fondos de ahorro comunitario colombianos.\n\n"
        "## Autenticación\n"
        "Usa el endpoint `POST /api/v1/auth/login` para obtener un JWT Bearer token "
        "y luego haz clic en **Authorize** arriba.\n\n"
        "## Reglas de negocio clave\n"
        "- **RN-06**: Los pagos confirmados nunca se eliminan, solo se revierten.\n"
        "- **RN-07**: La distribución final requiere estado `EN_CIERRE`.\n"
        "- **RN-10**: Saldo = aportes CONFIRMADOS − distribuciones.\n"
        "- **RN-12**: Mínimo 2 socios para activar una natillera.\n"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static files (uploads) ───────────────────────────────────────────────────

import os
if os.path.isdir(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ─── Exception handlers ───────────────────────────────────────────────────────

_EXCEPTION_STATUS_MAP: dict[type, int] = {
    # auth
    __import__("app.core.exceptions", fromlist=["EmailYaRegistradoError"]).EmailYaRegistradoError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["CredencialesInvalidasError"]).CredencialesInvalidasError: status.HTTP_401_UNAUTHORIZED,
    __import__("app.core.exceptions", fromlist=["CuentaBloqueadaError"]).CuentaBloqueadaError: status.HTTP_403_FORBIDDEN,
    __import__("app.core.exceptions", fromlist=["TokenInvalidoError"]).TokenInvalidoError: status.HTTP_401_UNAUTHORIZED,
    __import__("app.core.exceptions", fromlist=["TokenExpiradoError"]).TokenExpiradoError: status.HTTP_400_BAD_REQUEST,
    __import__("app.core.exceptions", fromlist=["AccesoNoAutorizadoError"]).AccesoNoAutorizadoError: status.HTTP_403_FORBIDDEN,
    # users
    __import__("app.core.exceptions", fromlist=["UsuarioNoEncontradoError"]).UsuarioNoEncontradoError: status.HTTP_404_NOT_FOUND,
    __import__("app.core.exceptions", fromlist=["ArchivoInvalidoError"]).ArchivoInvalidoError: status.HTTP_400_BAD_REQUEST,
    # natilleras
    __import__("app.core.exceptions", fromlist=["NatilleraNoEncontradaError"]).NatilleraNoEncontradaError: status.HTTP_404_NOT_FOUND,
    __import__("app.core.exceptions", fromlist=["NatilleraEstadoInvalidoError"]).NatilleraEstadoInvalidoError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["CambioParametrosFinancierosError"]).CambioParametrosFinancierosError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["SociosInsuficientesError"]).SociosInsuficientesError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["CupoMaximoAlcanzadoError"]).CupoMaximoAlcanzadoError: status.HTTP_409_CONFLICT,
    # socios
    __import__("app.core.exceptions", fromlist=["SocioNoEncontradoError"]).SocioNoEncontradoError: status.HTTP_404_NOT_FOUND,
    __import__("app.core.exceptions", fromlist=["SocioEnMoraError"]).SocioEnMoraError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["SocioConPagosError"]).SocioConPagosError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["SocioYaExisteError"]).SocioYaExisteError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["InvitacionInvalidaError"]).InvitacionInvalidaError: status.HTTP_400_BAD_REQUEST,
    # pagos
    __import__("app.core.exceptions", fromlist=["PagoNoEncontradoError"]).PagoNoEncontradoError: status.HTTP_404_NOT_FOUND,
    __import__("app.core.exceptions", fromlist=["PagoYaExisteError"]).PagoYaExisteError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["PagoYaConfirmadoError"]).PagoYaConfirmadoError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["PagoNoConfirmadoError"]).PagoNoConfirmadoError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["MontoIncorrectoError"]).MontoIncorrectoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    __import__("app.core.exceptions", fromlist=["PeriodoNoEncontradoError"]).PeriodoNoEncontradoError: status.HTTP_404_NOT_FOUND,
    # distribuciones
    __import__("app.core.exceptions", fromlist=["FondosInsuficientesError"]).FondosInsuficientesError: status.HTTP_409_CONFLICT,
    __import__("app.core.exceptions", fromlist=["DistribucionNoPermitidaError"]).DistribucionNoPermitidaError: status.HTTP_409_CONFLICT,
}


@app.exception_handler(NatilleraAppError)
async def domain_exception_handler(request: Request, exc: NatilleraAppError) -> JSONResponse:
    http_status = _EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JSONResponse(
        status_code=http_status,
        content={"detail": exc.message},
    )


# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(api_router, prefix=settings.API_V1_STR)


# ─── Root endpoints ───────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root() -> dict[str, Any]:
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": settings.API_V1_STR,
    }


@app.get("/health", tags=["health"], summary="Health check")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "version": settings.APP_VERSION}
