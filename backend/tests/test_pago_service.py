"""
Tests for PagoService — register, confirm, reject, revert payments.

Covers:
- ISSUE-42: Tests unitarios — servicios de natillera y pagos
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from app.services.pago_service import PagoService
from app.services.natillera_service import NatilleraService
from app.models.usuario import Usuario
from app.models.natillera import EstadoNatillera, Periodicidad
from app.models.socio import EstadoSocio
from app.models.pago import EstadoPago, MetodoPago
from app.repositories.usuario_repo import UsuarioRepository
from app.repositories.natillera_repo import NatilleraRepository, PeriodoRepository
from app.repositories.socio_repo import SocioRepository
from app.repositories.pago_repo import PagoRepository
from app.repositories.audit_repo import AuditRepository
from app.core.exceptions import (
    PagoYaExisteError,
    PagoYaConfirmadoError,
    MontoIncorrectoError,
    AccesoNoAutorizadoError,
    NatilleraNoEncontradaError,
)


def _create_user(db, email):
    from app.core.security import hash_password
    user = Usuario(nombre="User", email=email, password_hash=hash_password("Passw0rd!"))
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def _setup_natillera_activa(db):
    """Create an active natillera with 2 socios and return (admin, socio1, socio2, natillera, periodo)."""
    admin = _create_user(db, "admin@test.com")
    socio1 = _create_user(db, "socio1@test.com")
    socio2 = _create_user(db, "socio2@test.com")

    nat_service = NatilleraService(
        natillera_repo=NatilleraRepository(db),
        periodo_repo=PeriodoRepository(db),
        socio_repo=SocioRepository(db),
        usuario_repo=UsuarioRepository(db),
        audit_repo=AuditRepository(db),
    )

    natillera = nat_service.crear(
        nombre="Test Natillera",
        descripcion=None,
        monto_por_periodo=Decimal("100000"),
        periodicidad=Periodicidad.MENSUAL,
        fecha_inicio=date.today(),
        fecha_fin=date.today() + timedelta(days=90),
        max_socios=10,
        admin_id=admin.id,
    )

    from app.models.socio import Socio
    s1 = Socio(natillera_id=natillera.id, usuario_id=socio1.id, estado=EstadoSocio.ACTIVO)
    s2 = Socio(natillera_id=natillera.id, usuario_id=socio2.id, estado=EstadoSocio.ACTIVO)
    db.add_all([s1, s2])
    db.flush()

    nat_service.activar(natillera.id, admin.id)

    socio_obj1 = db.query(type(s1)).filter_by(usuario_id=socio1.id, natillera_id=natillera.id).first()
    socio_obj2 = db.query(type(s2)).filter_by(usuario_id=socio2.id, natillera_id=natillera.id).first()

    periodo = nat_service.periodo_repo.get_periodo_actual(natillera.id)

    return admin, socio1, socio2, socio_obj1, socio_obj2, natillera, periodo


def _pago_service(db):
    return PagoService(
        pago_repo=PagoRepository(db),
        natillera_repo=NatilleraRepository(db),
        periodo_repo=PeriodoRepository(db),
        socio_repo=SocioRepository(db),
        audit_repo=AuditRepository(db),
    )


@pytest.mark.transaction
class TestRegistrarPagoAdmin:
    """Tests for admin payment registration."""

    def test_registrar_pago_admin_exitoso(self, db):
        """Admin registers a confirmed payment successfully."""
        admin, socio1, socio2, socio_obj1, socio_obj2, natillera, periodo = _setup_natillera_activa(db)
        service = _pago_service(db)

        pago = service.registrar_por_admin(
            natillera_id=natillera.id,
            socio_id=socio_obj1.id,
            periodo_id=periodo.id,
            monto=Decimal("100000"),
            metodo=MetodoPago.EFECTIVO,
            admin_id=admin.id,
        )

        assert pago.estado == EstadoPago.CONFIRMADO
        assert pago.monto == Decimal("100000")

    def test_registrar_pago_duplicado(self, db):
        """Cannot register two active payments for the same socio/period."""
        admin, socio1, socio2, socio_obj1, socio_obj2, natillera, periodo = _setup_natillera_activa(db)
        service = _pago_service(db)

        service.registrar_por_admin(
            natillera_id=natillera.id,
            socio_id=socio_obj1.id,
            periodo_id=periodo.id,
            monto=Decimal("100000"),
            metodo=MetodoPago.EFECTIVO,
            admin_id=admin.id,
        )

        with pytest.raises(PagoYaExisteError):
            service.registrar_por_admin(
                natillera_id=natillera.id,
                socio_id=socio_obj1.id,
                periodo_id=periodo.id,
                monto=Decimal("100000"),
                metodo=MetodoPago.EFECTIVO,
                admin_id=admin.id,
            )

    def test_registrar_pago_monto_incorrecto(self, db):
        """Payment with wrong amount without forzar raises error."""
        admin, socio1, socio2, socio_obj1, socio_obj2, natillera, periodo = _setup_natillera_activa(db)
        service = _pago_service(db)

        with pytest.raises(MontoIncorrectoError):
            service.registrar_por_admin(
                natillera_id=natillera.id,
                socio_id=socio_obj1.id,
                periodo_id=periodo.id,
                monto=Decimal("50000"),
                metodo=MetodoPago.EFECTIVO,
                admin_id=admin.id,
                forzar=False,
            )

    def test_registrar_pago_monto_incorrecto_forzar(self, db):
        """Payment with wrong amount with forzar=True succeeds."""
        admin, socio1, socio2, socio_obj1, socio_obj2, natillera, periodo = _setup_natillera_activa(db)
        service = _pago_service(db)

        pago = service.registrar_por_admin(
            natillera_id=natillera.id,
            socio_id=socio_obj1.id,
            periodo_id=periodo.id,
            monto=Decimal("50000"),
            metodo=MetodoPago.EFECTIVO,
            admin_id=admin.id,
            forzar=True,
        )

        assert pago.monto == Decimal("50000")


@pytest.mark.transaction
class TestRegistrarPagoSocio:
    """Tests for socio payment self-registration."""

    def test_registrar_pago_socio_pendiente(self, db):
        """Socio registers a payment that starts in PENDIENTE_CONFIRMACION."""
        admin, socio1, socio2, socio_obj1, socio_obj2, natillera, periodo = _setup_natillera_activa(db)
        service = _pago_service(db)

        pago = service.registrar_por_socio(
            natillera_id=natillera.id,
            usuario_id=socio1.id,
            periodo_id=periodo.id,
            metodo=MetodoPago.TRANSFERENCIA,
            referencia="REF-001",
        )

        assert pago.estado == EstadoPago.PENDIENTE_CONFIRMACION
        assert pago.monto == natillera.monto_por_periodo


@pytest.mark.transaction
class TestConfirmarPago:
    """Tests for payment confirmation."""

    def test_confirmar_pago_pendiente(self, db):
        """Admin confirms a pending payment."""
        admin, socio1, socio2, socio_obj1, socio_obj2, natillera, periodo = _setup_natillera_activa(db)
        service = _pago_service(db)

        pago = service.registrar_por_socio(
            natillera_id=natillera.id,
            usuario_id=socio1.id,
            periodo_id=periodo.id,
            metodo=MetodoPago.TRANSFERENCIA,
        )

        confirmado = service.confirmar(pago.id, admin.id)
        assert confirmado.estado == EstadoPago.CONFIRMADO

    def test_confirmar_pago_ya_confirmado(self, db):
        """Cannot confirm an already confirmed payment."""
        admin, socio1, socio2, socio_obj1, socio_obj2, natillera, periodo = _setup_natillera_activa(db)
        service = _pago_service(db)

        pago = service.registrar_por_socio(
            natillera_id=natillera.id,
            usuario_id=socio1.id,
            periodo_id=periodo.id,
            metodo=MetodoPago.TRANSFERENCIA,
        )

        service.confirmar(pago.id, admin.id)

        with pytest.raises(PagoYaConfirmadoError):
            service.confirmar(pago.id, admin.id)


@pytest.mark.transaction
class TestRechazarPago:
    """Tests for payment rejection."""

    def test_rechazar_pago(self, db):
        """Admin rejects a pending payment with reason."""
        admin, socio1, socio2, socio_obj1, socio_obj2, natillera, periodo = _setup_natillera_activa(db)
        service = _pago_service(db)

        pago = service.registrar_por_socio(
            natillera_id=natillera.id,
            usuario_id=socio1.id,
            periodo_id=periodo.id,
            metodo=MetodoPago.TRANSFERENCIA,
        )

        rechazado = service.rechazar(pago.id, admin.id, "No se verificó el comprobante")
        assert rechazado.estado == EstadoPago.RECHAZADO


@pytest.mark.transaction
class TestRevertirPago:
    """Tests for payment reversal (RN-06)."""

    def test_revertir_pago_confirmado(self, db):
        """Admin reverts a confirmed payment, record stays in DB."""
        admin, socio1, socio2, socio_obj1, socio_obj2, natillera, periodo = _setup_natillera_activa(db)
        service = _pago_service(db)

        pago = service.registrar_por_admin(
            natillera_id=natillera.id,
            socio_id=socio_obj1.id,
            periodo_id=periodo.id,
            monto=Decimal("100000"),
            metodo=MetodoPago.EFECTIVO,
            admin_id=admin.id,
        )

        revertido = service.revertir(pago.id, admin.id, "Error en el monto")
        assert revertido.estado == EstadoPago.REVERTIDO
        assert revertido.razon == "Error en el monto"
