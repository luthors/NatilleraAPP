# 📋 Issues del Proyecto Natillera App

## Guía de Prioridades y Complejidad

- **Complejidad**: 0.5 (trivial) → 1.0 (simple) → 2.0 (media) → 3.0+ (compleja)
- **Prioridad**: P0 (crítica) → P1 (alta) → P2 (media) → P3 (baja)

---

## 🔐 BACKEND - Autenticación y Seguridad (P0)

### Issue 1: Configurar FastAPI base con CORS y estructura inicial
**Complejidad**: 1.0  
**Labels**: backend, setup, documentation  
**Descripción**:
```
Tareas:
- [ ] Crear main.py con FastAPI app
- [ ] Configurar CORS para localhost:3000, localhost:5173
- [ ] Setup logging
- [ ] Crear database.py con SQLAlchemy
- [ ] Estructura básica de carpetas (/models, /schemas, /services)
- [ ] README en backend/ con instrucciones setup

Criterios de aceptación:
- uvicorn app.main:app --reload funciona sin errores
- GET /docs muestra Swagger UI
- CORS headers configurados
```

### Issue 2: Implementar modelo User y schema Pydantic
**Complejidad**: 1.0  
**Labels**: backend, database, models  
**Descripción**:
```
Tareas:
- [ ] Crear models/user.py con SQLAlchemy
- [ ] Campos: id, email, password_hash, full_name, phone, created_at, is_active
- [ ] Crear schemas/user.py con Pydantic
- [ ] UserCreate, UserResponse, UserUpdate
- [ ] Agregar validaciones email y password strength

Criterios de aceptación:
- Email validation funciona
- Password requirements: min 8 chars, 1 uppercase, 1 digit
- Modelo se crea en DB sin errores
```

### Issue 3: Implementar autenticación JWT (login/register)
**Complejidad**: 2.0  
**Labels**: backend, auth, security  
**Descripción**:
```
Tareas:
- [ ] Crear security.py con funciones:
  - hash_password()
  - verify_password()
  - create_access_token()
  - create_refresh_token()
  - decode_token()
- [ ] Crear endpoints/auth.py:
  - POST /auth/register
  - POST /auth/login
  - POST /auth/refresh
- [ ] Crear dependencia get_current_user()
- [ ] Implementar JWT con 15 min access, 7 días refresh

Criterios de aceptación:
- POST /auth/register retorna JWT tokens
- POST /auth/login valida credenciales
- Access token expira en 15 min
- Refresh token extiende sesión
- Endpoints protegidos retornan 401 sin token
```

---

## 📊 BACKEND - Base de Datos (P0)

### Issue 4: Crear modelos de base de datos (Natillera, Participant, Transaction)
**Complejidad**: 2.0  
**Labels**: backend, database, models  
**Descripción**:
```
Tareas:
- [ ] models/natillera.py:
  - id, name, description, admin_id (FK)
  - total_amount, period_amount
  - periodicidad (semanal/quincenal/mensual)
  - start_date, end_date, status
  - created_at, updated_at
- [ ] models/participant.py:
  - natillera_id (FK), user_id (FK)
  - amount_per_period, status, joined_at, removed_at
- [ ] models/transaction.py:
  - natillera_id (FK), participant_id (FK)
  - amount, type (payment/interest), status
  - payment_method, transaction_date
- [ ] Crear índices en:
  - natillera_id, user_id, created_at

Criterios de aceptación:
- Modelos crean tablas sin errores
- Foreign keys configuradas
- Índices optimizan queries comunes
```

### Issue 5: Crear Alembic migrations iniciales
**Complejidad**: 1.0  
**Labels**: backend, database, devops  
**Descripción**:
```
Tareas:
- [ ] Inicializar Alembic: alembic init migrations
- [ ] Configurar alembic.ini con DATABASE_URL
- [ ] Crear migrations/env.py para auto-generate
- [ ] Primera migración: alembic revision --autogenerate -m "init"
- [ ] Test: alembic upgrade head

Criterios de aceptación:
- Tablas se crean correctamente
- alembic downgrade funciona
- alembic upgrade head es idempotente
```

---

## 🔄 BACKEND - APIs Principales (P0)

