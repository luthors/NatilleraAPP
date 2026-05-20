# Matriz de Trazabilidad — HU → Issue → Commit

Mapeo completo desde cada Historia de Usuario hasta el issue que la implementa y el commit que la resuelve.  
Actualizar la columna **Commit** y **Estado** cada vez que se cierre un issue.

---

## Leyenda de estados

| Estado | Significado |
|--------|-------------|
| `pendiente` | Issue no iniciado |
| `en progreso` | Issue en desarrollo activo |
| `completado` | Issue cerrado, commit registrado |
| `bloqueado` | Tiene dependencia sin resolver |

---

## E-01 — Autenticación y Perfil

| HU | Descripción | Issue | Estado | Commit | Archivos principales |
|----|-------------|-------|--------|--------|----------------------|
| HU-01-01 | Registro de usuario | ISSUE-04 | `pendiente` | — | `services/auth_service.py`, `api/v1/endpoints/auth.py` |
| HU-01-02 | Inicio de sesión | ISSUE-05 | `pendiente` | — | `services/auth_service.py`, `core/security.py` |
| HU-01-03 | Cierre de sesión | ISSUE-05 | `pendiente` | — | `api/v1/endpoints/auth.py` |
| HU-01-04 | Recuperación de contraseña | ISSUE-06 | `pendiente` | — | `models/password_reset_token.py` |
| HU-01-05 | Editar perfil | ISSUE-07 | `pendiente` | — | `api/v1/endpoints/users.py` |
| HU-01-06 | Autenticación 2FA | ISSUE-08 | `pendiente` | — | `core/security.py` |

---

## E-02 — Gestión de Natilleras

| HU | Descripción | Issue | Estado | Commit | Archivos principales |
|----|-------------|-------|--------|--------|----------------------|
| HU-02-01 | Crear natillera | ISSUE-09 | `pendiente` | — | `services/natillera_service.py`, `repositories/natillera_repo.py` |
| HU-02-02 | Ver mis natilleras | ISSUE-10 | `pendiente` | — | `api/v1/endpoints/natilleras.py` |
| HU-02-03 | Ver detalle (admin) | ISSUE-10 | `pendiente` | — | `services/natillera_service.py` |
| HU-02-04 | Ver detalle (socio) | ISSUE-10 | `pendiente` | — | `services/natillera_service.py` |
| HU-02-05 | Editar configuración | ISSUE-10 | `pendiente` | — | `services/natillera_service.py` |
| HU-02-06 | Activar natillera | ISSUE-09 | `pendiente` | — | `services/natillera_service.py`, `models/periodo.py` |
| HU-02-07 | Cerrar natillera | ISSUE-11 | `pendiente` | — | `services/natillera_service.py` |
| HU-02-08 | Archivar natillera | ISSUE-11 | `pendiente` | — | `services/natillera_service.py` |

---

## E-03 — Gestión de Socios

| HU | Descripción | Issue | Estado | Commit | Archivos principales |
|----|-------------|-------|--------|--------|----------------------|
| HU-03-01 | Invitar socio por email | ISSUE-12 | `pendiente` | — | `models/invitacion.py`, `services/socio_service.py` |
| HU-03-02 | Aceptar invitación | ISSUE-12 | `pendiente` | — | `api/v1/endpoints/invitaciones.py` |
| HU-03-03 | Ver lista de socios (admin) | ISSUE-13 | `pendiente` | — | `api/v1/endpoints/socios.py` |
| HU-03-04 | Suspender socio | ISSUE-13 | `pendiente` | — | `services/socio_service.py` |
| HU-03-05 | Eliminar socio | ISSUE-13 | `pendiente` | — | `services/socio_service.py` |
| HU-03-06 | Transferir administración | ISSUE-14 | `pendiente` | — | `services/natillera_service.py` |

---

## E-04 — Aportes y Pagos

| HU | Descripción | Issue | Estado | Commit | Archivos principales |
|----|-------------|-------|--------|--------|----------------------|
| HU-04-01 | Registrar pago por admin | ISSUE-15 | `pendiente` | — | `services/pago_service.py`, `repositories/pago_repo.py` |
| HU-04-02 | Registrar pago por socio | ISSUE-16 | `pendiente` | — | `services/pago_service.py` |
| HU-04-03 | Confirmar/rechazar pago | ISSUE-16 | `pendiente` | — | `api/v1/endpoints/pagos.py` |
| HU-04-04 | Revertir pago confirmado | ISSUE-17 | `pendiente` | — | `services/pago_service.py`, `repositories/audit_repo.py` |
| HU-04-05 | Pago por pasarela Stripe | ISSUE-18 | `pendiente` | — | `services/pagos/estrategias.py` |

---

## E-05 — Saldos y Estado de Cuenta

