# Arquitectura de Capas — Backend (FastAPI)

**Aplica a**: `backend/`  
**Última actualización**: Junio 2026

---

## El problema que resuelve

Sin una separación clara de capas, la lógica de negocio termina dispersa entre endpoints, modelos y servicios. En una app financiera esto es crítico: una regla mal ubicada puede ejecutarse dos veces, o no ejecutarse, comprometiendo la integridad del fondo.

---

## Capas definidas

```
┌─────────────────────────────────────────────────────┐
│  API Layer        backend/app/api/                  │
│  Solo HTTP: recibir request, validar con schema,    │
│  llamar servicio, devolver response.                │
│  NO contiene lógica de negocio.                     │
├─────────────────────────────────────────────────────┤
│  Service Layer    backend/app/services/             │
│  Lógica de negocio pura. Orquesta repositorios.    │
│  NO conoce HTTP ni SQLAlchemy directamente.         │
│  NO importa Request, Response, Session.             │
├─────────────────────────────────────────────────────┤
│  Repository Layer backend/app/repositories/         │
│  TODO el acceso a base de datos aquí.               │
│  Métodos: get_by_id, list_by_natillera,             │
│  create, update. Sin lógica de negocio.             │
├─────────────────────────────────────────────────────┤
│  Model Layer      backend/app/models/               │
│  Solo definición de tablas SQLAlchemy.              │
│  Sin métodos de negocio.                            │
└─────────────────────────────────────────────────────┘
```

---

## Estructura de archivos

```
backend/app/
├── api/
│   └── v1/
│       └── endpoints/
│           ├── auth.py
│           ├── natilleras.py
│           ├── pagos.py
│           └── socios.py
├── services/
│   ├── natillera_service.py
│   ├── pago_service.py
│   ├── socio_service.py
│   └── distribucion_service.py
├── repositories/           ← esta capa falta en el scaffold inicial
│   ├── natillera_repo.py
│   ├── pago_repo.py
│   └── socio_repo.py
├── models/
│   ├── natillera.py
│   ├── pago.py
│   └── socio.py
├── schemas/
│   ├── natillera.py
│   ├── pago.py
│   └── socio.py
└── core/
    ├── config.py
    ├── security.py
    └── exceptions.py       ← excepciones de dominio aquí
```

---

## Regla de dependencias

Las dependencias solo van hacia abajo. Nunca hacia arriba.

```
api → service → repository → model
```

- `api` puede importar `service` y `schema`. Nunca `repository` directamente.
- `service` puede importar `repository` y `model`. Nunca `Request` de FastAPI.
- `repository` puede importar `model` y `Session`. Nunca `service`.

---

## Ejemplo concreto: confirmar un pago

### MAL — lógica de negocio en el endpoint

```python
# api/v1/endpoints/pagos.py  ← MAL
@router.put("/{pago_id}/confirmar")
def confirmar_pago(pago_id: int, db: Session = Depends(get_db)):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if pago.estado == "confirmado":
        raise HTTPException(400, "Ya está confirmado")
    pago.estado = "confirmado"
    # actualizar saldo del fondo...
    natillera = db.query(Natillera).filter(...).first()
    natillera.saldo += pago.monto
    db.commit()
    return pago
```

**Problemas**: lógica de negocio en la capa HTTP, acceso directo a BD desde el endpoint, imposible testear sin levantar FastAPI.

---

### BIEN — cada capa en su lugar

```python
# api/v1/endpoints/pagos.py  ← solo HTTP
@router.put("/{pago_id}/confirmar")
def confirmar_pago(
    pago_id: int,
    admin: Usuario = Depends(get_current_admin),
    service: PagoService = Depends(get_pago_service),
):
    resultado = service.confirmar_pago(pago_id, admin.id)
    return PagoResponse.model_validate(resultado)
```

```python
# services/pago_service.py  ← lógica de negocio
class PagoService:
    def __init__(self, pago_repo: PagoRepository, natillera_repo: NatilleraRepository):
        self.pago_repo = pago_repo
        self.natillera_repo = natillera_repo

    def confirmar_pago(self, pago_id: int, admin_id: int) -> Pago:
        pago = self.pago_repo.get_by_id(pago_id)

        if pago is None:
            raise PagoNoEncontradoError(pago_id)
        if pago.estado == EstadoPago.CONFIRMADO:
            raise PagoYaConfirmadoError(pago_id)
        if pago.natillera.admin_id != admin_id:
            raise AccesoNoAutorizadoError()

        pago.estado = EstadoPago.CONFIRMADO
        self.natillera_repo.actualizar_saldo(pago.natillera_id, pago.monto)
        # el commit se hace en la capa de UoW, no aquí
        return pago
```

```python
# repositories/pago_repo.py  ← solo acceso a BD
class PagoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, pago_id: int) -> Pago | None:
        return self.db.query(Pago).filter(Pago.id == pago_id).first()
```

---

## Excepciones de dominio

Las excepciones de negocio se definen en `core/exceptions.py` y se convierten a HTTP en un handler global. Los servicios lanzan excepciones de dominio, nunca `HTTPException`.

```python
# core/exceptions.py
class NatilleraAppError(Exception):
    """Base de todas las excepciones del dominio."""
    pass

class PagoNoEncontradoError(NatilleraAppError):
    def __init__(self, pago_id: int):
        self.pago_id = pago_id

class PagoYaConfirmadoError(NatilleraAppError):
    pass

class SocioEnMoraError(NatilleraAppError):
    pass

class FondosInsuficientesError(NatilleraAppError):
    pass
```

```python
# main.py — handler global
@app.exception_handler(PagoNoEncontradoError)
def handle_pago_no_encontrado(request, exc: PagoNoEncontradoError):
    return JSONResponse(status_code=404, content={"detail": f"Pago {exc.pago_id} no encontrado"})

@app.exception_handler(SocioEnMoraError)
def handle_mora(request, exc):
    return JSONResponse(status_code=409, content={"detail": "El socio tiene pagos en mora"})
```

---

## Dónde viven las reglas de negocio del dominio

Cada regla definida en `CLIENT_BRIEF.md` tiene un hogar exacto:

| Regla | Capa | Archivo |
|-------|------|---------|
| RN-01: Una natillera tiene un solo admin | Service | `natillera_service.py` |
| RN-04: Socio en mora no recibe distribuciones | Service | `distribucion_service.py` |
| RN-06: Pago confirmado no se elimina, solo se revierte | Service | `pago_service.py` |
| RN-07: Distribución final solo si ciclo cerrado | Service | `distribucion_service.py` |
| RN-10: Saldo = aportes confirmados − distribuciones | Repository | `natillera_repo.py` (query) |

---

## Checklist antes de escribir código en el backend

- [ ] ¿Estoy poniendo lógica de negocio en un endpoint? → moverla al service.
- [ ] ¿El service importa `Session` directamente? → crear o usar un repository.
- [ ] ¿El service lanza `HTTPException`? → cambiar a excepción de dominio.
- [ ] ¿La operación modifica más de una tabla? → ¿está en una sola transacción?
- [ ] ¿La regla de negocio está documentada en `CLIENT_BRIEF.md`? → hacer referencia al ID de regla en el comentario del código.
