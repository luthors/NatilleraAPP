"""fix schema drift — align migration with models

Revision ID: 0002_fix_schema_drift
Revises: 0001_initial
Create Date: 2026-06-07 00:00:00.000000

Changes:
- Remove `nombre` column from `periodos` (computed property in Python)
- Add `RETIRADO` value to estadosocio enum (model uses RETIRADO, migration had ELIMINADO)
- Remove `removed_at` missing column from socios (add it)
- `BIMESTRAL` in periodicidad enum is extra but harmless; we leave it (ALTER ENUM DROP VALUE
  is not supported in PostgreSQL — removing it would require recreating the type)
- Add `invitado_por_id` FK to invitaciones if missing
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0002_fix_schema_drift"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Drop `nombre` column from periodos (it's a @property on the model now)
    inspector = sa.inspect(conn)
    periodos_cols = [c["name"] for c in inspector.get_columns("periodos")]
    if "nombre" in periodos_cols:
        op.drop_column("periodos", "nombre")

    # 2. Add `removed_at` to socios if missing
    socios_cols = [c["name"] for c in inspector.get_columns("socios")]
    if "removed_at" not in socios_cols:
        op.add_column("socios", sa.Column("removed_at", sa.Date(), nullable=True))

    # 3. Add RETIRADO to estadosocio enum if missing
    # PostgreSQL: ALTER TYPE ... ADD VALUE is safe and idempotent-ish
    existing_enums = {r[0] for r in conn.execute(
        sa.text("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'estadosocio'")
    )}
    if "RETIRADO" not in existing_enums:
        op.execute("ALTER TYPE estadosocio ADD VALUE 'RETIRADO'")

    # 4. Add `invitado_por_id` to invitaciones if missing
    inv_cols = [c["name"] for c in inspector.get_columns("invitaciones")]
    if "invitado_por_id" not in inv_cols:
        op.add_column(
            "invitaciones",
            sa.Column("invitado_por_id", sa.Integer(), nullable=True),
        )
        op.create_foreign_key(
            "fk_invitaciones_invitado_por_id",
            "invitaciones", "usuarios",
            ["invitado_por_id"], ["id"],
        )

    # 5. Rename audit_log → audit_logs if needed (model uses __tablename__ = "audit_logs")
    tables = inspector.get_table_names()
    if "audit_log" in tables and "audit_logs" not in tables:
        op.rename_table("audit_log", "audit_logs")


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Re-add nombre column to periodos
    periodos_cols = [c["name"] for c in inspector.get_columns("periodos")]
    if "nombre" not in periodos_cols:
        op.add_column(
            "periodos",
            sa.Column("nombre", sa.String(length=100), nullable=True),
        )
