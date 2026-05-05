# 🌟 Natillera App - Plataforma Digital de Ahorro Comunitario

> Transformando la tradición colombiana de las natilleras al mundo digital

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: MVP Development](https://img.shields.io/badge/Status-MVP%20Development-blue)]()
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)]()
[![Node: 18+](https://img.shields.io/badge/Node-18%2B-green)]()

## 📖 ¿Qué es una Natillera?

Una **natillera** es un mecanismo de ahorro informal y tradicional en Colombia donde:
- Un grupo de personas (familiares, amigos, compañeros) se asocian
- Aportan una suma fija de dinero **periódicamente** (semanal, quincenal, mensual)
- El dinero acumulado se **distribuye entre participantes** (generalmente en diciembre)
- El fondo puede generar **rentabilidad** mediante préstamos o inversiones

**Natillera App** lleva este concepto al mundo digital, agregando:
✅ Seguridad y transparencia  
✅ Automatización de pagos y cálculos  
✅ Múltiples opciones de pago  
✅ Integración móvil y web  
✅ Trazabilidad completa de transacciones  

---

## 🚀 Quick Start

### Requisitos Previos
```bash
# Backend
Python 3.11+
PostgreSQL 13+

# Frontend
Node.js 18+
npm o yarn

# Mobile
Node.js 18+
Expo CLI
```

### Instalación Local

#### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
# API disponible en http://localhost:8000
```

#### 2. Frontend Web
```bash
cd frontend
npm install
npm run dev
# Disponible en http://localhost:5173
```

#### 3. App Móvil
```bash
cd mobile
npm install
npx expo start
# Scannear código QR con Expo Go en tu teléfono
```

---

## 📁 Estructura del Proyecto

```
natillera-app/
├── 📄 CLIENT_BRIEF.md              # Brief completo del proyecto
├── 📄 README.md                    # Este archivo
├── 📄 ARCHITECTURE.md              # Arquitectura técnica detallada
├── 📄 CONTRIBUTING.md              # Guía de contribución
│
├── backend/                        # 🔧 API RESTful (FastAPI + Python)
│   ├── app/
│   │   ├── main.py                # Entry point
│   │   ├── core/                  # Configuración
│   │   ├── models/                # Modelos de DB (SQLAlchemy)
│   │   ├── schemas/               # Esquemas Pydantic
│   │   ├── api/                   # Rutas API
│   │   ├── services/              # Lógica de negocio
│   │   └── dependencies.py        # Inyección de dependencias
│   ├── migrations/                # Alembic migrations
│   ├── tests/                     # Tests unitarios
│   ├── requirements.txt
│   ├── .env.example
│   └── docker-compose.yml         # Para desarrollo local
│
├── frontend/                       # 💻 Web (React + Vite + Tailwind)
│   ├── src/
│   │   ├── main.jsx               # Entry point
│   │   ├── components/            # Componentes reutilizables
│   │   ├── pages/                 # Páginas principales
│   │   ├── services/              # Llamadas API
│   │   ├── hooks/                 # Hooks personalizados
│   │   ├── context/               # Context API
│   │   ├── utils/                 # Utilidades
│   │   └── App.jsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
├── mobile/                         # 📱 App Móvil (React Native + Expo)
│   ├── app/
│   │   ├── (tabs)/
│   │   ├── screens/
│   │   ├── components/
│   │   └── navigation/
│   ├── services/
│   ├── hooks/
│   ├── package.json
│   ├── app.json
│   └── .env.example
│
├── docs/                           # 📚 Documentación
│   ├── API.md                     # Documentación API
│   ├── DEVELOPMENT.md             # Guía de desarrollo
│   ├── DEPLOYMENT.md              # Guía de deployment
│   └── ARCHITECTURE.md            # Diagrama de arquitectura
│
├── .github/
│   └── workflows/                 # CI/CD (GitHub Actions)
│       ├── backend-tests.yml
│       ├── frontend-tests.yml
│       └── deploy.yml
│
└── .gitignore                      # Git ignore global
```

---

## 🔧 Stack Tecnológica

| Capa | Tecnología | Razón |
|------|-----------|-------|
| **Frontend Web** | React 18 + Vite + Tailwind CSS | Rápido, moderno, comunidad grande |
| **App Móvil** | React Native + Expo | Write once, run anywhere |
| **Backend** | FastAPI + Python | Rápido, documentación automática |
| **Base de Datos** | PostgreSQL | Confiable, ACID, escalable |
| **ORM** | SQLAlchemy | Flexible, migrations con Alembic |
| **Autenticación** | JWT + OAuth2 | Seguro, estándar industry |
| **Hosting Web** | Vercel | GRATIS, deploys automáticos |
| **Hosting API** | Render/Railway | GRATIS tier, PostgreSQL incluida |
| **Base de Datos** | Supabase/Render | GRATIS 500MB, backups automáticos |
| **Pagos** | Stripe/PayPal API | Seguro, compliant, integración simple |

---

## 📊 Funcionalidades MVP (Fase 1)

### ✅ Autenticación
- [x] Registro de usuarios
- [x] Login con email/password
- [x] JWT refresh tokens
- [ ] OAuth2 (Google, GitHub)

### ✅ Gestión de Natilleras
- [x] Crear natillera (admin)
- [x] Configurar: monto, periodicidad, fecha fin
- [x] Invitar socios
- [x] Agregar/remover participantes
- [x] Dashboard de administración

### ✅ Pagos y Transacciones
- [x] Registro de pagos manuales
- [x] Historial de transacciones
- [x] Cálculo automático de saldos
- [ ] Integración Stripe
- [ ] Recordatorios automáticos

### ✅ Reportes
- [x] Dashboard de estado actual
- [x] Reporte de balances por socio
- [x] Historial de movimientos
- [ ] Exportar a PDF/Excel

---

## 🔄 Metodología de Desarrollo con OpenCode

Este proyecto sigue el flujo de trabajo descrito en **"Running Your AFK Agent"**, adaptado para OpenCode:

### 1️⃣ **Planificación (Client Brief)**
- ✅ Documento: `CLIENT_BRIEF.md`
- Define objetivos, usuarios, funcionalidades
- Wireframes y flujos de usuario

### 2️⃣ **Arquitectura (Design)**
- ✅ Documento: `ARCHITECTURE.md`
- Diseño de base de datos
- Diagramas de flujo
- Especificación de APIs

### 3️⃣ **Desarrollo Ágil**
- Iteraciones cortas (1-2 semanas)
- Issues en GitHub (1.0 / 0.5 pts = complexidad)
- PRs con revisiones automáticas
- Commits semánticos: `feat:`, `fix:`, `docs:`

### 4️⃣ **Testing Continuo**
- Tests unitarios en backend: pytest
- Tests en frontend: Vitest
- GitHub Actions para CI/CD

### 5️⃣ **Deployment Progresivo**
- Dev branch: cambios en desarrollo
- Staging: tests antes de producción
- Main branch: producción en Vercel/Render

### 6️⃣ **Monitoreo**
- Logs en Vercel + Render
- Errores en Sentry (opcional)
- Métricas en Mixpanel/Posthog (opcional)

---

## 📋 Issues y Roadmap

Consulta la sección de **Issues** en GitHub para ver:
- Features en desarrollo
- Bugs reportados
- Tareas de documentación
- TODOs de infraestructura

Cada issue tiene:
- Descripción clara
- Criterios de aceptación
- Complejidad (1.0, 0.5, 2.0 pts)
- Etiquetas (backend, frontend, mobile, docs)

---

## 🚀 Deployment Gratuito

### Frontend (Vercel)
```bash
# 1. Push a GitHub
git push origin main

# 2. Conectar en Vercel.com
# Auto-redeploy con cada push
```

### Backend (Render)
```bash
# 1. Crear servicio web en render.com
# 2. Conectar repositorio
# 3. Set Environment Variables
# Auto-deploys con cada push
```

### Database (Supabase)
```bash
# 1. Crear proyecto en supabase.com
# 2. Copiar connection string
# 3. Usar en backend .env
```

---

## 📚 Documentación

- **[CLIENT_BRIEF.md](./CLIENT_BRIEF.md)** - Brief completo del proyecto
- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Diseño técnico
- **[API_DOCS.md](./docs/API_DOCS.md)** - Endpoints detallados
- **[DEVELOPMENT.md](./docs/DEVELOPMENT.md)** - Guía desarrollo local
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - Guía de despliegue

---

## 🤝 Contribución

Para contribuir:

1. Fork el repositorio
2. Crea una rama: `git checkout -b feat/tu-feature`
3. Commit: `git commit -m "feat: descripción"`
4. Push: `git push origin feat/tu-feature`
5. Abre un PR

Ver [CONTRIBUTING.md](./CONTRIBUTING.md) para más detalles.

---

## 📊 Métricas del Proyecto

| Métrica | Estado |
|---------|--------|
| Issues Abiertos | 15 |
| PRs en Revisión | 0 |
| Coverage | 75% |
| Build Status | ✅ Passing |
| Last Update | Mayo 2026 |

---

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver [LICENSE](./LICENSE) para detalles.

---

## 👥 Equipo

- **Product Owner**: [Tu nombre]
- **Backend Lead**: [Tu nombre]
- **Frontend Lead**: [Tu nombre]
- **Mobile Dev**: [Tu nombre]

---

## 🎯 Objetivos de la Entrega Actual

**Numeral 1: Client Brief** ✅
- Documento completo: `CLIENT_BRIEF.md`
- Usuarios, funcionalidades, timeline

**Numeral 2: Repositorio GitHub** ✅
- Estructura del proyecto
- README claro y profesional
- Archivos iniciales (`requirements.txt`, `package.json`)
- Issues bien documentadas

**Numeral 3: Issues en GitHub** ✅
- 15+ issues estructurados
- Complejidad asignada
- Criterios de aceptación claros

---

## 🔗 Enlaces Útiles

- 📖 [Documentación FastAPI](https://fastapi.tiangolo.com/)
- ⚛️ [Documentación React](https://react.dev/)
- 📱 [Documentación Expo](https://docs.expo.dev/)
- 🎨 [Tailwind CSS](https://tailwindcss.com/)
- 🗄️ [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

## 📞 Contacto y Soporte

- GitHub Issues: Reportar bugs
- Discussions: Preguntas generales
- Email: [tu-email@example.com]

---

**Versión**: 1.0.0  
**Última actualización**: Mayo 2026  
**Estado**: MVP en Desarrollo 🚀
