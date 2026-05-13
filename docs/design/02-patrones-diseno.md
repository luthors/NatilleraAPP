# Patrones de Diseño — Natillera App

**Aplica a**: `backend/` principalmente, con notas para `frontend/` y `mobile/`  
**Última actualización**: Junio 2026

---

## Patrones implementados

### 1. Repository Pattern

**Problema que resuelve**: los servicios no deben conocer cómo se almacenan los datos. Si mañana se cambia SQLAlchemy por otro ORM, solo se toca el repositorio.

**Estructura:**

```python
# repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, id: int) -> T | None: ...

    @abstractmethod
    def list_all(self) -> list[T]: ...

    @abstractmethod
    def save(self, entity: T) -> T: ...
```

```python
# repositories/natillera_repo.py
class NatilleraRepository(BaseRepository[Natillera]):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Natillera | None:
        return self.db.get(Natillera, id)

    def get_by_admin(self, admin_id: int) -> list[Natillera]:
        return (
            self.db.query(Natillera)
            .filter(Natillera.admin_id == admin_id)
            .order_by(Natillera.created_at.desc())
            .all()
        )

    def list_all(self) -> list[Natillera]:
        return self.db.query(Natillera).all()

    def save(self, natillera: Natillera) -> Natillera:
        self.db.add(natillera)
        self.db.flush()  # obtener ID sin hacer commit
        return natillera
```

**Beneficio clave**: el `NatilleraService` puede testearse con un `FakeNatilleraRepository` en memoria, sin necesidad de BD real.

---

### 2. Unit of Work (UoW)

**Problema que resuelve**: una operación de negocio puede tocar múltiples tablas. Si falla a mitad, la BD queda inconsistente. En una natillera: confirmar un pago actualiza `pagos` Y `natilleras.saldo`. Ambos deben ser atómicos.

**Implementación con FastAPI y SQLAlchemy:**

```python
# core/database.py
from contextlib import contextmanager
from sqlalchemy.orm import Session

def get_db():
    """Una sesión = una transacción = un request HTTP."""
    db = SessionLocal()
    try:
        yield db
        db.commit()       # commit al final si todo fue bien
    except Exception:
        db.rollback()     # rollback si algo falló
        raise
    finally:
        db.close()
```

```python
# dependencies.py
def get_pago_service(db: Session = Depends(get_db)) -> PagoService:
    return PagoService(
        pago_repo=PagoRepository(db),
        natillera_repo=NatilleraRepository(db),
        audit_repo=AuditRepository(db),
    )
```

**Regla**: el `commit()` y `rollback()` ocurren en `get_db()`, nunca dentro de un service ni repository. Los servicios solo operan sobre objetos; la sesión se encarga del estado.

**Ejemplo de operación atómica:**

```python
# services/pago_service.py
def confirmar_pago(self, pago_id: int, admin_id: int) -> Pago:
    pago = self.pago_repo.get_by_id(pago_id)      # SELECT
    pago.estado = EstadoPago.CONFIRMADO             # UPDATE pago
    self.natillera_repo.sumar_al_saldo(            # UPDATE natillera
        pago.natillera_id, pago.monto
    )
    self.audit_repo.registrar(                     # INSERT audit log
        accion="CONFIRMAR_PAGO",
        entidad_id=pago_id,
        usuario_id=admin_id,
    )
    # El commit ocurre en get_db() al terminar el request.
    # Si cualquier línea falla, get_db() hace rollback de todo.
    return pago
```

---

### 3. Dependency Injection (DI) nativa de FastAPI

**Problema que resuelve**: evitar instanciar manualmente servicios y repositorios en cada endpoint; facilitar el reemplazo de dependencias en tests.

```python
# dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session

def get_natillera_service(db: Session = Depends(get_db)) -> NatilleraService:
    return NatilleraService(
        natillera_repo=NatilleraRepository(db),
        socio_repo=SocioRepository(db),
    )

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    return auth_service.decode_token(token, db)

def get_current_admin(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    if not current_user.es_admin_de_alguna_natillera:
        raise HTTPException(403)
    return current_user
```

```python
# api/v1/endpoints/natilleras.py
@router.post("/", response_model=NatilleraResponse)
def crear_natillera(
    data: NatilleraCreate,
    admin: Usuario = Depends(get_current_user),
    service: NatilleraService = Depends(get_natillera_service),
):
    return service.crear(data, admin)
```

