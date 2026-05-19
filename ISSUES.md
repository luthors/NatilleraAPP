# ISSUES.md — Natillera App

## Convenciones

**Complejidad**: `0.5` trivial · `1.0` simple · `2.0` media · `3.0` compleja  
**Prioridad**: `P0` crítica · `P1` alta · `P2` media · `P3` baja  
**Fase**: MVP · Fase 2 · Fase 3 · Fase 4  
**Referencia HU**: cada issue indica la Historia de Usuario de `CLIENT_BRIEF.md` que implementa.

---

## Tabla de Contenido

- [INFRAESTRUCTURA — Setup y Base](#infraestructura--setup-y-base)
- [E-01 — Autenticación y Perfil](#e-01--autenticación-y-perfil)
- [E-02 — Gestión de Natilleras](#e-02--gestión-de-natilleras)
- [E-03 — Gestión de Socios](#e-03--gestión-de-socios)
- [E-04 — Aportes y Pagos](#e-04--aportes-y-pagos)
- [E-05 — Saldos y Estado de Cuenta](#e-05--saldos-y-estado-de-cuenta)
- [E-06 — Distribuciones](#e-06--distribuciones)
- [E-07 — Notificaciones y Alertas](#e-07--notificaciones-y-alertas)
- [E-08 — Reportes y Comprobantes](#e-08--reportes-y-comprobantes)
- [E-09 — Seguridad y Auditoría](#e-09--seguridad-y-auditoría)
- [FRONTEND — Setup y UI](#frontend--setup-y-ui)
- [MOBILE — Setup y Pantallas](#mobile--setup-y-pantallas)
- [TESTING](#testing)
- [CI/CD y DevOps](#cicd-y-devops)
- [Resumen y Roadmap](#resumen-y-roadmap)

---

## INFRAESTRUCTURA — Setup y Base

---

### ISSUE-01: Setup inicial FastAPI con estructura de capas

**Complejidad**: 1.0 | **Prioridad**: P0 | **Fase**: MVP  
**Labels**: `backend` `setup` `architecture`

**Descripción**:
Configurar el proyecto backend con la arquitectura de capas definida en `docs/design/01-arquitectura-capas.md`. Esto incluye la estructura de carpetas completa con la capa `repositories/` (ausente en el scaffold inicial).

**Tareas**:
- [ ] Crear `app/main.py` con FastAPI, CORS (`localhost:5173`, `localhost:3000`) y lifespan
- [ ] Crear estructura de carpetas: `api/v1/endpoints/`, `services/`, `repositories/`, `models/`, `schemas/`, `core/`
- [ ] Crear `core/config.py` con `pydantic-settings` (leer `.env`)
- [ ] Crear `core/exceptions.py` con excepciones de dominio base (`NatilleraAppError` y subclases)
- [ ] Crear `core/database.py` con `SessionLocal`, `get_db()` con commit/rollback automático (Unit of Work)
- [ ] Registrar handler global de excepciones de dominio → HTTP en `main.py`
- [ ] Crear `.env.example` con todas las variables requeridas
- [ ] Verificar: `uvicorn app.main:app --reload` sin errores, `GET /docs` muestra Swagger

**Criterios de aceptación**:
- `uvicorn app.main:app --reload` arranca sin errores
- `GET /docs` muestra Swagger UI con CORS activo
- Un error de dominio retorna el código HTTP correcto sin `HTTPException` en servicios
- `get_db()` hace rollback automático si ocurre una excepción durante el request

---

### ISSUE-02: Modelos de base de datos y migraciones Alembic

**Complejidad**: 2.0 | **Prioridad**: P0 | **Fase**: MVP  
**Labels**: `backend` `database` `models`  
**Depende de**: ISSUE-01

**Descripción**:
Crear todos los modelos SQLAlchemy y la primera migración Alembic. Los modelos deben reflejar el dominio definido en `CLIENT_BRIEF.md` incluyendo las reglas de negocio en los constraints de BD.

**Tareas**:
- [ ] `models/usuario.py`: `id`, `email` (UNIQUE), `password_hash`, `nombre`, `telefono`, `foto_url`, `is_active`, `created_at`, `updated_at`
- [ ] `models/natillera.py`: `id`, `nombre`, `descripcion`, `admin_id` (FK), `monto_por_periodo` (`Numeric(12,2)`), `periodicidad` (ENUM: semanal/quincenal/mensual), `fecha_inicio`, `fecha_fin`, `max_socios`, `estado` (ENUM: CONFIGURACION/ACTIVA/EN_CIERRE/CERRADA/ARCHIVADA), `created_at`
- [ ] `models/socio.py` (tabla `natillera_socios`): `id`, `natillera_id` (FK), `usuario_id` (FK), `estado` (ENUM: ACTIVO/SUSPENDIDO/RETIRADO), `joined_at`, `removed_at`; UNIQUE(`natillera_id`, `usuario_id`)
- [ ] `models/periodo.py`: `id`, `natillera_id` (FK), `numero`, `fecha_inicio`, `fecha_fin`, `estado` (ENUM: PENDIENTE/ABIERTO/CERRADO)
- [ ] `models/pago.py`: `id`, `natillera_id` (FK), `socio_id` (FK), `periodo_id` (FK), `monto` (`Numeric(12,2)`), `metodo` (ENUM: efectivo/transferencia/stripe/pse), `estado` (ENUM: PENDIENTE_CONFIRMACION/CONFIRMADO/RECHAZADO/REVERTIDO), `referencia`, `comprobante_url`, `confirmado_por` (FK usuario), `confirmado_at`, `created_at`
- [ ] `models/distribucion.py`: `id`, `natillera_id` (FK), `socio_id` (FK), `monto` (`Numeric(12,2)`), `tipo` (ENUM: PARCIAL/FINAL), `fecha`, `created_at`
- [ ] `models/audit_log.py`: `id`, `accion`, `entidad`, `entidad_id`, `usuario_id` (FK), `datos_anteriores` (JSON), `datos_nuevos` (JSON), `ip`, `created_at` — **sin UPDATE ni DELETE**
- [ ] Crear índices: `natillera_id`, `usuario_id`, `estado`, `created_at` en tablas de alto volumen
- [ ] Inicializar Alembic: `alembic init migrations`, configurar `env.py` con autogenerate
- [ ] Primera migración: `alembic revision --autogenerate -m "init_schema"`
- [ ] Verificar: `alembic upgrade head` y `alembic downgrade -1`

**Criterios de aceptación**:
- `alembic upgrade head` crea todas las tablas sin errores
- `alembic downgrade -1` revierte correctamente
- `monto_por_periodo` usa `Numeric`, no `Float` (RNF: precisión financiera)
- `audit_log` no tiene endpoint de DELETE ni UPDATE en ninguna capa

---

### ISSUE-03: Capa Repository — implementación base

**Complejidad**: 1.5 | **Prioridad**: P0 | **Fase**: MVP  
**Labels**: `backend` `architecture` `repository-pattern`  
**Depende de**: ISSUE-02

**Descripción**:
Implementar la capa `repositories/` según el patrón definido en `docs/design/02-patrones-diseno.md`. Sin esta capa los servicios dependerían directamente de SQLAlchemy, haciéndolos intestables.

**Tareas**:
- [ ] `repositories/base.py`: clase abstracta `BaseRepository[T]` con `get_by_id`, `list_all`, `save`, `delete`
- [ ] `repositories/usuario_repo.py`: `get_by_id`, `get_by_email`, `save`, `update`
- [ ] `repositories/natillera_repo.py`: `get_by_id`, `get_by_admin`, `get_by_socio`, `save`, `update`, `actualizar_saldo`
- [ ] `repositories/socio_repo.py`: `get_by_natillera`, `get_by_usuario_y_natillera`, `save`, `update_estado`
- [ ] `repositories/pago_repo.py`: `get_by_id`, `get_by_natillera`, `get_by_socio`, `get_pendientes_confirmacion`, `save`, `update`
- [ ] `repositories/periodo_repo.py`: `get_by_natillera`, `get_periodo_actual`, `save`, `crear_calendario`
- [ ] `repositories/audit_repo.py`: `registrar` (solo INSERT, sin update ni delete)
- [ ] Registrar todos los repositorios como dependencias en `dependencies.py`
- [ ] Test unitario de un repositorio usando SQLite en memoria

**Criterios de aceptación**:
- Los servicios no importan `Session` directamente
- Un `FakeNatilleraRepository` puede reemplazar al real en tests sin cambiar el servicio
- Todos los métodos tienen type hints completos

---

## E-01 — Autenticación y Perfil

---

### ISSUE-04: Registro de usuario

**Complejidad**: 1.0 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-01-01  
**Labels**: `backend` `auth` `security`  
**Depende de**: ISSUE-03

**Descripción**:
Implementar el endpoint de registro con validaciones de contraseña, hash bcrypt y envío de email de verificación.

**Tareas**:
- [ ] `schemas/usuario.py`: `UsuarioCreate` (nombre, email, password), `UsuarioResponse` (sin password)
- [ ] `core/security.py`: `hash_password()` con bcrypt cost=12, `verify_password()`, `create_access_token()`, `create_refresh_token()`, `decode_token()`
- [ ] `services/auth_service.py`: `registrar_usuario()` — valida email único, hashea password, crea usuario, emite `usuario.registrado`
- [ ] `api/v1/endpoints/auth.py`: `POST /auth/register` → llama service, retorna tokens
- [ ] Validación de password: mín. 8 chars, 1 mayúscula, 1 número (via Pydantic validator)
- [ ] Email de verificación: por ahora log en consola, estructura lista para SMTP
- [ ] `models/refresh_token.py`: guardar refresh tokens en BD para poder invalidarlos

**Criterios de aceptación** (de HU-01-01):
- Email duplicado retorna 409 con `"Este correo ya está registrado"`
- Password débil retorna 422 con descripción del requisito incumplido
- Registro exitoso retorna `access_token` (15 min) y `refresh_token` (7 días)
- Password nunca aparece en ninguna respuesta ni log

---

### ISSUE-05: Login, refresh token y logout

**Complejidad**: 1.5 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-01-02, HU-01-03  
**Labels**: `backend` `auth` `security`  
**Depende de**: ISSUE-04

**Descripción**:
Implementar login con bloqueo por intentos fallidos, refresh de token y logout con invalidación del refresh token.

**Tareas**:
- [ ] `POST /auth/login`: validar credenciales, retornar tokens; error genérico "Credenciales incorrectas" (no especificar cuál campo falló — RNF-06)
- [ ] Bloqueo de cuenta: tras 5 intentos fallidos → bloquear 15 min, notificar por email
- [ ] `models/intento_login.py`: tabla para rastrear intentos por email
- [ ] `POST /auth/refresh`: recibir refresh token, validar en BD, retornar nuevo access token (rotación de refresh token)
- [ ] `POST /auth/logout`: invalidar refresh token en BD, limpiar sesión
- [ ] Dependencia `get_current_user()` en `dependencies.py`
- [ ] Dependencia `get_current_admin_natillera(natillera_id)` para verificar que el usuario es admin de la natillera específica

**Criterios de aceptación** (de HU-01-02, HU-01-03):
- Error de login no especifica si falló email o password
- 5 intentos fallidos bloquean la cuenta 15 min
- Logout invalida el refresh token (re-uso del mismo token devuelve 401)
- Endpoint protegido sin token devuelve 401

---

### ISSUE-06: Recuperación de contraseña

**Complejidad**: 1.0 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-01-04  
**Labels**: `backend` `auth`  
**Depende de**: ISSUE-05

**Descripción**:
Flujo de recuperación de contraseña por email con token de un solo uso.

**Tareas**:
- [ ] `models/password_reset_token.py`: `token` (UUID), `usuario_id`, `expira_at`, `usado` (bool)
- [ ] `POST /auth/recuperar-password`: recibir email, crear token válido 1 hora, enviar email con link
- [ ] `POST /auth/reset-password`: recibir token + nueva password, validar token vigente y no usado, actualizar password, invalidar todos los refresh tokens del usuario
- [ ] Si email no existe: responder igual que si existe (no revelar si el email está registrado)

**Criterios de aceptación** (de HU-01-04):
- Token expirado devuelve error `"Enlace expirado, solicita uno nuevo"`
- Token usado una vez no puede reutilizarse
- Al restablecer, todos los tokens activos de la cuenta se invalidan
- La respuesta es idéntica independientemente de si el email existe o no

---

### ISSUE-07: Editar perfil de usuario

**Complejidad**: 0.5 | **Prioridad**: P2 | **Fase**: MVP  
**HU**: HU-01-05  
**Labels**: `backend` `users`  
**Depende de**: ISSUE-05

**Descripción**:
Endpoints para consultar y actualizar el perfil del usuario autenticado.

**Tareas**:
- [ ] `GET /users/me`: retornar perfil del usuario autenticado (sin password_hash)
- [ ] `PUT /users/me`: actualizar nombre, teléfono, foto_url
- [ ] Upload de foto: aceptar imagen (JPG/PNG/WEBP, máx 2MB), guardar en storage (por ahora filesystem local), retornar URL
- [ ] Validar que el nuevo email no esté en uso si se permite cambio de email

**Criterios de aceptación** (de HU-01-05):
- Cambios se reflejan en todas las natilleras donde participa
- Imagen >2MB devuelve error con formatos aceptados
- `password_hash` nunca aparece en la respuesta

---

### ISSUE-08: Autenticación de dos factores (2FA)

**Complejidad**: 2.0 | **Prioridad**: P3 | **Fase**: Fase 4  
**HU**: HU-01-06  
**Labels**: `backend` `auth` `security`  
**Depende de**: ISSUE-05

**Descripción**:
Implementar 2FA con TOTP (Google Authenticator / Authy compatible).

**Tareas**:
- [ ] `POST /auth/2fa/habilitar`: generar secret TOTP, retornar QR code URL
- [ ] `POST /auth/2fa/confirmar`: verificar código TOTP para activar 2FA
- [ ] `POST /auth/2fa/deshabilitar`: requiere contraseña actual
- [ ] Modificar login: si 2FA activo, primer paso retorna `requires_2fa: true`; segundo paso `POST /auth/2fa/verificar`
- [ ] Códigos de respaldo (backup codes): generar 8 códigos de un solo uso

**Criterios de aceptación** (de HU-01-06):
- Código TOTP inválido o expirado devuelve acceso denegado
- Sin 2FA el login no cambia

---

## E-02 — Gestión de Natilleras

---

### ISSUE-09: Crear y activar natillera (backend)

**Complejidad**: 2.0 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-02-01, HU-02-06  
**Labels**: `backend` `natilleras` `business-logic`  
**Depende de**: ISSUE-03

**Descripción**:
Implementar la creación de natilleras con generación automática del calendario de períodos y el flujo de activación.

**Tareas**:
- [ ] `schemas/natillera.py`: `NatilleraCreate`, `NatilleraResponse`, `NatilleraUpdate`
- [ ] `services/natillera_service.py`:
  - `crear(datos, admin_id)` → crea natillera en estado CONFIGURACION, agrega al creador como admin-socio
  - `activar(natillera_id, admin_id)` → valida mín. 2 socios activos, cambia estado a ACTIVA, genera calendario de períodos, emite evento `natillera.activada`
  - `_generar_calendario(natillera)` → crea registros `Periodo` según periodicidad y rango de fechas
- [ ] `api/v1/endpoints/natilleras.py`:
  - `POST /natilleras` — crear
  - `POST /natilleras/{id}/activar` — solo admin
- [ ] Validaciones: fecha_fin > fecha_inicio, monto > 0, max_socios >= 2 (RN-12)
- [ ] Al activar: notificar a todos los socios (evento)

**Criterios de aceptación** (de HU-02-01, HU-02-06):
- Natillera semanal de 1 año genera 52 períodos automáticamente
- `monto = 0` devuelve error `"El monto debe ser mayor a cero"`
- Activar con menos de 2 socios devuelve 409 con mensaje claro
- Estado inicial siempre es `CONFIGURACION`

---

### ISSUE-10: Consultar y editar natilleras (backend)

**Complejidad**: 1.0 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-02-02, HU-02-03, HU-02-04, HU-02-05  
**Labels**: `backend` `natilleras`  
**Depende de**: ISSUE-09

**Descripción**:
Endpoints para listar, detallar y editar natilleras con vistas diferenciadas para admin y socio.

**Tareas**:
- [ ] `GET /natilleras`: listar natilleras del usuario (admin + socio); retornar nombre, rol, estado, saldo_acumulado_personal, siguiente_fecha_pago
- [ ] `GET /natilleras/{id}`: si es admin → vista completa (saldo fondo, todos los socios con estado, socios en mora); si es socio → solo su información, NO datos financieros de otros socios
- [ ] `PUT /natilleras/{id}`: solo admin, solo nombre y descripción; rechazar cambio de monto o periodicidad en natillera ACTIVA (RN-02, RN-03)

**Criterios de aceptación** (de HU-02-02 a 02-05):
- Socio ve su saldo pero NO el detalle financiero de otros socios
- Cambiar monto en natillera activa devuelve 409
- Usuario sin natilleras recibe lista vacía (no error)

---

### ISSUE-11: Cerrar y archivar natillera (backend)

**Complejidad**: 1.0 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-02-07, HU-02-08  
**Labels**: `backend` `natilleras` `business-logic`  
**Depende de**: ISSUE-10

**Descripción**:
Implementar el ciclo de vida completo: cierre y archivo de natilleras.

**Tareas**:
- [ ] `POST /natilleras/{id}/cerrar`: solo admin; validar que `fecha_fin` fue alcanzada; si hay socios en mora, retornar advertencia con lista y requerir `force: true` para confirmar; cambiar estado a EN_CIERRE; no aceptar más pagos
- [ ] `POST /natilleras/{id}/archivar`: solo si estado es CERRADA y distribución final completada; cambiar a ARCHIVADA
- [ ] `GET /natilleras?incluir_archivadas=false` por defecto excluye ARCHIVADAS del dashboard

**Criterios de aceptación** (de HU-02-07, HU-02-08):
- Cierre con socios en mora devuelve lista de morosos antes de proceder
- Natillera archivada no aparece en dashboard pero sigue siendo consultable

---

## E-03 — Gestión de Socios

---

### ISSUE-12: Invitar y aceptar socios (backend)

**Complejidad**: 2.0 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-03-01, HU-03-02  
**Labels**: `backend` `socios` `notifications`  
**Depende de**: ISSUE-09

**Descripción**:
Sistema de invitaciones por email con enlace de un solo uso y flujo de aceptación.

**Tareas**:
- [ ] `models/invitacion.py`: `token` (UUID), `natillera_id`, `email_invitado`, `invitado_por` (FK), `expira_at` (48h), `aceptada` (bool), `created_at`
- [ ] `POST /natilleras/{id}/invitaciones`: solo admin; validar cupo máximo (RN-12); crear invitación, enviar email con link
- [ ] `POST /invitaciones/{token}/aceptar`: validar token vigente; si email tiene cuenta → agregar como socio; si no → redirigir a registro con token
- [ ] `GET /natilleras/{id}/invitaciones`: listar invitaciones pendientes (solo admin)
- [ ] `DELETE /natilleras/{id}/invitaciones/{token}`: revocar invitación pendiente

**Criterios de aceptación** (de HU-03-01, HU-03-02):
- Cupo lleno devuelve 409 `"Cupo máximo de socios alcanzado"`
- Token expirado (>48h) devuelve mensaje indicando que solicite nueva invitación
- Usuario sin cuenta que acepta invitación queda unido automáticamente al completar registro

---

### ISSUE-13: Listar, suspender y eliminar socios (backend)

**Complejidad**: 1.5 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-03-03, HU-03-04, HU-03-05  
**Labels**: `backend` `socios` `business-logic`  
**Depende de**: ISSUE-12

**Descripción**:
Gestión del ciclo de vida de socios dentro de una natillera.

**Tareas**:
- [ ] `GET /natilleras/{id}/socios`: solo admin; retornar por socio: nombre, email, fecha_ingreso, estado_periodo_actual (pagado/pendiente/en_mora), total_aportado
- [ ] `PUT /natilleras/{id}/socios/{socio_id}/suspender`: requiere `razon` obligatoria; notificar al socio; registrar en audit log
- [ ] `PUT /natilleras/{id}/socios/{socio_id}/reactivar`: reactivar socio suspendido
- [ ] `DELETE /natilleras/{id}/socios/{socio_id}`: solo si el socio no tiene ningún pago registrado; si tiene pagos → devuelve 409 sugiriendo usar "suspender" (RN-09)

**Criterios de aceptación** (de HU-03-03 a 03-05):
- Eliminar socio con pagos devuelve 409 con sugerencia de suspender
- Suspensión requiere razón no vacía
- Socio suspendido no puede registrar pagos

---

### ISSUE-14: Transferir administración de natillera

**Complejidad**: 1.0 | **Prioridad**: P2 | **Fase**: Fase 2  
**HU**: HU-03-06  
**Labels**: `backend` `socios` `natilleras`  
**Depende de**: ISSUE-13

**Descripción**:
Permitir al administrador transferir su rol a otro socio activo.

**Tareas**:
- [ ] `POST /natilleras/{id}/transferir-admin`: requiere `nuevo_admin_id` y `password` del admin actual (confirmación); validar que `nuevo_admin_id` es socio activo de la natillera; actualizar `admin_id` en natillera; registrar en audit log; notificar a ambos usuarios
- [ ] Validar que la natillera no quede sin admin (RN-01)

**Criterios de aceptación** (de HU-03-06):
- Requiere contraseña del admin actual para confirmar
- El ex-admin queda como socio regular
- Ambos reciben notificación del cambio

---

## E-04 — Aportes y Pagos

---

### ISSUE-15: Registrar pago manual por administrador (backend)

**Complejidad**: 2.0 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-04-01  
**Labels**: `backend` `pagos` `business-logic`  
**Depende de**: ISSUE-11

**Descripción**:
Implementar el flujo principal de registro de pago en efectivo por parte del administrador, con atomicidad garantizada (Unit of Work).

**Tareas**:
- [ ] `services/pago_service.py`:
  - `registrar_por_admin(socio_id, periodo_id, monto, metodo, admin_id)` → verificar que el socio pertenece a la natillera, verificar período abierto, crear pago en estado CONFIRMADO, actualizar saldo del fondo, registrar en audit log — todo en una transacción
  - Si monto ≠ monto estándar de la natillera → registrar advertencia pero permitir con confirmación explícita (`forzar: bool`)
- [ ] `POST /natilleras/{natillera_id}/pagos` (por admin): solo admin
- [ ] Emitir evento `pago.confirmado` (notificación al socio)

**Criterios de aceptación** (de HU-04-01):
- Si falla cualquier paso (UPDATE saldo, INSERT audit), se hace rollback completo (RN-10)
- Monto diferente al estándar solo se acepta con `forzar: true`
- Socio recibe notificación automática al confirmar

---

### ISSUE-16: Registrar pago propio por socio y confirmación por admin (backend)

**Complejidad**: 2.0 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-04-02, HU-04-03  
**Labels**: `backend` `pagos` `business-logic`  
**Depende de**: ISSUE-15

**Descripción**:
Flujo de dos pasos: socio registra pago como PENDIENTE_CONFIRMACION, admin confirma o rechaza.

**Tareas**:
- [ ] `services/pago_service.py`:
  - `registrar_por_socio(socio_id, periodo_id, metodo, referencia, comprobante_url)` → crear pago en estado PENDIENTE_CONFIRMACION; emitir `pago.pendiente_confirmacion` para notificar al admin
  - `confirmar(pago_id, admin_id)` → validar que el pago es de su natillera, cambiar estado a CONFIRMADO, actualizar saldo, audit log, emitir `pago.confirmado`
  - `rechazar(pago_id, admin_id, razon)` → cambiar a RECHAZADO, período vuelve a PENDIENTE, emitir `pago.rechazado`
- [ ] Validar que no exista pago activo (no RECHAZADO) para el mismo período (RN-02 implícito)
- [ ] `PUT /pagos/{id}/confirmar` y `PUT /pagos/{id}/rechazar`

**Criterios de aceptación** (de HU-04-02, HU-04-03):
- Pago duplicado para mismo período devuelve 409
- Rechazo requiere `razon` no vacía
- Rechazo deja el período en estado PENDIENTE nuevamente

---

### ISSUE-17: Revertir pago confirmado (backend)

**Complejidad**: 1.5 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-04-04  
**Labels**: `backend` `pagos` `audit`  
**Depende de**: ISSUE-16

**Descripción**:
Implementar la reversión de pagos ya confirmados con trazabilidad completa. El pago no se elimina, queda en estado REVERTIDO (RN-06).

**Tareas**:
- [ ] `services/pago_service.py`: `revertir(pago_id, admin_id, justificacion)` → cambiar estado a REVERTIDO, ajustar saldo del fondo (restar), período vuelve a PENDIENTE, registrar en audit log con `datos_anteriores` y `datos_nuevos`
- [ ] Si el pago tiene más de 72 horas → requerir confirmación con contraseña del admin (`password_confirmar`)
- [ ] `PUT /pagos/{id}/revertir`

**Criterios de aceptación** (de HU-04-04):
- El pago revertido permanece en BD con estado REVERTIDO (no se elimina)
- El audit log registra: usuario, acción, timestamp, IP, datos antes y después
- Reversión >72h requiere contraseña del admin
- El saldo del fondo se ajusta correctamente tras la reversión

---

### ISSUE-18: Integración pasarela de pago Stripe (backend)

**Complejidad**: 3.0 | **Prioridad**: P1 | **Fase**: Fase 2  
**HU**: HU-04-05  
**Labels**: `backend` `pagos` `stripe` `integration`  
**Depende de**: ISSUE-16

**Descripción**:
Integrar Stripe para pagos digitales directos sin intervención del admin, usando el patrón Strategy definido en `docs/design/02-patrones-diseno.md`.

**Tareas**:
- [ ] Implementar `EstrategiaPago` base y `PagoStripe(EstrategiaPago)` en `services/pagos/estrategias.py`
- [ ] `POST /natilleras/{id}/pagos/stripe/intent`: crear PaymentIntent de Stripe; retornar `client_secret` al frontend
- [ ] `POST /stripe/webhook`: endpoint público para recibir eventos de Stripe; verificar firma con `stripe-signature`; al recibir `payment_intent.succeeded` → confirmar pago automáticamente (sin intervención admin)
- [ ] Manejo de errores: `CardError` → 402; `APIConnectionError` → 503; fallo → período sigue PENDIENTE, no crear registro de pago
- [ ] Variables de entorno: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`

**Criterios de aceptación** (de HU-04-05):
- Pago exitoso por Stripe queda CONFIRMADO automáticamente (sin confirmar admin)
- Fallo en pasarela no crea registro de pago
- Webhook verifica la firma de Stripe antes de procesar

---

## E-05 — Saldos y Estado de Cuenta

---

### ISSUE-19: Cálculo de saldos y detección automática de mora (backend)

**Complejidad**: 2.0 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-05-01, HU-05-02, HU-05-04  
**Labels**: `backend` `business-logic` `scheduler`  
**Depende de**: ISSUE-16

**Descripción**:
Implementar el servicio de cálculo de saldos y el job nocturno que detecta mora automáticamente.

**Tareas**:
- [ ] `services/saldo_service.py`:
  - `calcular_saldo_fondo(natillera_id)` → suma aportes CONFIRMADOS − distribuciones realizadas (RN-10)
  - `calcular_estado_socio(natillera_id, socio_id)` → total aportado, períodos al día, períodos en mora, monto en mora
  - `calcular_saldo_personal(natillera_id, socio_id)` → proporción del fondo que corresponde al socio
- [ ] Job nocturno (`scheduler/mora_detector.py`): cada noche a las 00:00, detectar socios con período vencido >3 días sin pago confirmado, marcar como EN_MORA, emitir `socio.en_mora`
- [ ] `GET /natilleras/{id}/saldo`: solo admin, retornar saldo total, aportes recibidos período actual, pendientes del período, total distribuido
- [ ] `GET /natilleras/{id}/mi-estado`: socio, retornar su estado de cuenta personal
- [ ] Scheduler: usar `APScheduler` o tarea periódica de FastAPI lifespan

**Criterios de aceptación** (de HU-05-01, HU-05-02, HU-05-04):
- Saldo usa `Decimal`, no `float`
- Mora se detecta automáticamente (no requiere acción manual)
- Socio en mora recibe alerta, admin también

---

### ISSUE-20: Historial de transacciones con filtros y paginación

**Complejidad**: 1.5 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-05-03  
**Labels**: `backend` `transactions` `api`  
**Depende de**: ISSUE-19

**Descripción**:
Endpoint de historial paginado con filtros, con vista diferenciada admin/socio.

**Tareas**:
- [ ] `GET /natilleras/{id}/pagos`: paginado (20 por página, `?page=1&size=20`); filtros: `?estado=confirmado`, `?desde=YYYY-MM-DD`, `?hasta=YYYY-MM-DD`, `?socio_id=X`
- [ ] Admin ve historial de todos los socios; socio ve solo el suyo (validar en service)
- [ ] Response: lista de pagos con fecha, descripción, monto, estado, referencia; total de páginas

**Criterios de aceptación** (de HU-05-03):
- Socio no puede ver pagos de otros socios (devuelve 403 si intenta filtrar por otro `socio_id`)
- Paginación devuelve correctamente `total`, `page`, `size`, `pages`

---

## E-06 — Distribuciones

---

### ISSUE-21: Préstamo interno entre socios (distribución parcial)

**Complejidad**: 3.0 | **Prioridad**: P2 | **Fase**: Fase 3  
**HU**: HU-06-01  
**Labels**: `backend` `distribuciones` `business-logic`  
**Depende de**: ISSUE-19

**Descripción**:
Sistema de préstamos internos donde el fondo presta a un socio con interés, generando rentabilidad para la natillera.

**Tareas**:
- [ ] `models/prestamo.py`: `id`, `natillera_id`, `socio_id`, `monto`, `tasa_interes_mensual`, `plazo_periodos`, `estado`, `created_at`
- [ ] `services/prestamo_service.py`: `crear_prestamo(natillera_id, socio_id, monto, tasa, plazo, admin_id)` → validar fondos disponibles, socio sin mora (RN-04 y RN-08), reducir saldo del fondo, generar plan de pagos; emitir `prestamo.creado`
- [ ] Al registrar pago de cuota del préstamo: calcular interés acumulado, sumar al fondo (RN-11)
- [ ] `POST /natilleras/{id}/prestamos` y `GET /natilleras/{id}/prestamos`

**Criterios de aceptación** (de HU-06-01):
- Monto mayor al saldo disponible devuelve 409 `"Fondos insuficientes"`
- Socio en mora no puede recibir préstamo (RN-04)
- Los intereses pagados se suman al fondo y benefician a todos (RN-11)

---

### ISSUE-22: Distribución final del fondo

**Complejidad**: 2.0 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-06-02  
**Labels**: `backend` `distribuciones` `business-logic`  
**Depende de**: ISSUE-21

**Descripción**:
Implementar la distribución final al cierre del ciclo, con cálculo equitativo y pre-visualización antes de confirmar.

**Tareas**:
- [ ] `services/distribucion_service.py`:
  - `calcular_distribucion_final(natillera_id)` → retornar preview: por cada socio activo: monto_base + proporción de rentabilidad − deudas pendientes; socios con mora no saldada excluibles según configuración
  - `ejecutar_distribucion_final(natillera_id, admin_id, confirmacion: bool)` → solo si natillera en EN_CIERRE (RN-07); crear registros `Distribucion`; cambiar natillera a CERRADA; notificar a cada socio; generar comprobante de distribución
- [ ] `POST /natilleras/{id}/distribucion/preview`: solo admin, retornar cálculo sin ejecutar
- [ ] `POST /natilleras/{id}/distribucion/ejecutar`: solo admin, requiere `confirmado: true`

**Criterios de aceptación** (de HU-06-02):
- Distribución sin confirmar preview primero muestra advertencia
- Distribución solo disponible en estado EN_CIERRE (RN-07)
- Cada socio recibe notificación con su monto
- La natillera pasa a CERRADA al ejecutar

---

## E-07 — Notificaciones y Alertas

---

### ISSUE-23: Sistema de notificaciones por email (backend)

**Complejidad**: 2.0 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-07-01, HU-07-02, HU-07-03  
**Labels**: `backend` `notifications` `email`  
**Depende de**: ISSUE-16

**Descripción**:
Implementar el sistema de notificaciones basado en eventos (Observer Pattern de `docs/design/02-patrones-diseno.md`) con envío real de emails.

**Tareas**:
- [ ] `core/events.py`: sistema pub/sub simple con `emit(evento, **kwargs)` y `@on(evento)` decorator
- [ ] `services/email_service.py`: cliente SMTP con plantillas HTML; variables: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
- [ ] Handlers registrados con `@on(...)`:
  - `pago.confirmado` → email + push al socio con monto, período, saldo, link comprobante
  - `pago.rechazado` → email al socio con razón y CTA
  - `socio.en_mora` → email al socio (alerta) y al admin (reporte)
  - `natillera.activada` → email a todos los socios
  - `prestamo.creado` → email al socio con plan de pagos
- [ ] Recordatorio periódico (job): 3 días antes de cada fecha límite de período → email a socios con pago pendiente (HU-07-01)
- [ ] Ejecución asíncrona con `BackgroundTasks` de FastAPI para no bloquear el request

**Criterios de aceptación** (de HU-07-01 a 07-03):
- Socio que ya pagó NO recibe recordatorio
- Notificación crítica (mora, distribución) siempre se envía sin importar preferencias
- Si el servicio de email falla, la operación principal no falla (errores de notificación se loggean, no se propagan)

---

### ISSUE-24: Preferencias de notificación del usuario

**Complejidad**: 1.0 | **Prioridad**: P2 | **Fase**: Fase 2  
**HU**: HU-07-04  
**Labels**: `backend` `notifications` `users`  
**Depende de**: ISSUE-23

**Descripción**:
Permitir que los usuarios configuren qué notificaciones reciben y por qué canal.

**Tareas**:
- [ ] `models/preferencias_notificacion.py`: `usuario_id`, `tipo` (recordatorio/confirmacion/alerta), `canal` (email/push), `activo`
- [ ] `GET /users/me/notificaciones` y `PUT /users/me/notificaciones`
- [ ] Modificar handlers de eventos para consultar preferencias antes de enviar
- [ ] Notificaciones críticas (mora, distribución) ignorar preferencias — siempre enviar (HU-07-04)

---

## E-08 — Reportes y Comprobantes

---

### ISSUE-25: Generación de comprobante de pago en PDF

**Complejidad**: 2.0 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-08-01  
**Labels**: `backend` `reports` `pdf`  
**Depende de**: ISSUE-16

**Descripción**:
Generar comprobante de pago en PDF con número de referencia único y QR de verificación.

**Tareas**:
- [ ] `services/comprobante_service.py`: `generar_comprobante_pago(pago_id)` → generar PDF con: nombre natillera, nombre socio, monto, período, fecha confirmación, número referencia único (`COMP-{año}-{id:07d}`), QR con URL de verificación
- [ ] Librería recomendada: `reportlab` o `weasyprint`
- [ ] `GET /pagos/{id}/comprobante`: retornar PDF como `application/pdf`
- [ ] URL de verificación pública: `GET /verificar/comprobante/{referencia}` → retornar JSON con estado del pago (no requiere autenticación)
- [ ] Guardar URL del comprobante en `pago.comprobante_url`

**Criterios de aceptación** (de HU-08-01):
- PDF contiene todos los campos requeridos
- QR lleva a URL pública de verificación
- Endpoint de verificación no requiere autenticación
- Comprobante solo disponible para pagos CONFIRMADOS

---

### ISSUE-26: Reportes de natillera exportables

**Complejidad**: 2.0 | **Prioridad**: P2 | **Fase**: Fase 2  
**HU**: HU-08-02, HU-08-03  
**Labels**: `backend` `reports` `export`  
**Depende de**: ISSUE-25

**Descripción**:
Reportes descargables del estado completo de la natillera y del historial personal del socio.

**Tareas**:
- [ ] `GET /natilleras/{id}/reportes/balance`: JSON con: lista socios, aportes de cada uno, saldo fondo, socios en mora, distribuciones realizadas
- [ ] `GET /natilleras/{id}/reportes/exportar?formato=pdf|excel`: solo admin; generar archivo descargable
- [ ] `GET /natilleras/{id}/mi-reporte?formato=pdf`: socio, solo su historial personal
- [ ] Librería Excel: `openpyxl`

---

## E-09 — Seguridad y Auditoría

---

### ISSUE-27: Log de auditoría inmutable

**Complejidad**: 1.5 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-09-01  
**Labels**: `backend` `audit` `security`  
**Depende de**: ISSUE-03

**Descripción**:
Implementar el log de auditoría para todas las operaciones críticas. El log es de solo inserción: no existen endpoints ni métodos de UPDATE o DELETE para esta tabla.

**Tareas**:
- [ ] `audit_repo.py`: solo método `registrar(accion, entidad, entidad_id, usuario_id, datos_anteriores, datos_nuevos, ip)` — no implementar `update` ni `delete`
- [ ] Disparar registro de auditoría en: confirmar pago, revertir pago, rechazar pago, cambiar admin, crear/activar/cerrar natillera, ejecutar distribución, suspender/eliminar socio
- [ ] Middleware para capturar IP del request y pasarla al contexto
- [ ] `GET /natilleras/{id}/auditoria`: solo admin, paginado, filtros por acción y rango de fechas
- [ ] Trigger en PostgreSQL como segunda línea de defensa: `BEFORE DELETE OR UPDATE ON audit_log → RAISE EXCEPTION`

**Criterios de aceptación** (de HU-09-01):
- Toda operación crítica genera un registro con diff (antes/después)
- El endpoint de consulta no expone datos de otras natilleras
- Intentar UPDATE/DELETE en `audit_log` lanza excepción a nivel de BD

---

### ISSUE-28: Verificación de integridad de comprobante por QR

**Complejidad**: 1.0 | **Prioridad**: P3 | **Fase**: Fase 4  
**HU**: HU-09-02  
**Labels**: `backend` `security` `audit`  
**Depende de**: ISSUE-25

**Descripción**:
Endpoint público para verificar la autenticidad de un comprobante de pago mediante el código QR.

**Tareas**:
- [ ] `GET /verificar/{referencia}`: no requiere autenticación; buscar pago por referencia; retornar: `valido: bool`, y si válido: natillera, socio (solo nombre), monto, fecha, estado actual del pago
- [ ] Si el pago fue revertido después de emitir el comprobante: retornar `valido: false` con mensaje explicativo

---

## FRONTEND — Setup y UI

---

### ISSUE-29: Setup frontend con estructura feature-based

**Complejidad**: 1.0 | **Prioridad**: P0 | **Fase**: MVP  
**Labels**: `frontend` `setup` `architecture`

**Descripción**:
Configurar la estructura de carpetas feature-based definida en `docs/design/04-frontend-arquitectura.md`. No usar la estructura por tipo de archivo del scaffold inicial.

**Tareas**:
- [ ] Reorganizar `src/` en: `features/auth/`, `features/natilleras/`, `features/pagos/`, `features/reportes/`, `shared/`, `pages/`, `store/`, `lib/`
- [ ] `lib/apiClient.js`: Axios con interceptor de token (Authorization header) e interceptor de respuesta para refresh automático y redirect a login en 401
- [ ] `store/authStore.js`: Zustand + persist para `usuario` y `accessToken`
- [ ] `shared/utils/formatCurrency.js`: `formatCOP(centavos)` con `Intl.NumberFormat`
- [ ] Configurar TanStack Query: `QueryClient` con `staleTime: 60000`, `QueryClientProvider` en `main.jsx`
- [ ] React Router v6: rutas protegidas con `PrivateRoute`, rutas: `/login`, `/register`, `/dashboard`, `/natilleras/:id`, `/perfil`
- [ ] `npm run lint` pasa sin warnings

**Criterios de aceptación**:
- `npm run dev` corre sin errores
- `npm run lint` pasa con 0 warnings
- La estructura de carpetas sigue exactamente `docs/design/04-frontend-arquitectura.md`

---

### ISSUE-30: UI de Autenticación (login, registro, recuperación)

**Complejidad**: 1.5 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-01-01, HU-01-02, HU-01-04  
**Labels**: `frontend` `auth` `ui`  
**Depende de**: ISSUE-29

**Tareas**:
- [ ] `features/auth/components/LoginForm.jsx`: email, password, mensajes de error del servidor, loading state
- [ ] `features/auth/components/RegisterForm.jsx`: nombre, email, password, confirmar password con validación
- [ ] `features/auth/components/RecuperarPasswordForm.jsx`
- [ ] `features/auth/hooks/useLogin.js`, `useRegister.js`, `useRecuperarPassword.js` con `useMutation`
- [ ] Al login exitoso: guardar token en Zustand, redirect a `/dashboard`
- [ ] Al error: mostrar mensaje exacto del backend (no mensajes genéricos)
- [ ] Pantalla de verificación de email post-registro

---

### ISSUE-31: Dashboard de natilleras y detalle

**Complejidad**: 2.0 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-02-02, HU-02-03, HU-02-04  
**Labels**: `frontend` `natilleras` `dashboard`  
**Depende de**: ISSUE-30

**Tareas**:
- [ ] `features/natilleras/hooks/useNatilleras.js` y `useNatilleraDetalle.js` con TanStack Query y query keys estandarizadas
- [ ] `pages/Dashboard.jsx`: cards de natilleras (nombre, rol, estado, saldo personal, próximo pago); estado vacío con CTA
- [ ] `pages/NatilleraDetalle.jsx`: tabs (Resumen / Socios / Pagos / Reportes); vista diferenciada admin vs socio
- [ ] `features/natilleras/components/NatilleraCard.jsx`, `SaldoFondo.jsx`, `EstadoSocio.jsx`
- [ ] Todos los montos formateados con `formatCOP()`

---

### ISSUE-32: Formularios de creación y gestión de natillera

**Complejidad**: 1.5 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-02-01, HU-02-05, HU-02-06, HU-02-07  
**Labels**: `frontend` `natilleras` `forms`  
**Depende de**: ISSUE-31

**Tareas**:
- [ ] `features/natilleras/components/CrearNatilleraForm.jsx`: nombre, descripción, monto, periodicidad, fechas, max_socios; validaciones client-side
- [ ] `features/natilleras/hooks/useCrearNatillera.js`, `useActivarNatillera.js`, `useCerrarNatillera.js`
- [ ] Modal de confirmación de cierre: si hay socios en mora, mostrar lista y pedir confirmación explícita
- [ ] Feedback visual: toast de éxito/error, loading en botones, invalidación de queries al mutar

---

### ISSUE-33: Gestión de socios en el frontend

**Complejidad**: 1.5 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-03-01, HU-03-02, HU-03-03, HU-03-04, HU-03-05  
**Labels**: `frontend` `socios` `ui`  
**Depende de**: ISSUE-32

**Tareas**:
- [ ] `features/natilleras/components/SociosList.jsx`: tabla con nombre, estado pago período actual, total aportado; badge de mora; botones admin: suspender/eliminar
- [ ] `features/natilleras/components/InvitarSocioForm.jsx`: input email, botón enviar
- [ ] Pantalla de aceptación de invitación: `pages/AceptarInvitacion.jsx`
- [ ] Modal de suspensión: campo razón obligatorio

---

### ISSUE-34: Flujo de pagos en el frontend

**Complejidad**: 2.0 | **Prioridad**: P0 | **Fase**: MVP  
**HU**: HU-04-01, HU-04-02, HU-04-03, HU-04-04  
**Labels**: `frontend` `pagos` `forms`  
**Depende de**: ISSUE-33

**Tareas**:
- [ ] `features/pagos/components/RegistrarPagoForm.jsx`: período actual, monto (precompletado desde API, no editable por defecto), método, referencia, subir comprobante (imagen)
- [ ] `features/pagos/components/PagosPendientesConfirmacion.jsx`: lista para admin con botones confirmar/rechazar; modal de razón para rechazo
- [ ] `features/pagos/components/HistorialPagos.jsx`: tabla paginada con filtros; botón descargar comprobante PDF
- [ ] `features/pagos/hooks/useRegistrarPago.js`, `useConfirmarPago.js`, `useRechazarPago.js`
- [ ] **El monto se obtiene siempre del servidor, nunca calculado en el cliente**

---

### ISSUE-35: Vista de distribución final en el frontend

**Complejidad**: 1.5 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-06-02  
**Labels**: `frontend` `distribuciones` `ui`  
**Depende de**: ISSUE-34

**Tareas**:
- [ ] `features/distribuciones/components/DistribucionPreview.jsx`: mostrar tabla con monto por socio antes de confirmar
- [ ] `features/distribuciones/components/ConfirmarDistribucion.jsx`: botón confirmar con diálogo de confirmación + contraseña
- [ ] `features/distribuciones/hooks/useDistribucionPreview.js` y `useEjecutarDistribucion.js`

---

## MOBILE — Setup y Pantallas

---

### ISSUE-36: Setup mobile con navegación y SecureStore

**Complejidad**: 1.0 | **Prioridad**: P1 | **Fase**: MVP  
**Labels**: `mobile` `setup` `navigation`

**Tareas**:
- [ ] Configurar React Navigation: Bottom Tabs (Dashboard, Mis Pagos, Perfil) + Stack Navigator por tab
- [ ] `services/apiClient.js`: Axios con interceptor de token (mismo patrón que frontend)
- [ ] Almacenamiento de tokens con `expo-secure-store` (nunca `AsyncStorage` para tokens)
- [ ] `store/authStore.js`: Zustand + SecureStore persistence
- [ ] Probar en Expo Go (Android e iOS)

---

### ISSUE-37: Pantallas de autenticación mobile

**Complejidad**: 1.0 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-01-01, HU-01-02  
**Labels**: `mobile` `auth`  
**Depende de**: ISSUE-36

**Tareas**:
- [ ] `screens/Auth/LoginScreen.jsx`: email, password (secureTextEntry), botón, link registro
- [ ] `screens/Auth/RegisterScreen.jsx`
- [ ] Tokens en `expo-secure-store`, nunca en `AsyncStorage`
- [ ] Redirect a tabs tras login exitoso

---

### ISSUE-38: Pantalla dashboard mobile y detalle de natillera

**Complejidad**: 1.5 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-02-02, HU-02-04  
**Labels**: `mobile` `dashboard`  
**Depende de**: ISSUE-37

**Tareas**:
- [ ] `screens/Dashboard/DashboardScreen.jsx`: FlatList de tarjetas, pull-to-refresh con TanStack Query
- [ ] `screens/Natilleras/NatilleraDetalleScreen.jsx`: resumen, socios, mis pagos
- [ ] Montos formateados con `Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' })`

---

### ISSUE-39: Pantalla de pagos mobile

**Complejidad**: 1.5 | **Prioridad**: P1 | **Fase**: MVP  
**HU**: HU-04-02  
**Labels**: `mobile` `pagos`  
**Depende de**: ISSUE-38

**Tareas**:
- [ ] `screens/Pagos/RegistrarPagoScreen.jsx`: selector de natillera y período, método, referencia, foto de comprobante con `expo-image-picker`
- [ ] `screens/Pagos/MisPagosScreen.jsx`: historial con estados y badge de mora
- [ ] Toast de confirmación o error (con `expo-toast` o similar)

---

### ISSUE-40: Notificaciones push mobile

**Complejidad**: 2.0 | **Prioridad**: P2 | **Fase**: Fase 2  
**HU**: HU-07-01, HU-07-02  
**Labels**: `mobile` `notifications` `push`  
**Depende de**: ISSUE-39

**Tareas**:
- [ ] Configurar `expo-notifications`: permisos, registrar token de dispositivo
- [ ] Enviar token al backend `PUT /users/me/push-token`
- [ ] Backend: `services/push_service.py` con Expo Push API
- [ ] Handlers para notificaciones en foreground y background

---

## TESTING

---

### ISSUE-41: Tests unitarios — autenticación y servicios core

**Complejidad**: 1.5 | **Prioridad**: P1 | **Fase**: MVP  
**Labels**: `backend` `testing`  
**Depende de**: ISSUE-05

**Tareas**:
- [ ] Configurar BD de test con SQLite en memoria en `conftest.py`; fixtures: `db_session`, `usuario_admin`, `usuario_socio`, `natillera_activa`
- [ ] `tests/test_auth.py`: registro exitoso, email duplicado, contraseña débil, login correcto, login incorrecto, bloqueo por 5 intentos, refresh, logout
- [ ] `tests/test_usuario_service.py`: editar perfil, subir foto, validaciones
- [ ] Markers pytest: `@pytest.mark.auth`
- [ ] `pytest --cov=app --cov-report=term-missing`; target: >80% en servicios de auth

---

### ISSUE-42: Tests unitarios — servicios de natillera y pagos

**Complejidad**: 2.0 | **Prioridad**: P1 | **Fase**: MVP  
**Labels**: `backend` `testing`  
**Depende de**: ISSUE-16

**Tareas**:
- [ ] `tests/test_natillera_service.py`: crear, activar (con <2 socios), cerrar (con mora), archivar; generación correcta de calendario de períodos; `@pytest.mark.natillera`
- [ ] `tests/test_pago_service.py`: registrar por admin, registrar por socio, confirmar, rechazar, revertir, revertir >72h, pago duplicado mismo período; `@pytest.mark.transaction`
- [ ] `tests/test_saldo_service.py`: cálculo de saldo con pagos confirmados y revertidos; detección de mora
- [ ] Usar `FakeRepository` en lugar de BD real para tests unitarios de servicios

---

### ISSUE-43: Tests de integración — endpoints API

**Complejidad**: 2.0 | **Prioridad**: P2 | **Fase**: MVP  
**Labels**: `backend` `testing` `integration`  
**Depende de**: ISSUE-42

**Tareas**:
- [ ] `tests/test_api_natilleras.py`: flujo completo CRUD via HTTP con `httpx.AsyncClient`; `@pytest.mark.integration`
- [ ] `tests/test_api_pagos.py`: flujo completo registro → confirmación → comprobante
- [ ] `tests/test_api_distribucion.py`: preview + ejecución de distribución final
- [ ] Configurar BD de test PostgreSQL separada (no SQLite) para tests de integración
- [ ] Separar en CI: tests unitarios rápidos + tests de integración más lentos

---

### ISSUE-44: Tests frontend con Vitest

**Complejidad**: 1.5 | **Prioridad**: P2 | **Fase**: Fase 2  
**Labels**: `frontend` `testing`  
**Depende de**: ISSUE-34

**Tareas**:
- [ ] Configurar Vitest + `@testing-library/react` + `msw` para mock de API
- [ ] `features/auth/__tests__/LoginForm.test.jsx`: renderiza, valida campos, maneja error del servidor
- [ ] `features/pagos/__tests__/RegistrarPagoForm.test.jsx`: monto viene del servidor, no calculado en cliente
- [ ] `shared/utils/__tests__/formatCurrency.test.js`: casos edge (0, negativos, grandes)
- [ ] `npm test` pasa

---

## CI/CD y DevOps

---

### ISSUE-45: GitHub Actions — tests backend

**Complejidad**: 1.0 | **Prioridad**: P2 | **Fase**: MVP  
**Labels**: `devops` `ci-cd` `testing`  
**Depende de**: ISSUE-43

**Tareas**:
- [ ] `.github/workflows/backend-tests.yml`: trigger `push` a `dev` y PR a `main`; Python 3.11; `pip install -r requirements.txt`; `pytest -m "not integration"` (tests rápidos); fallar si coverage <75%
- [ ] Job separado para tests de integración: solo en PR a `main`, requiere service PostgreSQL

---

### ISSUE-46: GitHub Actions — build y lint frontend

**Complejidad**: 0.5 | **Prioridad**: P2 | **Fase**: MVP  
**Labels**: `devops` `ci-cd` `frontend`  
**Depende de**: ISSUE-29

**Tareas**:
- [ ] `.github/workflows/frontend-ci.yml`: Node 18; `npm ci`; `npm run lint` (0 warnings); `npm run build`; `npm test`
- [ ] Fallar el CI si lint tiene warnings

---

### ISSUE-47: Documentación técnica — API_DOCS, DEVELOPMENT, DEPLOYMENT

**Complejidad**: 1.0 | **Prioridad**: P2 | **Fase**: MVP  
**Labels**: `docs`

**Tareas**:
- [ ] `docs/API_DOCS.md`: todos los endpoints con ejemplos curl, request/response bodies, códigos HTTP posibles
- [ ] `docs/DEVELOPMENT.md`: setup completo local (backend con venv, frontend, mobile); variables de entorno requeridas con descripción; comandos útiles; troubleshooting común
- [ ] `docs/DEPLOYMENT.md`: Vercel (frontend), Render (backend + PostgreSQL), variables de entorno en cada plataforma

---

## Resumen y Roadmap

### Conteo de issues

| Categoría | Issues | Complejidad total |
|-----------|--------|-------------------|
| Infraestructura | 01–03 | 4.5 |
| E-01 Autenticación | 04–08 | 6.0 |
| E-02 Natilleras | 09–11 | 5.0 |
| E-03 Socios | 12–14 | 4.5 |
| E-04 Pagos | 15–18 | 8.5 |
| E-05 Saldos | 19–20 | 3.5 |
| E-06 Distribuciones | 21–22 | 5.0 |
| E-07 Notificaciones | 23–24 | 3.0 |
| E-08 Reportes | 25–26 | 4.0 |
| E-09 Seguridad | 27–28 | 2.5 |
| Frontend | 29–35 | 11.0 |
| Mobile | 36–40 | 7.0 |
| Testing | 41–44 | 7.0 |
| CI/CD y Docs | 45–47 | 2.5 |
| **Total** | **47** | **~74 pts** |

---

### MVP (Fase 1 — Semanas 1–5)

Issues de backend: 01, 02, 03, 04, 05, 06, 07, 09, 10, 11, 12, 13, 15, 16, 17, 19, 20, 22, 23, 25, 27  
Issues de frontend: 29, 30, 31, 32, 33, 34, 35  
Issues de mobile: 36, 37, 38, 39  
Issues de testing: 41, 42  
Issues CI/CD: 45, 46, 47

### Fase 2 — Transacciones digitales

Issues: 14, 18, 24, 26, 40, 43, 44

### Fase 3 — Rentabilidad

Issues: 21

### Fase 4 — Seguridad avanzada

Issues: 08, 28

---

**Total issues**: 47  
**Versión**: 2.0  
**Última actualización**: Junio 2026  
**Basado en**: `CLIENT_BRIEF.md` v2.0
