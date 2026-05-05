# CLIENT BRIEF - Natillera App

## 📋 Resumen Ejecutivo

Construir una plataforma digital que automatice y digitalice el proceso tradicional de las "natilleras" colombianas. La aplicación permitirá que grupos de personas (familiares, amigos, compañeros de trabajo) se asocien para aportar dinero periódicamente, con un sistema robusto de gestión financiera, transparencia total y múltiples opciones de pago.

---

## 🎯 Objetivos del Proyecto

1. **Democratizar el acceso**: Llevar la natillera del mundo físico al digital, eliminando barreras geográficas
2. **Aumentar seguridad**: Implementar un sistema confiable con trazabilidad de transacciones
3. **Generar valor**: Permitir rentabilidad del fondo mediante inversiones seguras
4. **Facilitar administración**: Automatizar cálculos, alertas y distribuciones de capital
5. **Cumplir regulaciones**: Garantizar transparencia y legalidad en operaciones financieras

---

## 📊 Usuarios Objetivo

### Usuario Principal: **Administrador (Tesorero)**
- Crea y gestiona natilleras
- Recibe pagos de socios
- Genera reportes de rentabilidad
- Administra inversiones del fondo
- Perfil: Mayor de 25 años, responsable, con acceso a dispositivos digitales

### Usuario Secundario: **Socio (Participante)**
- Se une a una natillera
- Realiza aportes periódicos
- Consulta saldo y movimientos
- Recibe distribuciones
- Perfil: Diverso, desde amas de casa hasta profesionales

---

## 🏗️ Funcionalidades Core (MVP)

### Fase 1: Gestión Básica
- [ ] Autenticación y registro de usuarios
- [ ] Creación de natilleras (configurar: monto, periodicidad, fecha fin)
- [ ] Gestión de socios (invitar, agregar, remover)
- [ ] Registro de pagos manuales
- [ ] Dashboard de visualización de estado
- [ ] Cálculo automático de saldos

### Fase 2: Transacciones y Pagos
- [ ] Integración con pasarela de pagos (Stripe o similar)
- [ ] Recordatorios de pagos por correo/SMS
- [ ] Historial de transacciones detallado
- [ ] Descarga de comprobantes

### Fase 3: Rentabilidad
- [ ] Sistema básico de intereses
- [ ] Registro de inversiones/rentabilidad
- [ ] Reportes de ganancia
- [ ] Distribución automática de ganancias

### Fase 4: Seguridad Avanzada
- [ ] Autenticación de dos factores
- [ ] Roles y permisos granulares
- [ ] Auditoría completa de operaciones
- [ ] Certificados de transacción

---

## 🛠️ Requisitos Técnicos

### Plataformas Requeridas
1. **Aplicación Web**: Desktop y tablet
2. **Aplicación Móvil**: iOS y Android (con React Native)
3. **Backend**: API RESTful robusta
4. **Base de Datos**: PostgreSQL con datos sensibles encriptados

### Características No Funcionales
- **Seguridad**: Encriptación end-to-end, cumplimiento PCI-DSS
- **Performance**: Carga <2s, máximo 100ms latencia en operaciones críticas
- **Disponibilidad**: 99.5% uptime
- **Escalabilidad**: Soportar 1,000+ natilleras, 10,000+ usuarios
- **Usabilidad**: Interfaz intuitiva, 95%+ de usuarios completando flujos en primer intento

---

## 💰 Modelo de Ingresos (Futuro)

- Comisión por transacción: 1-2%
- Plan Premium: $4.99/mes (sin publicidad, más funciones)
- Comisión por inversiones: 0.5% anual
- Modelo freemium para MVP

---

## 📱 Wireframes / Flujos Principales

### Flujo de Usuario - Crear Natillera
```
1. Login → Dashboard
2. Click "Nueva Natillera"
3. Configurar (monto, duración, periodicidad)
4. Invitar socios
5. Vista de administración
```

### Flujo de Usuario - Hacer Pago
```
1. Login → Mi Natillera
2. Click "Hacer Pago"
3. Seleccionar método (transferencia, tarjeta, app)
4. Confirmar cantidad
5. Comprobante automático
```

---

## 📈 Métricas de Éxito

| Métrica | Target MVP | Target 6 meses |
|---------|-----------|-----------------|
| Usuarios Registrados | 100 | 5,000 |
| Natilleras Activas | 20 | 500 |
| Capital Gestionado | $20,000 | $500,000 |
| Transacciones/mes | 200 | 10,000 |
| Tasa Retención (30d) | 70% | 80% |

---

## 🔄 Stack Tecnológica (Recomendada)

```
FRONTEND WEB:        React 18 + Vite + Tailwind CSS
APP MÓVIL:          React Native + Expo
BACKEND:            FastAPI (Python) con PostgreSQL
HOSTING:            Vercel (Frontend), Render (Backend), Supabase (DB)
PAGOS:              Stripe API / Paypal
ARQUITECTURA:       MVC con Clean Architecture
```

---

## ⏱️ Timeline MVP

- **Semana 1-2**: Backend core + DB schema
- **Semana 2-3**: Frontend básico + autenticación
- **Semana 3-4**: Integración mobile
- **Semana 4**: Testing y ajustes
- **Semana 5**: Deploy y documentación

---

## 📚 Referencias

- Artículo metodología: Running Your AFK Agent
- Flujo OpenCode: Desarrollo ágil e iterativo
- Inspiración: Plataformas fintech como Plaid, Venmo

---

## 👥 Stakeholders

| Rol | Responsabilidad |
|-----|-----------------|
| Product Owner | Definir prioridades, usuario |
| Backend Dev | API, DB, seguridad |
| Frontend Dev | Web UI/UX |
| Mobile Dev | App móvil |
| QA | Testing, auditoría |

---

## ✅ Criterios de Aceptación (MVP Ready)

- [x] API funcional con autenticación
- [x] Dashboard web operacional
- [x] App móvil usable en Expo Go
- [x] Trazabilidad de transacciones
- [x] Documentación completa (README + API Docs)
- [x] Repositorio público con Issues
- [x] Despliegue gratis en Vercel + Render + Supabase

---

**Documento Versión**: 1.0  
**Última Actualización**: Mayo 2026  
**Estado**: Aprobado para MVP
