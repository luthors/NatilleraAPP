"""initial schema — all tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-29 10:00:00.000000

Creates all tables for the Natillera App:
  - usuarios
  - refresh_tokens
  - intentos_login
  - password_reset_tokens
  - natilleras
  - socios
  - periodos
  - invitaciones
  - pagos
  - distribuciones
  - audit_log
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── usuarios ──────────────────────────────────────────────────────────────
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("telefono", sa.String(length=20), nullable=True),
        sa.Column("foto_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("email_verificado", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_id", "usuarios", ["id"])
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)

    # ── refresh_tokens ────────────────────────────────────────────────────────
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expira_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revocado", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_refresh_tokens_id", "refresh_tokens", ["id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
    op.create_index("ix_refresh_tokens_usuario_id", "refresh_tokens", ["usuario_id"])

    # ── intentos_login ────────────────────────────────────────────────────────
    op.create_table(
        "intentos_login",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("exitoso", sa.Boolean(), nullable=False),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_intentos_login_id", "intentos_login", ["id"])
    op.create_index("ix_intentos_login_usuario_id", "intentos_login", ["usuario_id"])

    # ── password_reset_tokens ──────────────────────────────────────────────────
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("expira_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usado", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_password_reset_tokens_token", "password_reset_tokens", ["token"], unique=True)

    # ── natilleras ────────────────────────────────────────────────────────────
    estado_natillera = postgresql.ENUM(
        "CONFIGURACION", "ACTIVA", "EN_CIERRE", "CERRADA", "ARCHIVADA",
        name="estadonatillera",
    )
    estado_natillera.create(op.get_bind())

    periodicidad = postgresql.ENUM(
        "SEMANAL", "QUINCENAL", "MENSUAL", "BIMESTRAL",
        name="periodicidad",
    )
    periodicidad.create(op.get_bind())

    op.create_table(
        "natilleras",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("monto_por_periodo", sa.Numeric(14, 2), nullable=False),
        sa.Column("periodicidad", sa.Enum("SEMANAL", "QUINCENAL", "MENSUAL", "BIMESTRAL", name="periodicidad"), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=False),
        sa.Column("max_socios", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("estado", sa.Enum("CONFIGURACION", "ACTIVA", "EN_CIERRE", "CERRADA", "ARCHIVADA", name="estadonatillera"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["admin_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_natilleras_id", "natilleras", ["id"])
    op.create_index("ix_natilleras_admin_id", "natilleras", ["admin_id"])

    # ── socios ────────────────────────────────────────────────────────────────
    estado_socio = postgresql.ENUM(
        "ACTIVO", "SUSPENDIDO", "ELIMINADO",
        name="estadosocio",
    )
    estado_socio.create(op.get_bind())

    op.create_table(
        "socios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("natillera_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("estado", sa.Enum("ACTIVO", "SUSPENDIDO", "ELIMINADO", name="estadosocio"), nullable=False),
        sa.Column("razon_suspension", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["natillera_id"], ["natilleras.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("natillera_id", "usuario_id", name="uq_socio_natillera_usuario"),
    )
    op.create_index("ix_socios_id", "socios", ["id"])
    op.create_index("ix_socios_natillera_id", "socios", ["natillera_id"])
    op.create_index("ix_socios_usuario_id", "socios", ["usuario_id"])

    # ── periodos ──────────────────────────────────────────────────────────────
    estado_periodo = postgresql.ENUM(
        "PENDIENTE", "ABIERTO", "CERRADO",
        name="estadoperiodo",
    )
    estado_periodo.create(op.get_bind())

    op.create_table(
        "periodos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("natillera_id", sa.Integer(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=False),
        sa.Column("estado", sa.Enum("PENDIENTE", "ABIERTO", "CERRADO", name="estadoperiodo"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["natillera_id"], ["natilleras.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_periodos_id", "periodos", ["id"])
    op.create_index("ix_periodos_natillera_id", "periodos", ["natillera_id"])

    # ── invitaciones ──────────────────────────────────────────────────────────
    op.create_table(
        "invitaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("natillera_id", sa.Integer(), nullable=False),
        sa.Column("email_invitado", sa.String(length=255), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("expira_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("aceptada", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("revocada", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["natillera_id"], ["natilleras.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invitaciones_id", "invitaciones", ["id"])
    op.create_index("ix_invitaciones_token", "invitaciones", ["token"], unique=True)

    # ── pagos ─────────────────────────────────────────────────────────────────
    estado_pago = postgresql.ENUM(
        "PENDIENTE_CONFIRMACION", "CONFIRMADO", "RECHAZADO", "REVERTIDO",
        name="estadopago",
    )
    estado_pago.create(op.get_bind())

    metodo_pago = postgresql.ENUM(
        "EFECTIVO", "TRANSFERENCIA", "STRIPE", "PSE",
        name="metodopago",
    )
    metodo_pago.create(op.get_bind())

    op.create_table(
        "pagos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("natillera_id", sa.Integer(), nullable=False),
        sa.Column("socio_id", sa.Integer(), nullable=False),
        sa.Column("periodo_id", sa.Integer(), nullable=False),
        sa.Column("monto", sa.Numeric(14, 2), nullable=False),
        sa.Column("metodo", sa.Enum("EFECTIVO", "TRANSFERENCIA", "STRIPE", "PSE", name="metodopago"), nullable=False),
        sa.Column("estado", sa.Enum("PENDIENTE_CONFIRMACION", "CONFIRMADO", "RECHAZADO", "REVERTIDO", name="estadopago"), nullable=False),
        sa.Column("referencia", sa.String(length=255), nullable=True),
        sa.Column("comprobante_url", sa.String(length=500), nullable=True),
        sa.Column("gestionado_por_id", sa.Integer(), nullable=True),
        sa.Column("gestionado_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("razon", sa.String(length=500), nullable=True),
        sa.Column("recibo_referencia", sa.String(length=50), nullable=True),
        sa.Column("recibo_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["gestionado_por_id"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["natillera_id"], ["natilleras.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["periodo_id"], ["periodos.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["socio_id"], ["socios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recibo_referencia"),
    )
    op.create_index("ix_pagos_id", "pagos", ["id"])
    op.create_index("ix_pagos_natillera_id", "pagos", ["natillera_id"])
    op.create_index("ix_pagos_socio_id", "pagos", ["socio_id"])
    op.create_index("ix_pagos_estado", "pagos", ["estado"])
    op.create_index("ix_pagos_recibo_referencia", "pagos", ["recibo_referencia"])

    # ── distribuciones ────────────────────────────────────────────────────────
    tipo_distribucion = postgresql.ENUM(
        "FINAL", "PARCIAL", "INTERESES",
        name="tipodistribucion",
    )
    tipo_distribucion.create(op.get_bind())

    op.create_table(
        "distribuciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("natillera_id", sa.Integer(), nullable=False),
        sa.Column("socio_id", sa.Integer(), nullable=False),
        sa.Column("monto", sa.Numeric(14, 2), nullable=False),
        sa.Column("tipo", sa.Enum("FINAL", "PARCIAL", "INTERESES", name="tipodistribucion"), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["natillera_id"], ["natilleras.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["socio_id"], ["socios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_distribuciones_id", "distribuciones", ["id"])
    op.create_index("ix_distribuciones_natillera_id", "distribuciones", ["natillera_id"])

    # ── audit_log ─────────────────────────────────────────────────────────────
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("accion", sa.String(length=100), nullable=False),
        sa.Column("entidad", sa.String(length=100), nullable=False),
        sa.Column("entidad_id", sa.Integer(), nullable=True),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("datos_anteriores", sa.JSON(), nullable=True),
        sa.Column("datos_nuevos", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_log_id", "audit_log", ["id"])
    op.create_index("ix_audit_log_entidad", "audit_log", ["entidad"])
    op.create_index("ix_audit_log_usuario_id", "audit_log", ["usuario_id"])

    # ── Audit log: INSERT-ONLY trigger ────────────────────────────────────────
    op.execute("""
    CREATE OR REPLACE FUNCTION audit_log_prevent_update_delete()
    RETURNS TRIGGER AS $$
    BEGIN
        RAISE EXCEPTION 'audit_log is insert-only — updates and deletes are forbidden';
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_audit_log_no_update
    BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_prevent_update_delete();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_no_update ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS audit_log_prevent_update_delete")

    op.drop_table("audit_log")
    op.drop_table("distribuciones")
    op.drop_table("pagos")
    op.drop_table("invitaciones")
    op.drop_table("periodos")
    op.drop_table("socios")
    op.drop_table("natilleras")
    op.drop_table("password_reset_tokens")
    op.drop_table("intentos_login")
    op.drop_table("refresh_tokens")
    op.drop_table("usuarios")

    for enum_name in [
        "tipodistribucion", "estadopago", "metodopago",
        "estadoperiodo", "estadosocio", "estadonatillera", "periodicidad",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
