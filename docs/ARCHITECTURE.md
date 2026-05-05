# 🏗️ Arquitectura de Natillera App

## Visión General

Natillera App sigue una **arquitectura de microservicios ligera** con tres capas principales:

```
┌─────────────────────────────────────────────────┐
│          FRONTEND (React + Vite)                │
│  Dashboard, Gestión Natilleras, Transacciones  │
└──────────────┬──────────────────────────────────┘
               │ HTTPS API Calls
┌──────────────▼──────────────────────────────────┐
│    MOBILE (React Native + Expo)                 │
│  App Android/iOS, Pagos, Notificaciones         │
└──────────────┬──────────────────────────────────┘
               │ REST API (JSON)
┌──────────────▼──────────────────────────────────┐
│         BACKEND (FastAPI)                       │
│    Routes → Services → Models → Database        │
└──────────────┬──────────────────────────────────┘
               │ SQL Queries
┌──────────────▼──────────────────────────────────┐
│    DATABASE (PostgreSQL)                        │
│  Tables: Users, Natilleras, Transactions, etc   │
└─────────────────────────────────────────────────┘
```

---

## 📐 Capas de la Aplicación

### 1. **Presentación (Frontend + Mobile)**

#### Frontend Web (React + Vite)
```
frontend/
├── src/
│   ├── components/          # Componentes reutilizables
│   │   ├── Auth/           # Login, Registro
│   │   ├── Natilleras/     # CRUD Natilleras
│   │   ├── Transactions/   # Tabla transacciones
│   │   └── Common/         # Header, Footer, etc
│   ├── pages/              # Páginas (rutas)
│   │   ├── Dashboard.jsx
│   │   ├── Natilleras.jsx
│   │   ├── Pagos.jsx
│   │   └── Profile.jsx
│   ├── services/           # Llamadas API
│   │   └── api.js          # Axios config
│   ├── hooks/              # Hooks personalizados
│   │   ├── useAuth.js
│   │   └── useNatilleras.js
│   ├── context/            # Context API
│   │   └── AuthContext.jsx
│   └── App.jsx
```

#### Mobile App (React Native + Expo)
```
mobile/
├── app/
│   ├── (tabs)/             # Navegación bottom tabs
│   │   ├── index.jsx       # Dashboard
│   │   ├── pagos.jsx       # Hacer pagos
│   │   └── profile.jsx     # Perfil
│   ├── screens/
│   │   ├── LoginScreen.jsx
│   │   └── NatilleraDetail.jsx
│   └── navigation/
├── services/               # Llamadas API
└── hooks/                  # Hooks
```

---

### 2. **Lógica de Negocio (Backend - FastAPI)**

#### Estructura Backend
```
backend/
├── app/
│   ├── main.py             # Entry point, CORS config
│   ├── core/
│   │   ├── config.py       # Settings, env vars
│   │   └── security.py     # JWT, password hashing
│   ├── models/             # SQLAlchemy ORM Models
│   │   ├── user.py
│   │   ├── natillera.py
│   │   ├── transaction.py
│   │   └── participant.py
│   ├── schemas/            # Pydantic validation
│   │   ├── user.py
│   │   ├── natillera.py
│   │   └── transaction.py
│   ├── api/                # API Routes (v1)
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── natilleras.py
│   │   │   │   ├── transactions.py
│   │   │   │   ├── users.py
│   │   │   │   └── reports.py
│   │   │   └── router.py
│   │   └── dependencies.py
│   ├── services/           # Business Logic
│   │   ├── auth.py
│   │   ├── natillera.py
│   │   ├── transaction.py
│   │   └── email.py
│   ├── database.py         # SQLAlchemy setup
│   └── dependencies.py     # Inyección de dependencias
├── migrations/             # Alembic (DB migrations)
├── tests/
│   ├── test_auth.py
│   ├── test_natilleras.py
│   └── test_transactions.py
└── requirements.txt
```

---

### 3. **Persistencia (Base de Datos)**

#### Diagrama E-R (Entidad-Relación)