### Issue 6: Crear endpoints GET/POST para Natilleras (CRUD básico)
**Complejidad**: 1.0  
**Labels**: backend, api, endpoints  
**Descripción**:
```
Tareas:
- [ ] endpoints/natilleras.py:
  - GET /natilleras (listar del user)
  - POST /natilleras (crear - admin)
  - GET /natilleras/{id} (detail)
  - PUT /natilleras/{id} (edit)
  - DELETE /natilleras/{id} (delete - admin)
- [ ] Agregar schemas: NatilleraCreate, NatilleraResponse, NatilleraUpdate
- [ ] Validaciones:
  - amount > 0
  - period_amount >= 0
  - end_date > start_date

Criterios de aceptación:
- Todos los endpoints funcionan
- Validaciones rechaza datos inválidos
- Autenticación required en todos
- Query filters: ?status=active
```

### Issue 7: Crear endpoints para Participants (agregar/remover socios)
**Complejidad**: 1.0  
**Labels**: backend, api, endpoints  
**Descripción**:
```
Tareas:
- [ ] endpoints/participants.py:
  - GET /natilleras/{id}/participants
  - POST /natilleras/{id}/participants (invite)
  - DELETE /natilleras/{id}/participants/{pid} (remove)
- [ ] Esquemas: ParticipantCreate, ParticipantResponse
- [ ] Validaciones:
  - Solo admin puede agregar
  - No duplicados
  - User existe antes de agregar

Criterios de aceptación:
- Admin puede invitar múltiples users
- Socios se listan correctamente
- Remover socio funciona
- Notificaciones (opcional MVP)
```

### Issue 8: Crear endpoints para Transactions (registrar pagos)
**Complejidad**: 1.5  
**Labels**: backend, api, endpoints  
**Descripción**:
```
Tareas:
- [ ] endpoints/transactions.py:
  - GET /transactions (con filtros)
  - POST /transactions (create payment)
  - GET /transactions/{id}
  - PUT /transactions/{id} (admin confirma pago)
- [ ] Schemas: TransactionCreate, TransactionResponse
- [ ] Lógica:
  - Validar que participant existe en natillera
  - Actualizar balance tras confirmación
  - Grabar payment_method
- [ ] Filtros soportados:
  - ?natillera_id=X
  - ?status=pending
  - ?date_from=YYYY-MM-DD

Criterios de aceptación:
- Crear transacción registra en DB
- Balance se actualiza
- Status pending→done funciona
- Filtros retornan datos correctos
```

---

## 👤 BACKEND - User Profile

### Issue 9: Crear endpoint GET/PUT para perfil de usuario
**Complejidad**: 0.5  
**Labels**: backend, api, endpoints  
**Descripción**:
```
Tareas:
- [ ] GET /users/me (obtener perfil actual)
- [ ] PUT /users/{id} (editar email, name, phone)
- [ ] Validaciones: no cambiar email si ya existe
- [ ] Response no retorna password_hash

Criterios de aceptación:
- GET /users/me retorna usuario autenticado
- PUT valida email único
- Password no se retorna
```

---

## 📈 BACKEND - Reportes y Distribuciones (P1)

### Issue 10: Crear servicio de cálculo de balances y saldos
**Complejidad**: 1.5  
**Labels**: backend, business-logic, services  
**Descripción**:
```
Tareas:
- [ ] services/natillera.py:
  - get_balance(natillera_id, participant_id)
  - get_total_collected(natillera_id)
  - get_expected_amount(natillera_id) // (monto x periodos)
  - calculate_distribution(natillera_id)
- [ ] Lógica:
  - Sum transacciones confirmadas
  - Calcular deuda si no pagó
  - Retornar por socio

Criterios de aceptación:
- Cálculos son precisos
- Funciones retornan decimales correctos
- Maneja edge cases (0 transacciones)
```

### Issue 11: Crear endpoint de reportes (balance, summary, export)
**Complejidad**: 2.0  
**Labels**: backend, api, reports  
**Descripción**:
```
Tareas:
- [ ] endpoints/reports.py:
  - GET /natilleras/{id}/reports/balance
  - GET /natilleras/{id}/reports/summary
  - GET /natilleras/{id}/reports/export (PDF - opcional)
- [ ] Respuestas:
  - Balance: {total, por_socio: [{name, amount, pago}]}
  - Summary: {total_recaudado, total_esperado, progreso}
  - Export: descargable PDF

Criterios de aceptación:
- Reportes muestran datos correctos
- Solo admin puede ver reportes
- PDF generado correctamente (opcional)
```

