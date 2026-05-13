# Diseño y Arquitectura — Índice

Documentación técnica de decisiones de arquitectura, patrones y convenciones de código para **Natillera App**.

> Este directorio se actualiza a medida que el proyecto avanza. Cada documento responde a decisiones reales tomadas durante el desarrollo.

---

## Documentos

| # | Documento | Qué resuelve |
|---|-----------|-------------|
| 01 | [Arquitectura de Capas — Backend](./01-arquitectura-capas.md) | Cómo separar API, servicios, repositorios y modelos en FastAPI |
| 02 | [Patrones de Diseño](./02-patrones-diseno.md) | Repository, Unit of Work, Strategy, Observer y Dependency Injection |
| 03 | [Clean Code](./03-clean-code.md) | Convenciones de nombres, funciones, comentarios y manejo de errores |
| 04 | [Arquitectura Frontend](./04-frontend-arquitectura.md) | Feature-based structure, TanStack Query, Zustand, manejo de montos |

---

## Cuándo consultar cada documento

- **Antes de crear un nuevo endpoint** → `01-arquitectura-capas.md`
- **Antes de agregar un método de pago** → `02-patrones-diseno.md` (Strategy)
- **Al revisar un PR** → `03-clean-code.md`
- **Al crear un nuevo componente React** → `04-frontend-arquitectura.md`
- **Al decidir dónde va una regla de negocio** → `01-arquitectura-capas.md` + `CLIENT_BRIEF.md`