```
┌──────────────────┐
│      USER        │
├──────────────────┤
│ id (PK)          │
│ email (UNIQUE)   │
│ password_hash    │
│ full_name        │
│ phone            │
│ created_at       │
│ is_active        │
└────────┬─────────┘
         │ 1:M
         │
         ├─────────────────────────┐
         │                         │
    ┌────▼─────────────────┐    ┌─▼──────────────────┐
    │    NATILLERA         │    │   PARTICIPANT      │
    ├──────────────────────┤    ├────────────────────┤
    │ id (PK)              │    │ id (PK)            │
    │ name                 │    │ natillera_id (FK)  │
    │ description          │    │ user_id (FK)       │
    │ admin_id (FK→USER)   │    │ amount_per_period  │
    │ total_amount         │    │ status             │
    │ period_amount        │    │ joined_at          │
    │ periodicidad         │    │ removed_at         │
    │ start_date           │    └────────────────────┘
    │ end_date             │                 │ 1:M
    │ status (active/inactive)│              │
    │ created_at           │    ┌────────────▼───────────┐
    └────┬────────────────┘     │    TRANSACTION         │
         │ 1:M                  ├────────────────────────┤
         │                      │ id (PK)                │
         │                      │ natillera_id (FK)      │
         │                      │ participant_id (FK)    │
         │                      │ amount                 │
         │                      │ type (payment/interest)│
         │                      │ status (pending/done)  │
         │                      │ payment_method         │
         │                      │ transaction_date       │
         │                      │ created_at             │
         │                      └────────────────────────┘
         │
    ┌────▼──────────────────┐
    │   DISTRIBUTION        │
    ├───────────────────────┤
    │ id (PK)               │
    │ natillera_id (FK)     │
    │ participant_id (FK)   │
    │ amount                │
    │ interest              │
    │ total_received        │
    │ distribution_date     │
    │ status (pending/done) │
    └───────────────────────┘
```

#### Flujo de Datos

```
1. Usuario se registra → CREATE USER
2. Admin crea natillera → CREATE NATILLERA
3. Admin invita socios → CREATE PARTICIPANT
4. Socio paga → CREATE TRANSACTION
5. Admin registra rentabilidad → UPDATE TRANSACTION + CREATE DISTRIBUTION
6. Diciembre: distribuir fondos → UPDATE PARTICIPANT BALANCE
```

---

## 🔄 Flujos Principales

### Flujo 1: Registro e Inicio de Sesión

```
Cliente (Frontend)           Backend              BD
    │                           │                 │
    ├─ POST /auth/register ───→ │                 │
    │                           ├─ Hash password  │
    │                           ├─ INSERT USER ──→│
    │                           │ ← INSERT OK    │
    │ ← JWT token ────────────── │                 │
    │                           │                 │
    ├─ POST /auth/login ───────→ │                 │
    │                           ├─ Query USER ───→│
    │                           │ ← USER data    │
    │                           ├─ Verify pass   │
    │ ← JWT access + refresh ── │                 │
    │    tokens                 │                 │
```

### Flujo 2: Crear Natillera

```
Admin                         Backend              BD
│                              │                  │
├─ POST /natilleras ──────────→ │                  │
│   { name, amount, period }    │                  │
│                              ├─ Validate ──────→│
│                              ├─ INSERT ────────→│
│                              │                  │
│ ← Natillera { id, ... } ──── │ ← ID           │
│                              │                  │
├─ POST /natilleras/{id}/participants ────→      │
│   { user_ids: [...] }        │                  │
│                              ├─ INSERT x3 ────→│
│ ← Participants created ────── │                 │
```

### Flujo 3: Registrar Pago

```
Socio                         Backend              BD
│                              │                  │
├─ POST /transactions ────────→ │                  │
│   { natillera_id,            │                  │
│     amount,                  │                  │
│     payment_method }         │                  │
│                              ├─ Validate ──────→│
│                              ├─ INSERT ────────→│
│                              │                  │
│                              ├─ UPDATE balance  │
│                              │     (si pagó)   │
│                              │                  │
│ ← Receipt { id, ... } ────── │                 │
│                              │                  │
├─ EMAIL confirmation ←──────── │                 │
│ (async task)                 │                  │
```

### Flujo 4: Distribución de Fondos

```
Admin                         Backend              BD
│                              │                  │
├─ POST /natilleras/{id}/distribute ────→         │
│                              │                  │
│                              ├─ Calculate ────→│
│                              │ - Total aportado │
│                              │ - Intereses    │
│                              │ - Por socio    │
│                              │                  │
│                              ├─ CREATE ───────→│
│                              │ DISTRIBUTIONS  │
│                              │                  │
│                              ├─ SEND EMAILS   │
│                              │ + Comprobantes  │
│                              │                  │
│ ← Distribution report ────── │                 │
```

