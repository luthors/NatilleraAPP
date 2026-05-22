"""
AuditRepository — insert-only access to the audit_log table.

This repository intentionally has NO update() or delete() methods.
The audit log is immutable once written (HU-09-01, RNF-10).

A PostgreSQL trigger should be added as a second line of defence:
    CREATE OR REPLACE FUNCTION prevent_audit_mutation()
    RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'audit_logs is immutable — no UPDATE or DELETE allowed';
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER audit_immutable
    BEFORE UPDATE OR DELETE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION prevent_audit_mutation();
"""
from datetime import datetime, timezone
from typing import Optional, Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, id: int) -> Optional[AuditLog]:
        return self.db.get(AuditLog, id)

    def registrar(
        self,
        accion: str,
        entidad: str,
        entidad_id: Optional[int] = None,
        usuario_id: Optional[int] = None,
        ip: Optional[str] = None,
        datos_anteriores: Optional[dict] = None,
        datos_nuevos: Optional[dict] = None,
    ) -> AuditLog:
        """
        Insert one immutable audit record.

        Args:
            accion: Short action name, e.g. 'CONFIRMAR_PAGO', 'CERRAR_NATILLERA'.
            entidad: Model name, e.g. 'Pago', 'Natillera'.
            entidad_id: Primary key of the affected record.
            usuario_id: ID of the user who performed the action.
            ip: Client IP address from the request.
            datos_anteriores: Snapshot of the entity before the change.
            datos_nuevos: Snapshot of the entity after the change.
        """
        log = AuditLog(
            accion=accion,
            entidad=entidad,
            entidad_id=entidad_id,
            usuario_id=usuario_id,
            ip=ip,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(log)
        self.db.flush()
        return log

    def get_by_natillera(
        self,
        natillera_id: int,
        page: int = 1,
        size: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """Return paginated audit logs where entidad_id = natillera_id."""
        query = (
            self.db.query(AuditLog)
            .filter(AuditLog.entidad_id == natillera_id)
            .order_by(AuditLog.created_at.desc())
        )
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return items, total

    def get_by_usuario(self, usuario_id: int, page: int = 1, size: int = 50) -> tuple[list[AuditLog], int]:
        query = (
            self.db.query(AuditLog)
            .filter(AuditLog.usuario_id == usuario_id)
            .order_by(AuditLog.created_at.desc())
        )
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return items, total
