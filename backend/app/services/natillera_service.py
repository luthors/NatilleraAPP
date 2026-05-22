"""
NatilleraService — create, activate, close, archive natilleras.

References:
- HU-02-01: crear
- HU-02-02 to 02-04: listar y ver detalle
- HU-02-05: editar (solo nombre/descripción)
- HU-02-06: activar (genera calendario)
- HU-02-07: cerrar
- HU-02-08: archivar
- RN-01, RN-02, RN-03, RN-07, RN-12
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from app.core.events import emit
from app.core.exceptions import (
    NatilleraNoEncontradaError,
    NatilleraEstadoInvalidoError,
    CambioParametrosFinancierosError,
    SociosInsuficientesError,
    AccesoNoAutorizadoError,
    DistribucionNoPermitidaError,
)
from app.models.natillera import Natillera, EstadoNatillera, Periodicidad
from app.models.socio import Periodo, EstadoPeriodo, Socio, EstadoSocio
from app.repositories.natillera_repo import NatilleraRepository, PeriodoRepository
from app.repositories.socio_repo import SocioRepository
from app.repositories.audit_repo import AuditRepository


class NatilleraService:

    def __init__(
        self,
        natillera_repo: NatilleraRepository,
        periodo_repo: PeriodoRepository,
        socio_repo: SocioRepository,
        audit_repo: AuditRepository,
    ) -> None:
        self.natillera_repo = natillera_repo
        self.periodo_repo = periodo_repo
        self.socio_repo = socio_repo
        self.audit_repo = audit_repo

    # ── Crear ─────────────────────────────────────────────────────────────────

    def crear(
        self,
        nombre: str,
        descripcion: Optional[str],
        monto_por_periodo: Decimal,
        periodicidad: Periodicidad,
        fecha_inicio: date,
        fecha_fin: date,
        max_socios: int,
        admin_id: int,
    ) -> Natillera:
        """
        Create a natillera in CONFIGURACION state.
        The creator is automatically added as the admin-socio.
        """
        natillera = Natillera(
            nombre=nombre,
            descripcion=descripcion,
            admin_id=admin_id,
            monto_por_periodo=monto_por_periodo,
            periodicidad=periodicidad,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            max_socios=max_socios,
            estado=EstadoNatillera.CONFIGURACION,
        )
        self.natillera_repo.save(natillera)

        # Add creator as first socio
        socio = Socio(
            natillera_id=natillera.id,
            usuario_id=admin_id,
            estado=EstadoSocio.ACTIVO,
        )
        self.socio_repo.save(socio)

        self.audit_repo.registrar(
            accion="CREAR_NATILLERA",
            entidad="Natillera",
            entidad_id=natillera.id,
            usuario_id=admin_id,
            datos_nuevos={"nombre": natillera.nombre, "estado": natillera.estado},
        )

        emit("natillera.creada", natillera=natillera)
        return natillera

    # ── Listar ────────────────────────────────────────────────────────────────

    def listar_por_usuario(self, usuario_id: int, incluir_archivadas: bool = False) -> list[Natillera]:
        return self.natillera_repo.get_by_usuario(usuario_id, incluir_archivadas)

    # ── Detalle ───────────────────────────────────────────────────────────────

    def obtener(self, natillera_id: int, solicitante_id: int) -> Natillera:
        """Return the natillera if the requester is admin or active socio."""
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(natillera_id)

        socio = self.socio_repo.get_by_usuario_y_natillera(solicitante_id, natillera_id)
        es_admin = natillera.admin_id == solicitante_id
        if not es_admin and (socio is None or not socio.esta_activo()):
            raise AccesoNoAutorizadoError()

        return natillera

    # ── Editar ────────────────────────────────────────────────────────────────

    def editar(
        self,
        natillera_id: int,
        admin_id: int,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
    ) -> Natillera:
        """
        Update name and description only (RN-02, RN-03).
        Financial parameters are immutable once ACTIVA.
        """
        natillera = self._get_admin_natillera(natillera_id, admin_id)
        updates = {}
        if nombre is not None:
            updates["nombre"] = nombre
        if descripcion is not None:
            updates["descripcion"] = descripcion
        return self.natillera_repo.update(natillera, **updates)

    # ── Activar ───────────────────────────────────────────────────────────────

    def activar(self, natillera_id: int, admin_id: int) -> Natillera:
        """
        Activate a natillera and generate its period calendar.

        Requires at least 2 active socios (RN-12).
        Changes state from CONFIGURACION → ACTIVA.
        """
        natillera = self._get_admin_natillera(natillera_id, admin_id)

        if natillera.estado != EstadoNatillera.CONFIGURACION:
            raise NatilleraEstadoInvalidoError("activar", natillera.estado)

        socios_activos = self.socio_repo.count_activos(natillera_id)
        if socios_activos < 2:
            raise SociosInsuficientesError(2)

        # Generate period calendar
        self._generar_calendario(natillera)

        self.natillera_repo.update_estado(natillera, EstadoNatillera.ACTIVA)
        self.audit_repo.registrar(
            accion="ACTIVAR_NATILLERA",
            entidad="Natillera",
            entidad_id=natillera.id,
            usuario_id=admin_id,
            datos_anteriores={"estado": EstadoNatillera.CONFIGURACION},
            datos_nuevos={"estado": EstadoNatillera.ACTIVA},
        )
        emit("natillera.activada", natillera=natillera)
        return natillera

    def _generar_calendario(self, natillera: Natillera) -> list[Periodo]:
        """
        Create Periodo records from fecha_inicio to fecha_fin
        based on the natillera's periodicidad.
        """
        delta_map = {
            Periodicidad.SEMANAL:   timedelta(weeks=1),
            Periodicidad.QUINCENAL: timedelta(days=15),
            Periodicidad.MENSUAL:   timedelta(days=30),  # approximate
        }
        delta = delta_map[natillera.periodicidad]

        periodos: list[Periodo] = []
        numero = 1
        inicio = natillera.fecha_inicio

        while inicio <= natillera.fecha_fin:
            fin = inicio + delta - timedelta(days=1)
            if fin > natillera.fecha_fin:
                fin = natillera.fecha_fin

            estado = EstadoPeriodo.ABIERTO if numero == 1 else EstadoPeriodo.PENDIENTE
            periodo = Periodo(
                natillera_id=natillera.id,
                numero=numero,
                fecha_inicio=inicio,
                fecha_fin=fin,
                estado=estado,
            )
            self.periodo_repo.save(periodo)
            periodos.append(periodo)

            inicio = fin + timedelta(days=1)
            numero += 1

            if inicio > natillera.fecha_fin:
                break

        return periodos

    # ── Cerrar ────────────────────────────────────────────────────────────────

    def cerrar(self, natillera_id: int, admin_id: int, forzar: bool = False) -> dict:
        """
        Move natillera to EN_CIERRE state.

        If there are socios in mora and forzar=False, returns a warning dict
        instead of closing, so the frontend can display the list and ask for
        explicit confirmation.
        """
        natillera = self._get_admin_natillera(natillera_id, admin_id)

        if natillera.estado != EstadoNatillera.ACTIVA:
            raise NatilleraEstadoInvalidoError("cerrar", natillera.estado)

        socios_en_mora = self._socios_con_mora(natillera_id)

        if socios_en_mora and not forzar:
            return {
                "requiere_confirmacion": True,
                "mensaje": "Hay socios en mora. Envía forzar=true para confirmar el cierre.",
                "socios_en_mora": [s.usuario_id for s in socios_en_mora],
            }

        self.natillera_repo.update_estado(natillera, EstadoNatillera.EN_CIERRE)
        self.audit_repo.registrar(
            accion="CERRAR_NATILLERA",
            entidad="Natillera",
            entidad_id=natillera.id,
            usuario_id=admin_id,
            datos_anteriores={"estado": EstadoNatillera.ACTIVA},
            datos_nuevos={"estado": EstadoNatillera.EN_CIERRE},
        )
        emit("natillera.cerrada", natillera=natillera)
        return {"requiere_confirmacion": False, "natillera": natillera}

    # ── Archivar ──────────────────────────────────────────────────────────────

    def archivar(self, natillera_id: int, admin_id: int) -> Natillera:
        natillera = self._get_admin_natillera(natillera_id, admin_id)
        if natillera.estado != EstadoNatillera.CERRADA:
            raise NatilleraEstadoInvalidoError("archivar", natillera.estado)
        return self.natillera_repo.update_estado(natillera, EstadoNatillera.ARCHIVADA)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_admin_natillera(self, natillera_id: int, admin_id: int) -> Natillera:
        natillera = self.natillera_repo.get_by_id(natillera_id)
        if natillera is None:
            raise NatilleraNoEncontradaError(natillera_id)
        if natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError("Solo el administrador puede realizar esta acción")
        return natillera

    def _socios_con_mora(self, natillera_id: int) -> list[Socio]:
        socios = self.socio_repo.get_by_natillera(natillera_id, solo_activos=True)
        return [s for s in socios if self.socio_repo.tiene_mora(s.id, natillera_id)]
