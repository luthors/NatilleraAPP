"""
Tests for NatilleraService — create, activate, close, archive.

Covers:
- ISSUE-42: Tests unitarios — servicios de natillera y pagos
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from app.services.natillera_service import NatilleraService
from app.models.usuario import Usuario
from app.models.natillera import EstadoNatillera, Periodicidad
from app.models.socio import EstadoSocio
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.natillera_repo import NatilleraRepository, PeriodoRepository
from app.repositories.socio_repo import SocioRepository
from app.repositories.audit_repo import AuditRepository
from app.core.exceptions import (
    NatilleraNoEncontradaError,
    NatilleraEstadoInvalidoError,
    SociosInsuficientesError,
    AccesoNoAutorizadoError,
)


def _create_admin(db, email="admin@test.com"):
    """Helper to create an admin user."""
    from app.core.security import hash_password
    user = Usuario(
        nombre="Admin",
        email=email,
        password_hash=hash_password("Passw0rd!"),
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def _create_user(db, email="user@test.com"):
    """Helper to create a regular user."""
    from app.core.security import hash_password
    user = Usuario(
        nombre="User",
        email=email,
        password_hash=hash_password("Passw0rd!"),
    )
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def _create_service(db):
    return NatilleraService(
        natillera_repo=NatilleraRepository(db),
        periodo_repo=PeriodoRepository(db),
        socio_repo=SocioRepository(db),
        usuario_repo=UsuarioRepository(db),
        audit_repo=AuditRepository(db),
    )


@pytest.mark.natillera
class TestCrearNatillera:
    """Tests for natillera creation."""

    def test_crear_exitosa(self, db):
        """Creating a natillera sets CONFIGURACION state and adds creator as socio."""
        service = _create_service(db)
        admin = _create_admin(db)

        natillera = service.crear(
            nombre="Mi Natillera",
            descripcion="Una natillera de prueba",
            monto_por_periodo=Decimal("100000"),
            periodicidad=Periodicidad.MENSUAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),
            max_socios=10,
            admin_id=admin.id,
        )

        assert natillera.nombre == "Mi Natillera"
        assert natillera.estado == EstadoNatillera.CONFIGURACION
        assert natillera.admin_id == admin.id

    def test_crear_agrega_admin_como_socio(self, db):
        """The creator is automatically added as the first socio."""
        service = _create_service(db)
        admin = _create_admin(db)

        natillera = service.crear(
            nombre="Test",
            descripcion=None,
            monto_por_periodo=Decimal("50000"),
            periodicidad=Periodicidad.SEMANAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            max_socios=5,
            admin_id=admin.id,
        )

        socio = service.socio_repo.get_by_usuario_y_natillera(admin.id, natillera.id)
        assert socio is not None
        assert socio.estado == EstadoSocio.ACTIVO


@pytest.mark.natillera
class TestActivarNatillera:
    """Tests for natillera activation."""

    def test_activar_con_socios_suficientes(self, db):
        """Activating with 2+ active socios succeeds and generates periods."""
        service = _create_service(db)
        admin = _create_admin(db)
        user2 = _create_user(db, "user2@test.com")

        natillera = service.crear(
            nombre="Test",
            descripcion=None,
            monto_por_periodo=Decimal("100000"),
            periodicidad=Periodicidad.MENSUAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            max_socios=10,
            admin_id=admin.id,
        )

        from app.models.socio import Socio
        socio2 = Socio(
            natillera_id=natillera.id,
            usuario_id=user2.id,
            estado=EstadoSocio.ACTIVO,
        )
        db.add(socio2)
        db.flush()

        result = service.activar(natillera.id, admin.id)
        assert result.estado == EstadoNatillera.ACTIVA

        periodos = service.periodo_repo.get_by_natillera(natillera.id)
        assert len(periodos) > 0

    def test_activar_con_pocos_socios(self, db):
        """Activating with fewer than 2 socios raises SociosInsuficientesError."""
        service = _create_service(db)
        admin = _create_admin(db)

        natillera = service.crear(
            nombre="Test",
            descripcion=None,
            monto_por_periodo=Decimal("100000"),
            periodicidad=Periodicidad.MENSUAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            max_socios=10,
            admin_id=admin.id,
        )

        with pytest.raises(SociosInsuficientesError):
            service.activar(natillera.id, admin.id)

    def test_activar_estado_invalido(self, db):
        """Cannot activate a natillera that is not in CONFIGURACION."""
        service = _create_service(db)
        admin = _create_admin(db)
        user2 = _create_user(db, "user2@test.com")

        natillera = service.crear(
            nombre="Test",
            descripcion=None,
            monto_por_periodo=Decimal("100000"),
            periodicidad=Periodicidad.MENSUAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            max_socios=10,
            admin_id=admin.id,
        )

        from app.models.socio import Socio
        socio2 = Socio(
            natillera_id=natillera.id,
            usuario_id=user2.id,
            estado=EstadoSocio.ACTIVO,
        )
        db.add(socio2)
        db.flush()

        service.activar(natillera.id, admin.id)

        with pytest.raises(NatilleraEstadoInvalidoError):
            service.activar(natillera.id, admin.id)


@pytest.mark.natillera
class TestCerrarNatillera:
    """Tests for natillera closure."""

    def test_cerrar_cambia_estado(self, db):
        """Closing an active natillera moves it to EN_CIERRE."""
        service = _create_service(db)
        admin = _create_admin(db)
        user2 = _create_user(db, "user2@test.com")

        natillera = service.crear(
            nombre="Test",
            descripcion=None,
            monto_por_periodo=Decimal("100000"),
            periodicidad=Periodicidad.MENSUAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            max_socios=10,
            admin_id=admin.id,
        )

        from app.models.socio import Socio
        socio2 = Socio(
            natillera_id=natillera.id,
            usuario_id=user2.id,
            estado=EstadoSocio.ACTIVO,
        )
        db.add(socio2)
        db.flush()

        service.activar(natillera.id, admin.id)
        result = service.cerrar(natillera.id, admin.id, forzar=True)

        assert result["requiere_confirmacion"] is False

    def test_cerrar_estado_invalido(self, db):
        """Cannot close a natillera that is not ACTIVA."""
        service = _create_service(db)
        admin = _create_admin(db)

        natillera = service.crear(
            nombre="Test",
            descripcion=None,
            monto_por_periodo=Decimal("100000"),
            periodicidad=Periodicidad.MENSUAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            max_socios=10,
            admin_id=admin.id,
        )

        with pytest.raises(NatilleraEstadoInvalidoError):
            service.cerrar(natillera.id, admin.id)


@pytest.mark.natillera
class TestArchivarNatillera:
    """Tests for natillera archiving."""

    def test_archivar_requiere_cerrada(self, db):
        """Cannot archive unless natillera is CERRADA."""
        service = _create_service(db)
        admin = _create_admin(db)

        natillera = service.crear(
            nombre="Test",
            descripcion=None,
            monto_por_periodo=Decimal("100000"),
            periodicidad=Periodicidad.MENSUAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            max_socios=10,
            admin_id=admin.id,
        )

        with pytest.raises(NatilleraEstadoInvalidoError):
            service.archivar(natillera.id, admin.id)


@pytest.mark.natillera
class TestObtenerNatillera:
    """Tests for natillera detail access."""

    def test_obtener_admin_accede(self, db):
        """Admin can access their own natillera."""
        service = _create_service(db)
        admin = _create_admin(db)

        natillera = service.crear(
            nombre="Test",
            descripcion=None,
            monto_por_periodo=Decimal("100000"),
            periodicidad=Periodicidad.MENSUAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            max_socios=10,
            admin_id=admin.id,
        )

        result = service.obtener(natillera.id, admin.id)
        assert result.id == natillera.id

    def test_obtener_no_admin_no_socio(self, db):
        """User who is neither admin nor socio gets AccessDenied."""
        service = _create_service(db)
        admin = _create_admin(db)
        outsider = _create_user(db, "outsider@test.com")

        natillera = service.crear(
            nombre="Test",
            descripcion=None,
            monto_por_periodo=Decimal("100000"),
            periodicidad=Periodicidad.MENSUAL,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=90),
            max_socios=10,
            admin_id=admin.id,
        )

        with pytest.raises(AccesoNoAutorizadoError):
            service.obtener(natillera.id, outsider.id)