### Issue 12: Crear endpoint para distribución de fondos
**Complejidad**: 2.0  
**Labels**: backend, api, business-logic  
**Descripción**:
```
Tareas:
- [ ] POST /natilleras/{id}/distribute
- [ ] Lógica:
  - Validar natillera está en período de distribución
  - Calcular por cada socio:
    - Aporte total
    - Intereses (si aplica)
    - Deudas (si aplica)
  - Crear registros DISTRIBUTION
  - Enviar notificaciones/emails
- [ ] schemas: DistributionResponse

Criterios de aceptación:
- Distribución calcula correctamente
- Socios reciben su corresponde
- Registros quedan en auditoría
- Solo admin puede distribuir
```

---

## 🧪 BACKEND - Testing (P2)

### Issue 13: Crear tests unitarios para autenticación
**Complejidad**: 1.0  
**Labels**: backend, testing, ci-cd  
**Descripción**:
```
Tareas:
- [ ] tests/test_auth.py:
  - test_register_success
  - test_register_invalid_email
  - test_register_weak_password
  - test_login_success
  - test_login_invalid_credentials
  - test_refresh_token

Criterios de aceptación:
- Todos los tests pasan
- Coverage >80%
- Tests corren en <5s
```

### Issue 14: Crear tests para endpoints de Natilleras
**Complejidad**: 1.0  
**Labels**: backend, testing, ci-cd  
**Descripción**:
```
Tareas:
- [ ] tests/test_natilleras.py con fixtures
- [ ] test_create_natillera_success
- [ ] test_create_natillera_invalid_amount
- [ ] test_get_natilleras_list
- [ ] test_update_natillera
- [ ] test_delete_natillera
- [ ] test_add_participant
- [ ] pytest --cov

Criterios de aceptación:
- Coverage >75%
- Tests com fixtures de BD
- Todos pasan
```

---

## 💻 FRONTEND - Estructura e Setup (P0)

### Issue 15: Setup React + Vite + Tailwind + routing inicial
**Complejidad**: 1.0  
**Labels**: frontend, setup, build  
**Descripción**:
```
Tareas:
- [ ] npm create vite@latest natillera-frontend -- --template react
- [ ] npm install tailwindcss postcss autoprefixer
- [ ] Configurar tailwind.config.js
- [ ] Crear componentes base:
  - Layout/Header.jsx
  - Layout/Sidebar.jsx
  - Layout/Footer.jsx
- [ ] React Router v6 setup:
  - /dashboard
  - /login
  - /register
  - /natilleras
- [ ] vite.config.js: API_BASE_URL

Criterios de aceptación:
- npm run dev funciona
- Tailwind aplica estilos
- Routing funciona
- Build genera dist/
```

### Issue 16: Crear componentes de Autenticación (Login/Register)
**Complejidad**: 1.0  
**Labels**: frontend, components, auth  
**Descripción**:
```
Tareas:
- [ ] components/Auth/LoginForm.jsx
  - Email input
  - Password input
  - "Recordarme" checkbox
  - Link "¿Olvidó contraseña?"
  - Validación antes de enviar
- [ ] components/Auth/RegisterForm.jsx
  - Full name, email, password, confirm password
  - Validaciones
  - Link "¿Ya tiene cuenta?"
- [ ] Integración con API:
  - axios POST /auth/login
  - axios POST /auth/register
  - Guardar JWT en localStorage
  - Redirect a /dashboard

Criterios de aceptación:
- Formularios validan
- JWT se guarda
- Redirect funciona
- Errores se muestran
```

### Issue 17: Crear Context de Autenticación (AuthContext)
**Complejidad**: 1.0  
**Labels**: frontend, state-management, auth  
**Descripción**:
```
Tareas:
- [ ] context/AuthContext.jsx:
  - useAuth hook
  - provider con login(), logout(), register()
  - currentUser state
  - isLoading, error states
  - Verificar token al cargar app
- [ ] localStorage: guardar JWT
- [ ] Axios interceptor: agregar Authorization header

Criterios de aceptación:
- Hook funciona en componentes
- Token persiste al recargar
- Logout limpia localStorage
- Interceptor agrega header
```

---

## 🎨 FRONTEND - Componentes Principales (P1)