---

## 🔐 Seguridad

### Autenticación
```
┌─────────────┐
│  Credenciales │
│ (email+pass) │
└──────┬──────┘
       │
       ▼
┌────────────────────────────────────┐
│ POST /auth/login                   │
│ - Hash password                    │
│ - Compare con DB                   │
└─────────┬──────────────────────────┘
          │
          ▼
    ┌─────────────────────┐
    │  JWT Generation     │
    │ Header.Payload.Sign │
    └─────────┬───────────┘
              │
              ▼
    ┌──────────────────┐
    │ Access Token     │ (15 min)
    │ Refresh Token    │ (7 días)
    └──────────────────┘
```

### Autorización
```
GET /natilleras/{id}
    │
    ▼
Verificar JWT válido
    │
    ▼
Verificar user es participante
    │
    ▼
Retornar datos
```

---

## 📦 API Endpoints (v1)

```
Authentication
  POST   /auth/register
  POST   /auth/login
  POST   /auth/refresh
  POST   /auth/logout

Users
  GET    /users/me
  PUT    /users/{id}
  GET    /users/{id}

Natilleras
  GET    /natilleras                      (listar)
  POST   /natilleras                      (crear - admin)
  GET    /natilleras/{id}
  PUT    /natilleras/{id}                 (admin)
  DELETE /natilleras/{id}                 (admin)
  GET    /natilleras/{id}/participants
  POST   /natilleras/{id}/participants    (agregar)
  DELETE /natilleras/{id}/participants/{pid}

Transactions
  GET    /transactions                     (filtrar)
  POST   /transactions                     (crear)
  GET    /transactions/{id}
  PUT    /transactions/{id}               (admin)

Reports
  GET    /natilleras/{id}/reports/balance
  GET    /natilleras/{id}/reports/summary
  GET    /natilleras/{id}/reports/export  (PDF)

Distributions
  GET    /distributions                    (listar)
  POST   /natilleras/{id}/distribute      (admin)
  GET    /distributions/{id}
```

---

## 🚀 Deployment Architecture

```
GitHub Repository
      │
      ├─→ GitHub Actions (CI/CD)
      │   ├─ Run tests
      │   ├─ Build Docker images
      │   └─ Deploy to production
      │
      ├─→ Frontend Deploy
      │   └─ Vercel (React + Vite)
      │       └─ https://natillera-app.vercel.app
      │
      ├─→ Backend Deploy
      │   └─ Render / Railway
      │       └─ https://natillera-api.render.com
      │       └─ Python + FastAPI
      │
      └─→ Database
          └─ Supabase / Render PostgreSQL
              └─ Backups automáticos
```

---

## 🛠️ Tech Stack Details

| Componente | Librería | Versión | Razón |
|-----------|----------|---------|-------|
| **Backend** | FastAPI | 0.104+ | Rendimiento, auto-docs |
| **ORM** | SQLAlchemy | 2.0+ | Flexible, migraciones |
| **Migraciones** | Alembic | 1.12+ | Control versiones DB |
| **Validación** | Pydantic | 2.5+ | Type-safe |
| **Auth** | python-jose | 3.3+ | JWT standard |
| **Password** | passlib | 1.7+ | Hash seguro |
| **DB** | PostgreSQL | 13+ | ACID, scalable |
| **Frontend** | React | 18+ | UI moderno |
| **Build** | Vite | 5+ | Rápido |
| **Styling** | Tailwind | 3.3+ | Utility-first |
| **Mobile** | React Native | 0.72+ | Cross-platform |

---

## 📊 Performance Targets

| Métrica | Target | Cómo Lograr |
|---------|--------|-----------|
| Tiempo carga página | <2s | Vite, lazy loading, CDN |
| API response | <100ms | Índices DB, caching |
| Mobile app | <3s | Expo optimized |
| Database | 99.5% uptime | Supabase backups |

---

## 🔄 Ciclo de Vida de Datos

```
1. USER → Registra en la app
2. NATILLERA → Admin crea grupo de ahorro
3. PARTICIPANT → Usuarios se unen
4. TRANSACTION → Registra aportes periódicamente
5. BALANCE → Sistema calcula saldo actualizado
6. DISTRIBUTION → Diciembre: reparte fondos
7. HISTÓRICO → Datos guardados para auditoría
```

---

**Versión**: 1.0  
**Última actualización**: Mayo 2026