| HU | Descripción | Issue | Estado | Commit | Archivos principales |
|----|-------------|-------|--------|--------|----------------------|
| HU-05-01 | Consultar saldo del fondo (admin) | ISSUE-19 | `pendiente` | — | `services/saldo_service.py` |
| HU-05-02 | Consultar estado de cuenta (socio) | ISSUE-19 | `pendiente` | — | `services/saldo_service.py` |
| HU-05-03 | Historial de transacciones | ISSUE-20 | `pendiente` | — | `api/v1/endpoints/pagos.py` |
| HU-05-04 | Alerta automática de mora | ISSUE-19 | `pendiente` | — | `scheduler/mora_detector.py` |

---

## E-06 — Distribuciones

| HU | Descripción | Issue | Estado | Commit | Archivos principales |
|----|-------------|-------|--------|--------|----------------------|
| HU-06-01 | Distribución parcial (préstamo) | ISSUE-21 | `pendiente` | — | `services/prestamo_service.py`, `models/prestamo.py` |
| HU-06-02 | Distribución final del fondo | ISSUE-22 | `pendiente` | — | `services/distribucion_service.py` |

---

## E-07 — Notificaciones y Alertas

| HU | Descripción | Issue | Estado | Commit | Archivos principales |
|----|-------------|-------|--------|--------|----------------------|
| HU-07-01 | Recordatorio de pago próximo | ISSUE-23 | `pendiente` | — | `scheduler/recordatorios.py`, `services/email_service.py` |
| HU-07-02 | Confirmación de pago recibido | ISSUE-23 | `pendiente` | — | `core/events.py` |
| HU-07-03 | Alerta de pago rechazado | ISSUE-23 | `pendiente` | — | `core/events.py` |
| HU-07-04 | Preferencias de notificación | ISSUE-24 | `pendiente` | — | `models/preferencias_notificacion.py` |

---

## E-08 — Reportes y Comprobantes

| HU | Descripción | Issue | Estado | Commit | Archivos principales |
|----|-------------|-------|--------|--------|----------------------|
| HU-08-01 | Comprobante de pago PDF + QR | ISSUE-25 | `pendiente` | — | `services/comprobante_service.py` |
| HU-08-02 | Reporte de natillera exportable | ISSUE-26 | `pendiente` | — | `api/v1/endpoints/reportes.py` |
| HU-08-03 | Reporte personal del socio | ISSUE-26 | `pendiente` | — | `api/v1/endpoints/reportes.py` |

---

## E-09 — Seguridad y Auditoría

| HU | Descripción | Issue | Estado | Commit | Archivos principales |
|----|-------------|-------|--------|--------|----------------------|
| HU-09-01 | Log de auditoría inmutable | ISSUE-27 | `pendiente` | — | `repositories/audit_repo.py`, `models/audit_log.py` |
| HU-09-02 | Verificación de comprobante por QR | ISSUE-28 | `pendiente` | — | `api/v1/endpoints/verificar.py` |

---

## E-10 — Administración del Sistema

| HU | Descripción | Issue | Estado | Commit | Archivos principales |
|----|-------------|-------|--------|--------|----------------------|
| HU-10-01 | Panel superadmin con métricas | ISSUE (Fase 4) | `pendiente` | — | — |

---

## Issues de infraestructura sin HU directa

| Issue | Descripción | Estado | Commit |
|-------|-------------|--------|--------|
| ISSUE-01 | Setup FastAPI con arquitectura de capas | `pendiente` | — |
| ISSUE-02 | Modelos SQLAlchemy y migraciones Alembic | `pendiente` | — |
| ISSUE-03 | Capa Repository — implementación base | `pendiente` | — |
| ISSUE-29 | Setup frontend feature-based + Axios + TanStack Query | `pendiente` | — |
| ISSUE-36 | Setup mobile: navegación + SecureStore | `pendiente` | — |
| ISSUE-41 | Tests unitarios: auth y servicios core | `pendiente` | — |
| ISSUE-42 | Tests unitarios: natillera y pagos con fake repos | `pendiente` | — |
| ISSUE-43 | Tests de integración: endpoints API | `pendiente` | — |
| ISSUE-44 | Tests frontend con Vitest | `pendiente` | — |
| ISSUE-45 | GitHub Actions: backend tests CI | `pendiente` | — |
| ISSUE-46 | GitHub Actions: frontend build y lint CI | `pendiente` | — |
| ISSUE-47 | Documentación: API_DOCS, DEVELOPMENT, DEPLOYMENT | `pendiente` | — |

---

## Resumen de progreso

| Épica | Total HU | Completadas | Porcentaje |
|-------|----------|-------------|------------|
| E-01 Autenticación | 6 | 0 | 0% |
| E-02 Natilleras | 8 | 0 | 0% |
| E-03 Socios | 6 | 0 | 0% |
| E-04 Pagos | 5 | 0 | 0% |
| E-05 Saldos | 4 | 0 | 0% |
| E-06 Distribuciones | 2 | 0 | 0% |
| E-07 Notificaciones | 4 | 0 | 0% |
| E-08 Reportes | 3 | 0 | 0% |
| E-09 Seguridad | 2 | 0 | 0% |
| E-10 Superadmin | 1 | 0 | 0% |
| **Total** | **41** | **0** | **0%** |

> Última actualización: Junio 2026