### Issue 18: Crear Dashboard principal (listado de Natilleras)
**Complejidad**: 1.5  
**Labels**: frontend, components, dashboard  
**Descripción**:
```
Tareas:
- [ ] pages/Dashboard.jsx
  - Header con saludo
  - Botón "Nueva Natillera"
  - Lista de natilleras (cards o tabla)
  - Por cada natillera:
    - Nombre, descripción
    - "Fondos recaudados: $X"
    - "Período: semanal/quincenal/mensual"
    - Botones: Ver, Editar, Eliminar
  - Estado vacío si no hay
- [ ] TanStack Query para fetch
- [ ] Refetch cada 30s o manual

Criterios de aceptación:
- Carga lista de natilleras
- Cards se muestran
- Botones navegan
- Actualiza con query
```

### Issue 19: Crear página de detalle de Natillera
**Complejidad**: 1.5  
**Labels**: frontend, components, pages  
**Descripción**:
```
Tareas:
- [ ] pages/NatilleraDetail.jsx
  - Información general (nombre, descripción)
  - Resumen financiero (total, por socio)
  - Tab 1: Participantes (lista + botón agregar)
  - Tab 2: Transacciones (tabla de pagos)
  - Tab 3: Reportes (balance, summary)
  - Botón "Hacer Pago" (si es socio)
  - Botón "Distribuir" (si es admin)
- [ ] Uso de React Router useParams()
- [ ] useQuery para fetch data

Criterios de aceptación:
- Tabs funcionan
- Datos se cargan
- Botones habilitan acciones
- Responsivo en mobile
```

### Issue 20: Crear formulario para crear/editar Natillera
**Complejidad**: 1.0  
**Labels**: frontend, components, forms  
**Descripción**:
```
Tareas:
- [ ] components/Forms/NatilleraForm.jsx
  - Input: nombre, descripción
  - Input: monto total, monto período
  - Select: periodicidad
  - DatePicker: fecha inicio, fecha fin
  - Botones: Guardar, Cancelar
  - Validaciones
- [ ] Modal o página separada
- [ ] Llamar POST /natilleras o PUT /natilleras/{id}
- [ ] Toast de éxito/error

Criterios de aceptación:
- Validaciones funcionan
- API call funciona
- Toast se muestra
- Redirect tras guardar
```

### Issue 21: Crear componente de tabla de Transacciones
**Complejidad**: 1.0  
**Labels**: frontend, components, tables  
**Descripción**:
```
Tareas:
- [ ] components/Transactions/TransactionsTable.jsx
  - Tabla con columnas:
    - Fecha, Participante, Monto, Estado, Acción
  - Fila expandible para ver detalles (opcional)
  - Paginación o infinite scroll
  - Filtro por estado
  - Filtro por rango de fechas
- [ ] useQuery para fetch
- [ ] Botón: descargar comprobante

Criterios de aceptación:
- Tabla muestra datos
- Paginación funciona
- Filtros funcionan
- Responsive
```

---

## 📱 MOBILE - Setup (P1)

### Issue 22: Crear app base con Expo y navegación
**Complejidad**: 1.0  
**Labels**: mobile, setup, navigation  
**Descripción**:
```
Tareas:
- [ ] npx create-expo-app natillera-mobile
- [ ] npm install react-navigation @react-navigation/native @react-navigation/bottom-tabs
- [ ] Configurar app.json (nombre, version, etc)
- [ ] Estructura de navegación:
  - Bottom tabs: Dashboard, Pagos, Perfil
  - Stack navigator dentro de cada tab
- [ ] Estilos base con React Native StyleSheet
- [ ] Testeado en Expo Go

Criterios de aceptación:
- expo start funciona
- Navegación responde
- Bottom tabs visible
- Assets cargan
```

### Issue 23: Crear pantalla de login móvil
**Complejidad**: 0.5  
**Labels**: mobile, components, auth  
**Descripción**:
```
Tareas:
- [ ] screens/Auth/LoginScreen.jsx
  - Input email
  - Input password (securo)
  - Botón login
  - Link registro
  - Validaciones
- [ ] Llamar API /auth/login
- [ ] Guardar JWT en device storage (SecureStore)
- [ ] Navigate a app después login

Criterios de aceptacion:
- Form valida
- API call funciona
- Token guardado
- Navigation funciona
```

### Issue 24: Crear pantalla Dashboard móvil
**Complejidad**: 1.0  
**Labels**: mobile, components, dashboard  
**Descripción**:
```
Tareas:
- [ ] screens/Dashboard/DashboardScreen.jsx
  - Header con saludo
  - Cards de natilleras (scroll horizontal)
  - Datos: nombre, progreso, monto
  - Botón: ir a detalle
  - Pull-to-refresh
- [ ] Llamar useQuery /natilleras
- [ ] Responsive width

Criterios de aceptación:
- Cards se muestran
- Pull-to-refresh funciona
- Responsive
- Scroll suave
```

