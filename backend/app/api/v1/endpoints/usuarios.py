"""
Usuarios endpoints — profile update and avatar upload.

References:
- HU-01-05: editar perfil
- HU-01-06: subir foto de perfil
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.core.config import settings
from app.core.exceptions import ArchivoInvalidoError, UsuarioNoEncontradoError
from app.dependencies import CurrentUser, get_usuario_repo
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.auth import UsuarioResponse, UsuarioUpdate

import os
import uuid

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.patch(
    "/me",
    response_model=UsuarioResponse,
    summary="Actualizar perfil del usuario autenticado",
)
def actualizar_perfil(
    body: UsuarioUpdate,
    current_user: CurrentUser,
    usuario_repo: Annotated[UsuarioRepository, Depends(get_usuario_repo)],
):
    updates = body.model_dump(exclude_none=True)
    if updates:
        usuario_repo.update(current_user, **updates)
    return current_user


@router.post(
    "/me/foto",
    response_model=UsuarioResponse,
    summary="Subir foto de perfil",
)
async def subir_foto(
    current_user: CurrentUser,
    usuario_repo: Annotated[UsuarioRepository, Depends(get_usuario_repo)],
    file: UploadFile = File(...),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de imagen no soportado. Usa JPEG, PNG o WebP.",
        )

    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"La imagen excede el tamaño máximo de {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    avatars_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(avatars_dir, exist_ok=True)
    filepath = os.path.join(avatars_dir, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    foto_url = f"/uploads/avatars/{filename}"
    usuario_repo.update(current_user, foto_url=foto_url)
    return current_user
