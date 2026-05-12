# CLIENT BRIEF — Natillera App

**Versión**: 2.0  
**Última actualización**: Junio 2026  
**Estado**: Aprobado para desarrollo

---

## Tabla de Contenido

1. [Contexto del Dominio](#1-contexto-del-dominio)
2. [Objetivos del Proyecto](#2-objetivos-del-proyecto)
3. [Actores del Sistema](#3-actores-del-sistema)
   - 3.1 [Administrador (Tesorero)](#31-administrador-tesorero)
   - 3.2 [Socio (Participante)](#32-socio-participante)
   - 3.3 [Sistema (Actor secundario)](#33-sistema-actor-secundario)
4. [Reglas de Negocio](#4-reglas-de-negocio)
5. [Épicas](#5-épicas)
6. [Historias de Usuario](#6-historias-de-usuario)
   - E-01 [Autenticación y Perfil](#e-01-autenticación-y-perfil)
   - E-02 [Gestión de Natilleras](#e-02-gestión-de-natilleras)
   - E-03 [Gestión de Socios](#e-03-gestión-de-socios)
   - E-04 [Aportes y Pagos](#e-04-aportes-y-pagos)
   - E-05 [Saldos y Estado de Cuenta](#e-05-saldos-y-estado-de-cuenta)
   - E-06 [Distribuciones](#e-06-distribuciones)
   - E-07 [Notificaciones y Alertas](#e-07-notificaciones-y-alertas)
   - E-08 [Reportes y Comprobantes](#e-08-reportes-y-comprobantes)
   - E-09 [Seguridad y Auditoría](#e-09-seguridad-y-auditoría)
   - E-10 [Administración del Sistema](#e-10-administración-del-sistema-superadmin)
7. [Requisitos No Funcionales](#7-requisitos-no-funcionales)
8. [Casos de Uso — Diagramas de Flujo Texto](#8-casos-de-uso--diagramas-de-flujo-texto)
9. [Backlog Priorizado por Fases](#9-backlog-priorizado-por-fases)
10. [Glosario](#10-glosario)
11. [Stakeholders](#11-stakeholders)
12. [Métricas de Éxito](#12-métricas-de-éxito)

---

## 1. Contexto del Dominio

Una **natillera** es un mecanismo de ahorro colectivo informal y tradicional en Colombia. Su funcionamiento base:

- Un grupo de personas (familiares, amigos, compañeros de trabajo) se asocia voluntariamente.
- Cada integrante (**socio**) aporta una suma fija de dinero de forma periódica (semanal, quincenal o mensual).
- Un **administrador (tesorero)** recolecta, custodia y registra los aportes.
- Al final del ciclo (normalmente diciembre) el fondo acumulado se **distribuye en partes iguales** entre los socios, o puede distribuirse parcialmente durante el año.
- El fondo puede generar **rentabilidad** si el tesorero otorga préstamos a socios con interés, o invierte el capital en instrumentos seguros.
- La confianza es el pilar central: el sistema es informal, no está regulado, y la reputación del tesorero es garantía.

**Natillera App** digitaliza este proceso eliminando el manejo de efectivo, la comunicación informal y los registros en papel, manteniendo la esencia del modelo.

---

## 2. Objetivos del Proyecto

| # | Objetivo | Indicador de éxito |
|---|----------|--------------------|
| 1 | Digitalizar el flujo completo de una natillera | 100% de operaciones sin papel |
| 2 | Garantizar transparencia total para todos los socios | Historial auditable en tiempo real |
| 3 | Reducir el trabajo manual del administrador | Cálculos y alertas 100% automáticos |
| 4 | Eliminar barreras geográficas | Socios pueden participar desde cualquier ciudad |
| 5 | Generar confianza mediante trazabilidad | Cada transacción tiene comprobante descargable |

---

## 3. Actores del Sistema

### 3.1 Administrador (Tesorero)
- Crea y configura natilleras.
- Gestiona la membresía (invitar, aprobar, suspender socios).
- Registra pagos recibidos y los confirma.
- Genera reportes, comprobantes y distribuciones.
- Es el único responsable legal y operativo del fondo.
- Puede ser socio activo a la vez.

### 3.2 Socio (Participante)
- Se une a una natillera mediante invitación del administrador.
- Realiza o registra sus aportes periódicos.
- Consulta su estado de cuenta, historial y saldo acumulado.
- Recibe notificaciones de pagos pendientes y distribuciones.
- No tiene visibilidad sobre la información privada de otros socios.

### 3.3 Sistema (Actor secundario)
- Calcula automáticamente saldos, mora e intereses.
- Envía notificaciones programadas (recordatorios, confirmaciones).
- Genera reportes y comprobantes.

---

## 4. Reglas de Negocio

Estas reglas son invariantes del dominio y deben respetarse en toda implementación:

| ID | Regla |
|----|-------|
| RN-01 | Una natillera tiene exactamente un administrador. No puede quedar sin administrador. |
| RN-02 | El monto de aporte por socio es fijo para todo el ciclo. No puede cambiar una vez iniciada. |
| RN-03 | La periodicidad (semanal/quincenal/mensual) es fija al crear la natillera. |
| RN-04 | Un socio en mora (≥1 período sin pagar) no puede recibir distribuciones parciales. |
| RN-05 | El administrador puede registrar pagos a nombre de socios (pago en efectivo presencial). |
| RN-06 | Un pago confirmado no puede eliminarse; solo puede marcarse como "revertido" con justificación. |
| RN-07 | La distribución final solo puede ejecutarse cuando el ciclo ha cerrado (fecha fin alcanzada). |
| RN-08 | Las distribuciones parciales (préstamos con interés) requieren aprobación explícita del administrador. |
| RN-09 | Un socio puede salir de la natillera solo si no tiene aportes pendientes y el administrador lo aprueba. |
| RN-10 | El saldo del fondo = suma de todos los aportes confirmados − distribuciones realizadas. |
| RN-11 | Los intereses generados por préstamos internos se suman al fondo y benefician a todos los socios por igual. |
| RN-12 | El administrador fija el número máximo de socios al crear la natillera. |

---

## 5. Épicas

| ID | Épica | Descripción |
|----|-------|-------------|
| E-01 | Autenticación y Perfil | Registro, login, gestión de cuenta y seguridad |
| E-02 | Gestión de Natilleras | Crear, configurar, cerrar y archivar natilleras |
| E-03 | Gestión de Socios | Invitar, aprobar, suspender y gestionar participantes |
| E-04 | Aportes y Pagos | Registro, confirmación y reverso de pagos |
| E-05 | Saldos y Estado de Cuenta | Consulta en tiempo real, cálculo automático |
| E-06 | Distribuciones | Distribución parcial (préstamos) y distribución final del fondo |
| E-07 | Notificaciones y Alertas | Recordatorios, confirmaciones y alertas de mora |
| E-08 | Reportes y Comprobantes | Generación de informes y documentos descargables |
| E-09 | Seguridad y Auditoría | Logs, 2FA, roles y trazabilidad |
| E-10 | Administración del Sistema | Panel de superadmin para gestión de la plataforma |

---

## 6. Historias de Usuario

El formato usado es:

> **Como** [actor], **quiero** [acción], **para** [beneficio].

Con **criterios de aceptación** en formato Gherkin (Given / When / Then).

---

### E-01: Autenticación y Perfil

---

#### HU-01-01: Registro de usuario

**Como** persona nueva, **quiero** registrarme con mi correo y contraseña, **para** poder acceder a la plataforma.

**Criterios de aceptación:**

```gherkin
Given el usuario no tiene cuenta
When envía nombre, email válido y contraseña (mín. 8 chars, 1 mayúscula, 1 número)
Then se crea la cuenta, se envía email de verificación y se redirige al dashboard

Given el email ya está registrado
When intenta registrarse con el mismo email
Then recibe error "Este correo ya está registrado"

Given la contraseña no cumple los requisitos
When intenta registrarse
Then recibe mensaje descriptivo del requisito incumplido
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-01-02: Inicio de sesión

**Como** usuario registrado, **quiero** iniciar sesión con email y contraseña, **para** acceder a mis natilleras.

**Criterios de aceptación:**

```gherkin
Given credenciales correctas
When el usuario hace login
Then recibe un JWT de acceso (15 min) y un refresh token (7 días) y accede al dashboard

Given contraseña incorrecta
When intenta hacer login
Then recibe error genérico "Credenciales incorrectas" (sin especificar cuál falló)

Given 5 intentos fallidos consecutivos
When intenta hacer login nuevamente
Then la cuenta se bloquea 15 minutos y se notifica al usuario por email
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-01-03: Cierre de sesión

**Como** usuario autenticado, **quiero** cerrar sesión, **para** proteger mi cuenta en dispositivos compartidos.

**Criterios de aceptación:**

```gherkin
Given el usuario está autenticado
When hace logout
Then el refresh token se invalida en base de datos y se limpia el almacenamiento local
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-01-04: Recuperación de contraseña

**Como** usuario que olvidó su contraseña, **quiero** recuperarla por correo, **para** recuperar el acceso.

**Criterios de aceptación:**

```gherkin
Given email registrado en el sistema
When solicita recuperación
Then recibe email con enlace de un solo uso válido por 1 hora

Given enlace válido
When ingresa nueva contraseña
Then la contraseña se actualiza y todos los tokens activos se invalidan

Given enlace expirado
When intenta usarlo
Then recibe error "Enlace expirado, solicita uno nuevo"
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-01-05: Editar perfil

**Como** usuario autenticado, **quiero** actualizar mi nombre y foto de perfil, **para** que los demás socios me identifiquen.

**Criterios de aceptación:**

```gherkin
Given usuario autenticado
When actualiza nombre o foto
Then los cambios se reflejan inmediatamente en todas las natilleras donde participa

Given imagen mayor a 2MB o formato no permitido
When intenta subir la foto
Then recibe error con formatos aceptados (JPG, PNG, WEBP)
```

**Prioridad**: Media | **Fase**: MVP

---

#### HU-01-06: Autenticación de dos factores (2FA)

**Como** usuario, **quiero** activar 2FA, **para** añadir una capa de seguridad adicional a mi cuenta.

**Criterios de aceptación:**

```gherkin
Given usuario con 2FA habilitado
When hace login con credenciales correctas
Then se le solicita el código TOTP antes de acceder

Given código TOTP inválido o expirado
When lo ingresa
Then acceso denegado con mensaje claro
```

**Prioridad**: Media | **Fase**: Fase 4

---

### E-02: Gestión de Natilleras

---

#### HU-02-01: Crear natillera

**Como** administrador, **quiero** crear una natillera configurando sus parámetros, **para** iniciar un ciclo de ahorro grupal.

**Criterios de aceptación:**

```gherkin
Given usuario autenticado
When crea una natillera con: nombre, monto por aporte, periodicidad, fecha inicio, fecha fin, máximo de socios
Then la natillera queda en estado "Configuración" y el creador queda como administrador

Given fecha fin menor a fecha inicio
When intenta guardar
Then recibe error de validación

Given periodicidad semanal y duración de 1 año
When se crea la natillera
Then el sistema calcula automáticamente el calendario de 52 períodos de pago

Given monto de aporte = $0
When intenta guardar
Then recibe error "El monto debe ser mayor a cero"
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-02-02: Ver mis natilleras

**Como** usuario, **quiero** ver todas las natilleras en las que participo (como admin o socio), **para** tener una vista general de mis ahorros.

**Criterios de aceptación:**

```gherkin
Given usuario con múltiples natilleras
When accede al dashboard
Then ve tarjetas con: nombre, rol (admin/socio), estado, saldo acumulado personal y siguiente fecha de pago

Given usuario sin natilleras
When accede al dashboard
Then ve un estado vacío con CTA para crear o unirse a una natillera
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-02-03: Ver detalle de natillera (administrador)

**Como** administrador, **quiero** ver el estado completo de mi natillera, **para** tomar decisiones informadas.

**Criterios de aceptación:**

```gherkin
Given administrador en su natillera
When accede al detalle
Then ve: saldo total del fondo, lista de socios con estado de pago del período actual, socios en mora, próxima fecha de corte y gráfico de aportes acumulados
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-02-04: Ver detalle de natillera (socio)

**Como** socio, **quiero** ver mi estado en la natillera, **para** saber cuánto he aportado y cuánto me corresponde.

**Criterios de aceptación:**

```gherkin
Given socio activo en una natillera
When accede al detalle
Then ve: su saldo acumulado personal, historial de sus propios pagos, próxima fecha de pago y monto, y estado (al día / en mora)
Then NO ve información financiera detallada de otros socios individuales
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-02-05: Editar configuración de natillera

**Como** administrador, **quiero** editar el nombre y descripción de la natillera, **para** mantenerla actualizada.

**Criterios de aceptación:**

```gherkin
Given natillera en estado "Activa"
When administrador edita nombre o descripción
Then los cambios se guardan y todos los socios ven el cambio inmediatamente

Given natillera activa
When administrador intenta cambiar el monto de aporte o la periodicidad
Then la operación es rechazada con mensaje "No se pueden cambiar parámetros financieros de una natillera activa"
```

**Prioridad**: Media | **Fase**: MVP

---

#### HU-02-06: Activar natillera

**Como** administrador, **quiero** activar la natillera cuando tenga al menos 2 socios confirmados, **para** iniciar formalmente el ciclo.

**Criterios de aceptación:**

```gherkin
Given natillera con mínimo 2 socios activos
When administrador la activa
Then el estado cambia a "Activa", se genera el calendario de pagos y se notifica a todos los socios

Given natillera con menos de 2 socios
When administrador intenta activarla
Then recibe error "Se requieren al menos 2 socios para activar"
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-02-07: Cerrar natillera

**Como** administrador, **quiero** cerrar la natillera al finalizar el ciclo, **para** proceder a la distribución final.

**Criterios de aceptación:**

```gherkin
Given natillera activa y fecha fin alcanzada
When administrador inicia el cierre
Then el estado cambia a "En cierre", no se aceptan más aportes y se habilita la distribución final

Given natillera activa con socios en mora al momento del cierre
When administrador inicia cierre
Then recibe advertencia con lista de socios en mora y debe confirmar explícitamente el cierre
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-02-08: Archivar natillera

**Como** administrador, **quiero** archivar natilleras cerradas y con distribución completada, **para** mantener organizado mi historial.

**Criterios de aceptación:**

```gherkin
Given natillera en estado "Cerrada" con distribución final completada
When administrador la archiva
Then el estado cambia a "Archivada", sigue siendo consultable en modo lectura pero no aparece en el dashboard principal
```

**Prioridad**: Baja | **Fase**: Fase 2

---

### E-03: Gestión de Socios

---

#### HU-03-01: Invitar socio por email

**Como** administrador, **quiero** invitar personas por correo electrónico, **para** que se unan a mi natillera.

**Criterios de aceptación:**

```gherkin
Given natillera en estado "Configuración" o "Activa"
When administrador ingresa un email y envía invitación
Then el invitado recibe un email con enlace de invitación válido por 48 horas

Given natillera con número máximo de socios alcanzado
When administrador intenta invitar a alguien más
Then recibe error "Cupo máximo de socios alcanzado"

Given el email invitado no tiene cuenta
When el invitado acepta la invitación
Then se le redirige al flujo de registro y al completarlo queda unido a la natillera
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-03-02: Aceptar invitación

**Como** persona invitada, **quiero** aceptar la invitación, **para** unirme a la natillera.

**Criterios de aceptación:**

```gherkin
Given enlace de invitación válido y vigente
When el invitado hace clic y acepta
Then queda como socio activo en la natillera y puede ver su estado de cuenta

Given enlace expirado (más de 48 horas)
When el invitado hace clic
Then recibe mensaje "Invitación expirada, pide al administrador una nueva"
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-03-03: Ver lista de socios (administrador)

**Como** administrador, **quiero** ver la lista completa de socios con su estado de pago, **para** gestionar el grupo.

**Criterios de aceptación:**

```gherkin
Given administrador en su natillera
When accede a la sección de socios
Then ve para cada socio: nombre, email, fecha de ingreso, estado del período actual (pagado / pendiente / en mora), total aportado
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-03-04: Suspender socio

**Como** administrador, **quiero** suspender temporalmente a un socio, **para** que no pueda realizar aportes mientras se resuelve una situación.

**Criterios de aceptación:**

```gherkin
Given socio activo
When administrador lo suspende con una razón obligatoria
Then el socio recibe notificación, no puede realizar aportes y su período actual queda en "suspendido"

Given socio suspendido
When administrador lo reactiva
Then el socio vuelve a estado activo y puede retomar aportes
```

**Prioridad**: Media | **Fase**: MVP

---

#### HU-03-05: Eliminar socio

**Como** administrador, **quiero** eliminar a un socio que no ha hecho ningún aporte, **para** liberar su cupo.

**Criterios de aceptación:**

```gherkin
Given socio sin ningún aporte registrado
When administrador lo elimina
Then el socio es removido, recibe notificación y el cupo queda disponible

Given socio con al menos un aporte registrado
When administrador intenta eliminarlo
Then la operación es rechazada con mensaje "El socio tiene aportes registrados, usa 'Suspender' en su lugar"
```

**Prioridad**: Media | **Fase**: MVP

---

#### HU-03-06: Transferir administración

**Como** administrador, **quiero** transferir el rol de administrador a otro socio, **para** delegar la gestión.

**Criterios de aceptación:**

```gherkin
Given administrador y socio activo destino
When administrador confirma la transferencia (requiere contraseña)
Then el socio destino pasa a ser administrador, el anterior queda como socio regular y ambos reciben notificación
```

**Prioridad**: Media | **Fase**: Fase 2

---

### E-04: Aportes y Pagos

---

#### HU-04-01: Registrar aporte de socio (por administrador)

**Como** administrador, **quiero** registrar manualmente el pago en efectivo de un socio, **para** reflejar aportes presenciales.

**Criterios de aceptación:**

```gherkin
Given socio activo con período pendiente
When administrador selecciona el socio, el período y confirma el monto
Then el aporte queda registrado como "Confirmado", el saldo del fondo se actualiza y el socio recibe notificación con comprobante

Given monto ingresado diferente al monto fijo de la natillera
When administrador intenta confirmar
Then recibe advertencia "El monto no corresponde al aporte estándar" y debe confirmar explícitamente
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-04-02: Registrar pago propio (por socio)

**Como** socio, **quiero** registrar mi pago indicando el método y adjuntando comprobante, **para** notificar al administrador que pagué.

**Criterios de aceptación:**

```gherkin
Given socio con período pendiente
When socio registra su pago con: método (transferencia, efectivo, app), referencia opcional y foto del comprobante
Then el aporte queda en estado "Pendiente de confirmación" y el administrador recibe notificación para validarlo

Given socio que ya pagó el período actual
When intenta registrar otro pago para el mismo período
Then recibe error "Ya existe un pago registrado para este período"
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-04-03: Confirmar pago registrado por socio

**Como** administrador, **quiero** confirmar o rechazar un pago enviado por un socio, **para** mantener el control del fondo.

**Criterios de aceptación:**

```gherkin
Given pago en estado "Pendiente de confirmación"
When administrador lo aprueba
Then el estado cambia a "Confirmado", el saldo del fondo se actualiza y el socio recibe notificación

Given pago en estado "Pendiente de confirmación"
When administrador lo rechaza con razón obligatoria
Then el estado cambia a "Rechazado", el socio recibe notificación con la razón y el período vuelve a "Pendiente"
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-04-04: Revertir pago

**Como** administrador, **quiero** revertir un pago confirmado por error, **para** corregir registros incorrectos.

**Criterios de aceptación:**

```gherkin
Given pago en estado "Confirmado"
When administrador lo revierte con justificación obligatoria
Then el pago queda en estado "Revertido" (no se elimina), el saldo del fondo se ajusta, el período vuelve a "Pendiente" y queda registrado en el log de auditoría con usuario, fecha y razón

Given intento de revertir un pago con más de 72 horas
When administrador intenta revertirlo directamente
Then recibe advertencia de que el plazo estándar superó, debe confirmar con contraseña
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-04-05: Pago por pasarela digital

**Como** socio, **quiero** pagar directamente desde la app con tarjeta o PSE, **para** no depender del efectivo ni transferencias manuales.

**Criterios de aceptación:**

```gherkin
Given socio con período pendiente
When inicia pago por pasarela (Stripe)
Then es redirigido al formulario de pago seguro; al completar, el pago queda automáticamente "Confirmado" sin intervención del administrador

Given fallo en la pasarela de pago
When ocurre el error
Then el socio recibe mensaje de error descriptivo, el período sigue "Pendiente" y no se crea ningún registro de pago
```

**Prioridad**: Alta | **Fase**: Fase 2

---

### E-05: Saldos y Estado de Cuenta

---

#### HU-05-01: Consultar saldo del fondo (administrador)

**Como** administrador, **quiero** ver el saldo total del fondo en tiempo real, **para** conocer el estado financiero de la natillera.

**Criterios de aceptación:**

```gherkin
Given natillera activa
When administrador accede al dashboard
Then ve: saldo total del fondo, aportes recibidos en el período actual, aportes pendientes del período actual, total distribuido a la fecha
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-05-02: Consultar mi estado de cuenta (socio)

**Como** socio, **quiero** ver mi estado de cuenta personal, **para** saber cuánto he aportado y qué debo.

**Criterios de aceptación:**

```gherkin
Given socio activo
When accede a su estado de cuenta
Then ve: total aportado desde el inicio del ciclo, períodos pagados y pendientes, monto del próximo aporte y fecha límite, y si está en mora: cantidad de períodos y monto total en mora
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-05-03: Historial de transacciones

**Como** usuario (admin o socio), **quiero** ver el historial completo de mis transacciones, **para** tener trazabilidad de mis movimientos.

**Criterios de aceptación:**

```gherkin
Given usuario autenticado
When accede al historial
Then ve lista paginada (20 por página) con: fecha, descripción, monto, estado, y referencia; con filtros por rango de fecha, estado y tipo

Given administrador
When accede al historial de la natillera
Then ve el historial de TODOS los socios (el socio solo ve el suyo)
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-05-04: Alerta de mora

**Como** sistema, **quiero** marcar automáticamente a socios en mora, **para** que el administrador tome acción.

**Criterios de aceptación:**

```gherkin
Given socio con período de pago vencido hace más de 3 días
When el sistema ejecuta el job nocturno
Then el socio es marcado en mora, el administrador recibe notificación y el socio recibe alerta de mora
```

**Prioridad**: Alta | **Fase**: MVP

---

### E-06: Distribuciones

---

#### HU-06-01: Distribución parcial — préstamo interno

**Como** administrador, **quiero** otorgar un préstamo a un socio usando fondos de la natillera, **para** que el capital no quede ocioso y genere rentabilidad.

**Criterios de aceptación:**

```gherkin
Given natillera activa, socio sin mora y fondos disponibles
When administrador crea el préstamo con: monto, tasa de interés mensual y plazo (número de períodos de pago)
Then el préstamo queda registrado, el saldo del fondo se reduce, el socio recibe notificación con el plan de pagos

Given monto del préstamo mayor al saldo disponible del fondo
When administrador intenta crearlo
Then recibe error "Fondos insuficientes en el fondo"

Given socio en mora
When administrador intenta asignarle un préstamo
Then recibe bloqueo según RN-04
```

**Prioridad**: Media | **Fase**: Fase 3

---

#### HU-06-02: Distribución final del fondo

**Como** administrador, **quiero** ejecutar la distribución final al cerrar el ciclo, **para** repartir equitativamente el fondo acumulado más rentabilidad.

**Criterios de aceptación:**

```gherkin
Given natillera en estado "En cierre"
When administrador ejecuta la distribución final
Then el sistema calcula: monto total del fondo ÷ número de socios activos (excluyendo socios con mora no saldada según configuración), muestra vista previa antes de confirmar

Given administrador confirma la distribución
When la aprueba
Then cada socio recibe notificación con su monto correspondiente, queda registrado el comprobante de distribución y la natillera pasa a estado "Cerrada"
```

**Prioridad**: Alta | **Fase**: MVP (cálculo manual) / Fase 3 (automático con rentabilidad)

---

### E-07: Notificaciones y Alertas

---

#### HU-07-01: Recordatorio de pago próximo

**Como** socio, **quiero** recibir recordatorio antes de la fecha límite de pago, **para** no incurrir en mora.

**Criterios de aceptación:**

```gherkin
Given socio con pago pendiente
When faltan 3 días para la fecha límite del período
Then recibe notificación push (móvil) y email con: monto, fecha límite y enlace directo al pago

Given socio que ya pagó el período
When llega la fecha del recordatorio
Then NO recibe notificación
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-07-02: Confirmación de pago recibido

**Como** socio, **quiero** recibir confirmación cuando mi pago sea registrado o confirmado, **para** tener tranquilidad.

**Criterios de aceptación:**

```gherkin
Given pago confirmado por administrador o por pasarela
When el estado cambia a "Confirmado"
Then socio recibe notificación push y email con: monto, período, saldo actualizado y enlace al comprobante
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-07-03: Alerta de pago rechazado

**Como** socio, **quiero** recibir alerta si mi pago fue rechazado, **para** volver a enviarlo.

**Criterios de aceptación:**

```gherkin
Given pago rechazado por administrador
When el estado cambia a "Rechazado"
Then socio recibe notificación con la razón del rechazo y el botón de acción para registrar un nuevo pago
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-07-04: Configurar preferencias de notificación

**Como** usuario, **quiero** configurar qué notificaciones recibo y por qué canal, **para** no recibir spam.

**Criterios de aceptación:**

```gherkin
Given usuario autenticado
When accede a preferencias de notificación
Then puede activar/desactivar por tipo (recordatorios, confirmaciones, alertas) y por canal (email, push) de forma independiente

Given notificación crítica (mora, distribución)
Regardless de las preferencias del usuario
Then siempre se envía (no es desactivable)
```

**Prioridad**: Media | **Fase**: Fase 2

---

### E-08: Reportes y Comprobantes

---

#### HU-08-01: Descargar comprobante de pago

**Como** socio o administrador, **quiero** descargar el comprobante de un pago, **para** tener respaldo físico.

**Criterios de aceptación:**

```gherkin
Given pago en estado "Confirmado"
When usuario solicita el comprobante
Then se genera PDF con: nombre natillera, nombre socio, monto, período, fecha de confirmación, número de referencia único y QR de verificación
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-08-02: Reporte de estado de natillera

**Como** administrador, **quiero** exportar el estado completo de la natillera, **para** compartirlo con los socios o revisarlo offline.

**Criterios de aceptación:**

```gherkin
Given natillera activa o cerrada
When administrador genera el reporte
Then puede elegir formato (PDF o Excel) y descarga: lista de socios, historial de aportes, saldo del fondo, socios en mora y distribuciones realizadas
```

**Prioridad**: Media | **Fase**: Fase 2

---

#### HU-08-03: Reporte personal del socio

**Como** socio, **quiero** exportar mi historial de aportes, **para** tener un registro personal.

**Criterios de aceptación:**

```gherkin
Given socio activo o en natillera cerrada
When solicita su reporte
Then descarga PDF con su historial completo de aportes, montos, fechas y estado
```

**Prioridad**: Media | **Fase**: Fase 2

---

### E-09: Seguridad y Auditoría

---

#### HU-09-01: Log de auditoría

**Como** administrador de plataforma, **quiero** que todas las operaciones críticas queden registradas, **para** garantizar trazabilidad ante disputas.

**Criterios de aceptación:**

```gherkin
Given cualquier operación crítica: confirmar pago, revertir pago, cambiar administrador, crear/cerrar natillera, realizar distribución
When se ejecuta la operación
Then queda registrada en el log con: usuario ejecutor, acción, timestamp, IP, datos anteriores y nuevos (diff)
Then el log es inmutable: no puede editarse ni eliminarse
```

**Prioridad**: Alta | **Fase**: MVP

---

#### HU-09-02: Verificar integridad de comprobante

**Como** cualquier persona, **quiero** verificar la autenticidad de un comprobante mediante su QR, **para** detectar documentos falsos.

**Criterios de aceptación:**

```gherkin
Given QR en un comprobante de pago
When se escanea el QR
Then se abre una URL pública que muestra: válido/inválido, y si es válido: natillera, socio, monto, fecha y estado actual
```

**Prioridad**: Media | **Fase**: Fase 4

---

### E-10: Administración del Sistema (Superadmin)

---

#### HU-10-01: Panel de administración de plataforma

**Como** superadmin, **quiero** ver métricas globales de uso de la plataforma, **para** monitorear la salud del negocio.

**Criterios de aceptación:**

```gherkin
Given superadmin autenticado
When accede al panel
Then ve: total de usuarios, natilleras activas, capital total gestionado, transacciones del mes, y alertas del sistema
```

**Prioridad**: Media | **Fase**: Fase 4

---

## 7. Requisitos No Funcionales

| ID | Categoría | Requisito | Métrica |
|----|-----------|-----------|---------|
| RNF-01 | Rendimiento | Tiempo de respuesta de API en operaciones normales | < 300ms (p95) |
| RNF-02 | Rendimiento | Tiempo de carga inicial de la app web | < 2s en conexión 4G |
| RNF-03 | Disponibilidad | Uptime del backend | ≥ 99.5% mensual |
| RNF-04 | Seguridad | Contraseñas almacenadas con hash | bcrypt, cost ≥ 12 |
| RNF-05 | Seguridad | Comunicaciones cifradas | HTTPS/TLS 1.2+ en todos los endpoints |
| RNF-06 | Seguridad | Tokens JWT | Access token: 15 min, Refresh: 7 días con rotación |
| RNF-07 | Seguridad | Datos financieros sensibles en BD | Cifrados con AES-256 |
| RNF-08 | Escalabilidad | Capacidad mínima inicial | 1,000 natilleras, 10,000 usuarios |
| RNF-09 | Usabilidad | Flujo de pago completado por usuarios nuevos sin ayuda | ≥ 90% en primer intento |
| RNF-10 | Auditabilidad | Registros de log deben conservarse | Mínimo 3 años |
| RNF-11 | Cumplimiento | Manejo de datos personales | Conforme a Ley 1581 de 2012 (Colombia) |
| RNF-12 | Portabilidad | App móvil | Funcional en Android 8+ e iOS 13+ |

---

## 8. Casos de Uso — Diagramas de Flujo Texto

### CU-01: Ciclo completo de vida de una natillera

```
[Admin] Crea natillera (estado: CONFIGURACION)
    → Invita socios (estado: CONFIGURACION)
    → Socios aceptan invitaciones
    → Admin activa natillera (estado: ACTIVA)
        → [Sistema] Genera calendario de períodos
        → [Sistema] Notifica a todos los socios
    → [Ciclo por período]
        → [Sistema] Envía recordatorio 3 días antes
        → [Socio] Registra pago (estado pago: PENDIENTE_CONFIRMACION)
        → [Admin] Confirma pago (estado pago: CONFIRMADO)
        → [Sistema] Notifica confirmación al socio
    → [Al alcanzar fecha fin]
        → [Admin] Inicia cierre (estado: EN_CIERRE)
        → [Admin] Ejecuta distribución final
        → [Sistema] Notifica a cada socio su monto
        → (estado: CERRADA)
    → [Admin] Archiva natillera (estado: ARCHIVADA)
```

### CU-02: Flujo de pago con rechazo

```
[Socio] Registra pago + adjunta comprobante
    → (estado pago: PENDIENTE_CONFIRMACION)
    → [Admin] Revisa comprobante
        → [Admin] Rechaza con razón
            → (estado pago: RECHAZADO)
            → [Sistema] Notifica al socio con razón
            → [Socio] Corrige y registra nuevo pago
        → [Admin] Aprueba
            → (estado pago: CONFIRMADO)
            → [Sistema] Notifica y genera comprobante
```

### CU-03: Flujo de mora y resolución

```
[Sistema] (job nocturno) Detecta período vencido > 3 días sin pago
    → Marca socio como EN_MORA
    → Notifica al admin y al socio
    → [Socio en mora] NO puede recibir distribuciones parciales (RN-04)
    → [Socio] Paga el período en mora
    → [Admin] Confirma pago
    → Estado de mora se levanta automáticamente
```

---

## 9. Backlog Priorizado por Fases

### Fase 1 — MVP (Semanas 1-5)

| Historia | Descripción |
|----------|-------------|
| HU-01-01 a 01-05 | Autenticación y perfil completo |
| HU-02-01 a 02-07 | Gestión completa de natilleras |
| HU-03-01 a 03-05 | Gestión de socios |
| HU-04-01 a 04-04 | Aportes y pagos manuales |
| HU-05-01 a 05-04 | Saldos, historial y mora |
| HU-06-02 | Distribución final (cálculo simple) |
| HU-07-01 a 07-03 | Notificaciones básicas (email) |
| HU-08-01 | Comprobante de pago en PDF |
| HU-09-01 | Log de auditoría |

### Fase 2 — Transacciones digitales

| Historia | Descripción |
|----------|-------------|
| HU-04-05 | Pago por pasarela (Stripe) |
| HU-03-06 | Transferencia de administración |
| HU-07-04 | Preferencias de notificación |
| HU-08-02 a 08-03 | Reportes exportables PDF/Excel |
| HU-02-08 | Archivar natilleras |

### Fase 3 — Rentabilidad

| Historia | Descripción |
|----------|-------------|
| HU-06-01 | Préstamos internos con interés |
| HU-06-02 | Distribución final con rentabilidad incluida |

### Fase 4 — Seguridad avanzada

| Historia | Descripción |
|----------|-------------|
| HU-01-06 | Autenticación 2FA |
| HU-09-02 | Verificación de comprobante por QR |
| HU-10-01 | Panel superadmin |

---

## 10. Glosario

| Término | Definición |
|---------|------------|
| **Natillera** | Grupo de ahorro colectivo con ciclo definido, monto fijo y periodicidad establecida |
| **Período** | Unidad de tiempo entre aportes (semana, quincena o mes) |
| **Ciclo** | Duración total de la natillera desde activación hasta cierre |
| **Tesorero / Administrador** | Usuario responsable de gestionar el fondo |
| **Socio** | Participante activo en la natillera |
| **Mora** | Estado de un socio que no ha pagado uno o más períodos vencidos |
| **Distribución** | Reparto del fondo acumulado entre los socios |
| **Distribución parcial** | Préstamo con interés otorgado a un socio antes del cierre del ciclo |
| **Distribución final** | Reparto del fondo total + rentabilidad al cierre del ciclo |
| **Comprobante** | Documento PDF firmado digitalmente que certifica una transacción |
| **Fondo** | Capital total acumulado en la natillera: aportes confirmados − distribuciones |

---

## 11. Stakeholders

| Rol | Responsabilidad |
|-----|-----------------|
| Product Owner | Priorizar backlog, validar criterios de aceptación |
| Backend Dev | API, modelos de BD, lógica de negocio, seguridad |
| Frontend Dev | Web UI/UX, integración con API |
| Mobile Dev | App React Native, notificaciones push |
| QA | Validar criterios de aceptación, pruebas de regresión |

---

## 12. Métricas de Éxito

| Métrica | Target MVP | Target 6 meses |
|---------|-----------|-----------------|
| Usuarios registrados | 100 | 5,000 |
| Natilleras activas | 20 | 500 |
| Capital gestionado | $20,000 COP | $500,000 COP |
| Transacciones/mes | 200 | 10,000 |
| Retención a 30 días | 70% | 80% |
| Tasa de mora promedio | < 20% | < 10% |

---

**Documento Versión**: 2.0  
**Última actualización**: Junio 2026  
**Estado**: Aprobado para desarrollo MVP
