"""
Main API v1 router — aggregates all endpoint routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    usuarios,
    natilleras,
    socios,
    pagos,
    distribuciones,
    reportes,
    verificar,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(natilleras.router)
api_router.include_router(socios.router)
api_router.include_router(pagos.router)
api_router.include_router(distribuciones.router)
api_router.include_router(reportes.router)
api_router.include_router(verificar.router)
