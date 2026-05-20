# Traceability — Natillera App

Documentación de trazabilidad del proyecto. Registra el hilo completo entre requisito, historia de usuario, issue de desarrollo y commit de código.

---

## Propósito

Mantener visibilidad sobre **qué se hizo, por qué y cuándo** a lo largo del ciclo de vida del proyecto. Útil para:

- Auditorías del proceso de desarrollo
- Onboarding de nuevos miembros del equipo
- Identificar qué commit implementó una regla de negocio específica
- Revisión retrospectiva de decisiones técnicas

---

## Documentos

| # | Documento | Descripción |
|---|-----------|-------------|
| 01 | [commit-history.md](./01-commit-history.md) | Estrategia de commits, convenciones y log actualizable |
| 02 | [hu-issues-matrix.md](./02-hu-issues-matrix.md) | Matriz de trazabilidad: HU → Issue → Commit → Archivo |

---

## Cómo mantener esta sección actualizada

| Evento | Acción |
|--------|--------|
| Se hace un nuevo commit | Agregar entrada en `01-commit-history.md` |
| Se implementa un issue | Actualizar fila en `02-hu-issues-matrix.md` con hash del commit |
| Se crea una nueva HU | Agregar fila pendiente en `02-hu-issues-matrix.md` |
| Se toma una decisión técnica importante | Documentarla en `docs/design/` y referenciar desde la matriz |
