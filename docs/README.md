# 📚 Documentación - Natillera App

Bienvenido a la carpeta de documentación de Natillera App. Aquí encontrarás guías detalladas para el desarrollo, despliegue y uso de la plataforma.

## 📖 Documentos Disponibles

### 0. [design/](./design/README.md) - Diseño, Arquitectura y Patrones
- Arquitectura de capas del backend (API → Service → Repository → Model)
- Patrones de diseño: Repository, Unit of Work, Strategy, Observer
- Convenciones de Clean Code para Python y JavaScript
- Arquitectura feature-based del frontend (React + TanStack Query)

### 1. [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitectura Técnica
- Diagramas de arquitectura
- Diseño de base de datos (ER)
- Flujos de datos
- Stack tecnológico
- Performance targets

### 2. [API_DOCS.md](./API_DOCS.md) - Documentación de API
- Endpoints disponibles
- Ejemplos de requests/responses
- Códigos de error
- Autenticación JWT
- Ejemplos curl

### 3. [DEVELOPMENT.md](./DEVELOPMENT.md) - Guía de Desarrollo Local
- Instalación de dependencias
- Setup de cada componente
- Variables de entorno
- Comandos útiles
- Troubleshooting
- Estructura de carpetas

### 4. [DEPLOYMENT.md](./DEPLOYMENT.md) - Guía de Despliegue
- Desplegar en Vercel (frontend)
- Desplegar en Render (backend)
- Configurar base de datos en Supabase
- GitHub Actions CI/CD
- Monitoreo en producción

## 🚀 Quick Links

| Documento | Propósito | Audiencia |
|-----------|----------|-----------|
| ARCHITECTURE.md | Entender diseño técnico | Developers, Architects |
| API_DOCS.md | Integración con API | Frontend/Mobile devs |
| DEVELOPMENT.md | Setup local | Todos |
| DEPLOYMENT.md | Llevar a producción | DevOps, Leads |

## 📊 Diagrama de Flujo de Documentación

```
Nuevo Dev
    │
    ├─→ DEVELOPMENT.md (Setup local)
    │
    ├─→ ARCHITECTURE.md (Entender sistema)
    │
    ├─→ API_DOCS.md (Integración)
    │
    └─→ DEPLOYMENT.md (Deploy)
```

## 🔍 Busca por tema

### Autenticación
- ARCHITECTURE.md → Sección "Seguridad"
- API_DOCS.md → Endpoints /auth

### Base de Datos
- ARCHITECTURE.md → Sección "Diagrama E-R"
- DEVELOPMENT.md → Setup PostgreSQL

### API Endpoints
- API_DOCS.md → Todos los endpoints
- ARCHITECTURE.md → Flujos principales

### Deploy y DevOps
- DEPLOYMENT.md → Todas las plataformas
- DEVELOPMENT.md → Troubleshooting

## ❓ FAQ (Frequently Asked Questions)

### ¿Por dónde empiezo?
1. Lee [DEVELOPMENT.md](./DEVELOPMENT.md)
2. Setup local
3. Lee [ARCHITECTURE.md](./ARCHITECTURE.md)
4. Comienza a codificar

### ¿Cómo despliego a producción?
Ver [DEPLOYMENT.md](./DEPLOYMENT.md) - pasos paso a paso.

### ¿Dónde veo los endpoints disponibles?
Ver [API_DOCS.md](./API_DOCS.md) - documentación completa de API.

### ¿Cómo contribuyo?
Ver [CONTRIBUTING.md](../CONTRIBUTING.md) en la raíz del proyecto.

## 📞 Soporte

- **Problemas técnicos**: Revisa DEVELOPMENT.md → Troubleshooting
- **Deploy issues**: Revisa DEPLOYMENT.md
- **API questions**: Revisa API_DOCS.md
- **General questions**: Abre un Issue en GitHub

## 📈 Roadmap de Documentación

### ✅ Completado
- [x] ARCHITECTURE.md
- [x] API_DOCS.md (estructura)
- [x] DEVELOPMENT.md (estructura)
- [x] DEPLOYMENT.md (estructura)

### 🔄 En Progreso
- Agregar ejemplos de código más detallados
- Screenshots de setup
- Videos tutoriales (opcional)

### 📋 Por Hacer
- Guía de troubleshooting expandida
- Performance tuning guide
- Security best practices
- Mobile development guide

---

**Última actualización**: Mayo 2026  
**Versión**: 1.0  
**Mantenedor**: Equipo Natillera App
