"""
UsuarioRepository — all database access for the Usuario model.

Services must use this repository instead of querying SQLAlchemy directly.
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id: int) -> Optional[Usuario]:
        return self.db.get(Usuario, id)

    def get_by_email(self, email: str) -> Optional[Usuario]:
        return (
            self.db.query(Usuario)
            .filter(Usuario.email == email.lower().strip())
            .first()
        )

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def update(self, usuario: Usuario, **fields) -> Usuario:
        for key, value in fields.items():
            setattr(usuario, key, value)
        self.db.flush()
        self.db.refresh(usuario)
        return usuario
