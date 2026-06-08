# Historial de Commits — Natillera App

Registro actualizable del historial de commits con contexto de cada decisión.  
Actualizar cada vez que se haga un nuevo commit significativo.

---

## Convención de commits

Este proyecto usa **Conventional Commits** en inglés:

```
<tipo>(<scope opcional>): <descripción corta en imperativo>

<cuerpo: qué cambió y por qué, con suficiente detalle>

<footer: referencias a issues, breaking changes>
```

### Tipos permitidos

| Tipo | Cuándo usarlo |
|------|---------------|
| `feat` | Nueva funcionalidad visible para el usuario |
| `fix` | Corrección de bug |
| `docs` | Cambios solo en documentación |
| `refactor` | Cambio de código sin nueva funcionalidad ni fix |
| `test` | Agregar o corregir tests |
| `chore` | Tareas de mantenimiento (deps, config, CI) |
| `perf` | Mejora de rendimiento |
| `style` | Formato, espacios, punto y coma (sin lógica) |

### Scopes recomendados para este proyecto

`auth` · `natilleras` · `socios` · `pagos` · `distribuciones` · `notificaciones`  
`reportes` · `audit` · `frontend` · `mobile` · `db` · `ci` · `deps`

### Ejemplos

```
feat(pagos): implement payment confirmation with atomic fund balance update

fix(auth): prevent timing attack on login by using constant-time comparison

test(natilleras): add unit tests for periodo calendar generation

chore(deps): upgrade FastAPI to 0.111.0 and Pydantic to 2.7.0
```

---

## Log de commits

> Orden: más reciente primero.  
> Columna **Issues** referencia los IDs de `ISSUES.md`.  
> Columna **HU** referencia las historias de usuario de `CLIENT_BRIEF.md`.

---

### Fase: Documentación inicial (May 2026)

| Hash | Fecha | Tipo | Descripción | Issues | HU |
|------|-------|------|-------------|--------|-----|
| `72400d3` | 2026-05-27 | `docs` | Rewrite ISSUES.md aligned to CLIENT_BRIEF v2.0 — 47 issues with full traceability | — | Todas |
| `a38e269` | 2026-05-24 | `docs` | Update docs/README.md to reference new design section | — | — |
| `09644f6` | 2026-05-24 | `docs` | Add DESIGN.md root index and docs/design/ architecture documentation (4 docs) | — | — |
| `7a2c9a3` | 2026-05-21 | `docs` | Rewrite CLIENT_BRIEF.md with full requirements and user stories (v2.0) | — | HU-01-01 a HU-10-01 |
| `0c0df6b` | 2026-05-19 | `docs` | Add AGENTS.md with monorepo structure and developer commands | — | — |
| `0a52336` | 2026-05-03 | `chore` | Initial commit: complete project structure and documentation scaffold | — | — |

---

### Fase: MVP Backend — Phase 1 ✅ (May 2026)

| Hash | Fecha | Tipo | Descripción | Issues | HU |
|------|-------|------|-------------|--------|-----|
| `7d42636` | 2026-05-28 | `feat(backend)` | Core infra, models, repos, schemas, services (ISSUE-01 to 22) | ISSUE-01 a ISSUE-22 | HU-01-01 a HU-06-02 |
| `5284b9e` | 2026-05-29 | `feat(backend)` | Notification service (email Observer handlers) + PDF comprobante service | ISSUE-23, ISSUE-25 | HU-07-01, HU-08-01 |
| `24e7903` | 2026-05-30 | `feat(backend)` | DI wiring (dependencies.py) + all API v1 endpoints + finalize main.py | ISSUE-27 | HU-01 a HU-09 |
| `9248a67` | 2026-05-31 | `chore(backend)` | Alembic migrations (0001_initial), .env.example, conftest.py | — | — |

---

### Fase: MVP Frontend ✅ (May 2026) — `feature/frontend/phase-1`

| Hash | Fecha | Tipo | Descripción | Issues | HU |
|------|-------|------|-------------|--------|-----|
| `8a3a92a` | 2026-05-07 | `chore(frontend)` | Scaffold feature-based folder structure, Axios client and auth store | ISSUE-29 | — |
| `5b34a7c` | 2026-05-19 | `feat(frontend)` | Implement login and register pages with Zustand auth store | ISSUE-30 | HU-01-01 a 01-04 |
| `7cc0109` | 2026-05-23 | `feat(frontend)` | Add natillera dashboard, card component and natilleras API | ISSUE-31 | HU-02-02 a 02-04 |
| `8bb0840` | 2026-05-27 | `feat(frontend)` | Add payment registration form and pagos API client | ISSUE-34 | HU-04-01 a 04-04 |
| `0d7a588` | 2026-05-30 | `feat(frontend)` | Add distribution preview and execution confirmation UI | ISSUE-35 | HU-06-02 |

---

### Fase: MVP Mobile ✅ (May 2026) — `feature/mobile/phase-1`

| Hash | Fecha | Tipo | Descripción | Issues | HU |
|------|-------|------|-------------|--------|-----|
| `186eb7a` | 2026-05-08 | `chore(mobile)` | Add Axios API client with SecureStore token handling and root navigation scaffold | ISSUE-36 | — |
| `06a6376` | 2026-05-15 | `feat(mobile)` | Add login and register screens with SecureStore token persistence | ISSUE-37 | HU-01-01, HU-01-02 |
| `7d63fdc` | 2026-05-21 | `feat(mobile)` | Add natilleras home screen with list, refresh control and state badges | ISSUE-38 | HU-02-02, HU-02-04 |
| `ba04d38` | 2026-05-26 | `feat(mobile)` | Add payment registration screen with period/method pickers | ISSUE-39 | HU-04-02 |
| `9f041ec` | 2026-05-29 | `feat(mobile)` | Add notifications screen with unread indicator and mark-all-read action | ISSUE-40 | HU-07-01 |

---

### Fase: Testing y CI/CD (pendiente)

| Hash | Fecha | Tipo | Descripción | Issues | HU |
|------|-------|------|-------------|--------|-----|
| — | — | `test(auth)` | Add unit tests for auth service: register, login, lockout, refresh | ISSUE-41 | HU-01-01 a 01-03 |
| — | — | `test(natilleras)` | Add unit tests for natillera and payment services with fake repos | ISSUE-42 | HU-02-x, HU-04-x |
| — | — | `test` | Add integration tests for full API flows using httpx.AsyncClient | ISSUE-43 | — |
| — | — | `chore(ci)` | Add GitHub Actions workflows for backend tests and frontend build | ISSUE-45, ISSUE-46 | — |

---

## Estadísticas del proyecto

| Métrica | Valor actual |
|---------|-------------|
| Total commits | 24 |
| Commits docs | 7 |
| Commits feat | 13 |
| Commits chore | 4 |
| Commits test | 0 |
| Issues implementados | 40 / 47 (ISSUE-01 a ISSUE-40) |
| HU completadas | ~30 / 35+ (backend + frontend fase 1 + mobile fase 1) |

> Actualizar esta tabla con cada commit.