### Issue 25: Crear pantalla de Pagos móvil
**Complejidad**: 1.0  
**Labels**: mobile, components, transactions  
**Descripción**:
```
Tareas:
- [ ] screens/Pagos/PagosScreen.jsx
  - Select: ¿Cuál natillera?
  - Input: monto
  - Select: método pago
  - Botón: confirmar
  - Validaciones
- [ ] Llamar POST /transactions
- [ ] Mostrar comprobante tras éxito
- [ ] Toast errors

Criterios de aceptación:
- Formulario valida
- API call funciona
- Comprobante se muestra
- Toast funciona
```

---

## 📚 DOCUMENTACIÓN (P2)

### Issue 26: Escribir documentación de API (API_DOCS.md)
**Complejidad**: 0.5  
**Labels**: docs, documentation, backend  
**Descripción**:
```
Tareas:
- [ ] docs/API_DOCS.md:
  - Resumen de endpoints
  - Autenticación (JWT)
  - Ejemplos curl de cada endpoint
  - Respuestas exitosas y errores
  - Códigos HTTP explicados
- [ ] Incluir ejemplos de request/response

Criterios de aceptación:
- Documento es claro
- Ejemplos funcionales
- Cubre todos endpoints
```

### Issue 27: Escribir DEVELOPMENT.md (guía local)
**Complejidad**: 0.5  
**Labels**: docs, documentation, setup  
**Descripción**:
```
Tareas:
- [ ] docs/DEVELOPMENT.md:
  - Instalación Python + Node
  - Setup Backend (venv, pip install)
  - Setup Frontend (npm install)
  - Setup Mobile (expo)
  - Variables de entorno
  - Comandos útiles (test, lint)
  - Estructura de carpetas

Criterios de aceptación:
- Nuevo dev sigue pasos sin problemas
- Links a recursos
- Troubleshooting
```

### Issue 28: Escribir DEPLOYMENT.md (guía Vercel + Render)
**Complejidad**: 1.0  
**Labels**: docs, documentation, devops  
**Descripción**:
```
Tareas:
- [ ] docs/DEPLOYMENT.md:
  - Desplegar frontend en Vercel
  - Desplegar backend en Render
  - Configurar PostgreSQL en Supabase
  - Environment variables en cada plataforma
  - GitHub Actions CI/CD basics
  - Monitoreo (logs, errores)

Criterios de aceptación:
- Pasos son claros
- Incluye screenshots
- Troubleshooting
```

---

## 🔄 CI/CD y DevOps (P2)

### Issue 29: Crear GitHub Actions para backend tests
**Complejidad**: 1.0  
**Labels**: devops, ci-cd, testing  
**Descripción**:
```
Tareas:
- [ ] .github/workflows/backend-tests.yml:
  - Trigger: push a dev, PR a main
  - Python setup (3.11)
  - pip install -r requirements.txt
  - pytest --cov
  - Fallar si coverage < 75%
  - Optional: Codecov upload

Criterios de aceptación:
- Workflow corre automáticamente
- Tests pasan localmente
- Coverage reportado
```

### Issue 30: Crear GitHub Actions para frontend build
**Complejidad**: 0.5  
**Labels**: devops, ci-cd, build  
**Descripción**:
```
Tareas:
- [ ] .github/workflows/frontend-build.yml:
  - Trigger: push a dev, PR a main
  - Node setup (18)
  - npm install
  - npm run build
  - Fallar si build falla

Criterios de aceptación:
- Workflow corre
- Build exitoso
```

---

## 🎯 Resumen de Issues por Fase

### FASE 1 (MVP Core - Semanas 1-3)
- ✅ Issues 1-14 (Backend core)
- ✅ Issues 15-21 (Frontend core)
- ✅ Issues 22-25 (Mobile core)

### FASE 2 (Testing y Docs)
- Issues 13, 14, 26-30

### FASE 3+ (Features avanzadas)
- Integración Stripe
- Notificaciones/SMS
- OAuth
- Inversiones

---

**Total Issues**: 30  
**Complejidad Total Estimada**: 40 pts  
**Tiempo Estimado MVP**: 4-5 semanas
