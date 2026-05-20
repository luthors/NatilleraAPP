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

### Fase: MVP Backend (pendiente)

| Hash | Fecha | Tipo | Descripción | Issues | HU |
|------|-------|------|-------------|--------|-----|
| — | — | `chore` | Setup FastAPI base with layered architecture and domain exceptions | ISSUE-01 | — |
| — | — | `chore(db)` | Add SQLAlchemy models, Alembic migrations and database indexes | ISSUE-02 | — |
| — | — | `chore` | Implement Repository layer base classes and all concrete repos | ISSUE-03 | — |
| — | — | `feat(auth)` | Implement user registration with bcrypt hashing and email validation | ISSUE-04 | HU-01-01 |
| — | — | `feat(auth)` | Implement login, refresh token rotation and logout with invalidation | ISSUE-05 | HU-01-02, HU-01-03 |
| — | — | `feat(auth)` | Implement password recovery with single-use time-limited token | ISSUE-06 | HU-01-04 |
| — | — | `feat(users)` | Add GET and PUT /users/me endpoints with photo upload | ISSUE-07 | HU-01-05 |
| — | — | `feat(natilleras)` | Implement natillera creation, period calendar generation and activation | ISSUE-09 | HU-02-01, HU-02-06 |
| — | — | `feat(natilleras)` | Add natillera list, detail and edit endpoints with role-based views | ISSUE-10 | HU-02-02 a 02-05 |
| — | — | `feat(natilleras)` | Implement natillera close and archive lifecycle transitions | ISSUE-11 | HU-02-07, HU-02-08 |
| — | — | `feat(socios)` | Implement invitation system with 48h single-use token via email | ISSUE-12 | HU-03-01, HU-03-02 |
| — | — | `feat(socios)` | Add socio list, suspend and delete endpoints with RN-09 enforcement | ISSUE-13 | HU-03-03 a 03-05 |
| — | — | `feat(pagos)` | Implement admin payment registration with atomic fund balance update | ISSUE-15 | HU-04-01 |
| — | — | `feat(pagos)` | Implement socio payment submission and admin confirm/reject flow | ISSUE-16 | HU-04-02, HU-04-03 |
| — | — | `feat(pagos)` | Implement payment reversal with immutable audit trail (RN-06) | ISSUE-17 | HU-04-04 |
| — | — | `feat(saldos)` | Add fund balance calculation service and nightly mora detection job | ISSUE-19 | HU-05-01, HU-05-02, HU-05-04 |
| — | — | `feat(saldos)` | Add paginated transaction history with role-based access control | ISSUE-20 | HU-05-03 |
| — | — | `feat(distribuciones)` | Implement final distribution preview and execution with RN-07 guard | ISSUE-22 | HU-06-02 |
| — | — | `feat(notificaciones)` | Implement event-driven notification system with email handlers | ISSUE-23 | HU-07-01 a 07-03 |
| — | — | `feat(reportes)` | Generate PDF payment receipt with unique reference and QR code | ISSUE-25 | HU-08-01 |
| — | — | `feat(audit)` | Add immutable audit log with PostgreSQL trigger as second guard | ISSUE-27 | HU-09-01 |

---

### Fase: MVP Frontend (pendiente)

| Hash | Fecha | Tipo | Descripción | Issues | HU |
|------|-------|------|-------------|--------|-----|
| — | — | `chore(frontend)` | Setup feature-based folder structure, Axios client and TanStack Query | ISSUE-29 | — |
| — | — | `feat(frontend)` | Implement login, register and password recovery UI | ISSUE-30 | HU-01-01 a 01-04 |
| — | — | `feat(frontend)` | Add natillera dashboard cards and detail page with role-based tabs | ISSUE-31 | HU-02-02 a 02-04 |
| — | — | `feat(frontend)` | Add natillera creation form, activation and close confirmation modal | ISSUE-32 | HU-02-01, 02-05 a 02-07 |
| — | — | `feat(frontend)` | Add socio management: list, invite form and invitation acceptance page | ISSUE-33 | HU-03-01 a 03-05 |
| — | — | `feat(frontend)` | Implement payment registration, confirm/reject flow and history table | ISSUE-34 | HU-04-01 a 04-04 |
| — | — | `feat(frontend)` | Add final distribution preview and confirmation UI | ISSUE-35 | HU-06-02 |

---

### Fase: MVP Mobile (pendiente)

| Hash | Fecha | Tipo | Descripción | Issues | HU |
|------|-------|------|-------------|--------|-----|
| — | — | `chore(mobile)` | Setup React Navigation, SecureStore token storage and Axios client | ISSUE-36 | — |
| — | — | `feat(mobile)` | Add login and register screens with SecureStore token persistence | ISSUE-37 | HU-01-01, HU-01-02 |
| — | — | `feat(mobile)` | Add dashboard and natillera detail screens with pull-to-refresh | ISSUE-38 | HU-02-02, HU-02-04 |
| — | — | `feat(mobile)` | Add payment registration screen with image picker for receipt | ISSUE-39 | HU-04-02 |

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
| Total commits | 6 |
| Commits docs | 6 |
| Commits feat | 0 |
| Commits test | 0 |
| Issues implementados | 0 / 47 |
| HU completadas | 0 / 35+ |

> Actualizar esta tabla con cada commit.
