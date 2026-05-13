# Diseño y Arquitectura — Natillera App

Índice de toda la documentación técnica del proyecto. Punto de entrada para cualquier decisión de diseño, arquitectura o convención de código.

---

## Documentación técnica (`docs/design/`)

| Documento | Descripción |
|-----------|-------------|
| [01 — Arquitectura de Capas (Backend)](./docs/design/01-arquitectura-capas.md) | Separación API / Service / Repository / Model en FastAPI. Ejemplos concretos con casos de la natillera. |
| [02 — Patrones de Diseño](./docs/design/02-patrones-diseno.md) | Repository, Unit of Work, Strategy (métodos de pago), Observer (notificaciones), Dependency Injection. |
| [03 — Clean Code](./docs/design/03-clean-code.md) | Convenciones de nombres, funciones, comentarios, manejo de errores y uso de `Decimal` para montos. |
| [04 — Arquitectura Frontend](./docs/design/04-frontend-arquitectura.md) | Feature-based folder structure, TanStack Query vs Zustand, capa API con Axios, formateo de montos. |

---

## Documentación general (`docs/`)

| Documento | Descripción |
|-----------|-------------|
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Diagramas de arquitectura general, ER de base de datos, flujos de datos y endpoints. |
| [docs/README.md](./docs/README.md) | Índice de toda la carpeta `docs/`. |

---

## Documentos raíz del proyecto

| Documento | Descripción |
|-----------|-------------|
| [CLIENT_BRIEF.md](./CLIENT_BRIEF.md) | Requisitos, historias de usuario, reglas de negocio, casos de uso y backlog por fases. |
| [README.md](./README.md) | Quickstart, stack tecnológico y estructura del proyecto. |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Guía de contribución, branching y convención de commits. |
| [AGENTS.md](./AGENTS.md) | Instrucciones para agentes de IA que trabajen en este repositorio. |

---

## Cómo mantener este documento actualizado

Cuando se tome una decisión técnica importante durante el desarrollo:

1. Agregarla al documento correspondiente en `docs/design/`.
2. Si es un documento nuevo, agregarlo a la tabla de arriba con una descripción de una línea.
3. Hacer commit con `docs: actualizar decisión de arquitectura sobre [tema]`.