**Para tests:**

```python
# tests/test_natillera_service.py
def test_crear_natillera():
    fake_repo = FakeNatilleraRepository()  # en memoria
    service = NatilleraService(natillera_repo=fake_repo, ...)
    result = service.crear(NatilleraCreate(...), admin_mock)
    assert result.estado == EstadoNatillera.CONFIGURACION
```

---

### 4. Strategy Pattern — métodos de pago

**Problema que resuelve**: agregar métodos de pago (Stripe, PSE, efectivo) sin modificar el código existente. Aplica el principio Open/Closed.

```python
# services/pagos/estrategias.py
from abc import ABC, abstractmethod

class EstrategiaPago(ABC):
    @abstractmethod
    def procesar(self, monto: int, metadata: dict) -> ResultadoPago: ...

class PagoEfectivo(EstrategiaPago):
    def procesar(self, monto: int, metadata: dict) -> ResultadoPago:
        # sin integración externa, registro manual
        return ResultadoPago(referencia=metadata.get("referencia"), estado="pendiente_confirmacion")

class PagoStripe(EstrategiaPago):
    def procesar(self, monto: int, metadata: dict) -> ResultadoPago:
        intent = stripe.PaymentIntent.create(amount=monto, currency="cop")
        return ResultadoPago(referencia=intent.id, estado="pendiente_stripe")

class PagoPSE(EstrategiaPago):
    def procesar(self, monto: int, metadata: dict) -> ResultadoPago:
        # integración PSE...
        pass
```

```python
# services/pago_service.py
ESTRATEGIAS = {
    "efectivo": PagoEfectivo(),
    "stripe": PagoStripe(),
    "pse": PagoPSE(),
}

def registrar_pago(self, socio_id: int, natillera_id: int, metodo: str, monto: int):
    estrategia = ESTRATEGIAS.get(metodo)
    if estrategia is None:
        raise MetodoPagoNoSoportadoError(metodo)
    resultado = estrategia.procesar(monto, {})
    # guardar pago con el resultado...
```

Agregar un nuevo método de pago = crear una nueva clase `EstrategiaPago` + registrarla en `ESTRATEGIAS`. Cero cambios en el service.

---

### 5. Observer Pattern — notificaciones

**Problema que resuelve**: el servicio de pagos no debería conocer nada sobre emails, push notifications o SMS. Cuando un pago se confirma, múltiples acciones deben ocurrir de forma desacoplada.

```python
# core/events.py
from typing import Callable

_handlers: dict[str, list[Callable]] = {}

def on(evento: str):
    def decorator(fn: Callable):
        _handlers.setdefault(evento, []).append(fn)
        return fn
    return decorator

def emit(evento: str, **kwargs):
    for handler in _handlers.get(evento, []):
        handler(**kwargs)
```

```python
# services/notificaciones.py
from core.events import on

@on("pago.confirmado")
def enviar_email_confirmacion(pago, socio, **kwargs):
    email_service.enviar(socio.email, "Pago confirmado", ...)

@on("pago.confirmado")
def enviar_push_notification(pago, socio, **kwargs):
    push_service.enviar(socio.device_token, ...)

@on("pago.confirmado")
def registrar_en_audit_log(pago, admin_id, **kwargs):
    audit_service.registrar("PAGO_CONFIRMADO", pago.id, admin_id)
```

```python
# services/pago_service.py
from core.events import emit

def confirmar_pago(self, pago_id, admin_id):
    pago = self.pago_repo.get_by_id(pago_id)
    pago.estado = EstadoPago.CONFIRMADO
    emit("pago.confirmado", pago=pago, socio=pago.socio, admin_id=admin_id)
    return pago
```

El `PagoService` no sabe nada de emails ni push. Agregar una nueva acción al confirmar un pago = un nuevo `@on("pago.confirmado")`.

---

## Resumen: ¿qué patrón para qué problema?

| Problema | Patrón |
|----------|--------|
| Aislar acceso a BD | Repository |
| Operaciones financieras atómicas | Unit of Work |
| Testear servicios sin BD real | Repository + DI |
| Múltiples métodos de pago | Strategy |
| Acciones post-evento desacopladas | Observer / Events |
| Crear objetos complejos (natillera + socios + calendario) | Factory / Builder |
