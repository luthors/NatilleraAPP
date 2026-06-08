# GIT WORKFLOW — NatilleraApp

## Estrategia: GitFlow

Se eligió **GitFlow** sobre Trunk-Based Development por las siguientes razones:

- Las tres sub-aplicaciones (backend, frontend, mobile) son esfuerzos independientes de varias semanas
- No existe CI/CD activo aún — TBD requiere pipelines sólidos para ser seguro
- El proyecto tiene fases de entrega bien definidas que mapean naturalmente a `release/*`
- El historial explícito de GitFlow facilita la trazabilidad académica

---

## Colaboradores y asignaciones

| Rol | Usuario Git | Email | Sub-proyecto |
|-----|------------|-------|--------------|
| **Backend Lead** | Luis Gregorio Toro Amador - Luthors | `luis.g.toro@gmail.com` | `backend/` |
| **Frontend Lead** | Luis Toro | `luthors@hotmail.com` | `frontend/` |
| **Mobile Lead** | LUIS GREGORIO TORO AMADOR | `ltoro@qvision.us` | `mobile/` |

---

## Estructura de ramas

```
main                          ← producción — solo merge desde release/* o hotfix/*
│
└── develop                   ← integración — todos los features se integran aquí
    │
    ├── feature/backend/*     ← commits del Backend Lead
    ├── feature/frontend/*    ← commits del Frontend Lead
    ├── feature/mobile/*      ← commits del Mobile Lead
    │
    ├── release/v1.0.0        ← (cuando se prepara un release)
    └── hotfix/*              ← correcciones urgentes sobre main
```

### Convención de nombres de ramas

```
feature/<sub-proyecto>/<descripcion-corta>
release/v<MAJOR>.<MINOR>.<PATCH>
hotfix/<descripcion-corta>
```

**Ejemplos:**
```
feature/backend/auth-endpoints
feature/backend/payment-pdf-receipt
feature/frontend/login-page
feature/frontend/natillera-dashboard
feature/mobile/payment-screen
hotfix/fix-token-expiry-check
release/v1.0.0
```

---

## Cambiar de identidad Git

Antes de hacer cualquier commit, activa la identidad correcta para tu sub-proyecto.
Este script modifica **solo el config local** del repositorio (`--local`), sin tocar `~/.gitconfig`.

```powershell
# Desde la raíz del repositorio:

.\scripts\switch-git-user.ps1 backend    # Backend Lead
.\scripts\switch-git-user.ps1 frontend   # Frontend Lead
.\scripts\switch-git-user.ps1 mobile     # Mobile Lead

.\scripts\switch-git-user.ps1            # Ver identidad actual
```

**Verificar:**
```powershell
git config --local user.name
git config --local user.email
```

---

## Flujo completo paso a paso

### 1. Iniciar trabajo en una feature

```powershell
# Cambiar a la identidad correcta
.\scripts\switch-git-user.ps1 frontend

# Partir siempre desde develop actualizado
git checkout develop
git pull origin develop

# Crear la rama de feature
git checkout -b feature/frontend/natillera-dashboard
```

### 2. Trabajar y hacer commits

```powershell
# Commits con formato Conventional Commits en inglés
git add frontend/src/features/natilleras/
git commit -m "feat(frontend): add natillera dashboard card component

- NatilleraCard shows nombre, estado, monto_por_periodo
- Clickable — navigates to /natilleras/:id
- Skeleton loader while fetching

Closes ISSUE-31"
```

### 3. Publicar la rama

```powershell
git push -u origin feature/frontend/natillera-dashboard
```

### 4. Abrir Pull Request → develop

- **Base:** `develop`
- **Compare:** `feature/frontend/natillera-dashboard`
- **Título:** igual al commit principal (Conventional Commits)
- **Descripción:** lista de cambios + issues cerrados
- **Reviewers:** al menos 1 de los otros colaboradores
- **Labels:** `frontend` | `backend` | `mobile`

### 5. Después del merge

```powershell
git checkout develop
git pull origin develop
git branch -d feature/frontend/natillera-dashboard   # limpiar local
```

### 6. Preparar un release

```powershell
# Solo el Backend Lead / Tech Lead prepara releases
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# Bumps de versión, últimas correcciones...
git commit -m "chore(release): bump version to 1.0.0"

# Merge a main y a develop
git checkout main
git merge --no-ff release/v1.0.0 -m "chore: release v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0 — MVP Phase 1 (backend complete)"

git checkout develop
git merge --no-ff release/v1.0.0 -m "chore: merge release/v1.0.0 back into develop"
git branch -d release/v1.0.0

git push origin main develop --tags
```

### 7. Hotfix sobre producción

```powershell
git checkout main
git pull origin main
git checkout -b hotfix/fix-token-expiry

# Corrección...
git commit -m "fix(auth): correct refresh token expiry comparison (timezone-aware)"

git checkout main
git merge --no-ff hotfix/fix-token-expiry
git tag -a v1.0.1 -m "Hotfix v1.0.1"

git checkout develop
git merge --no-ff hotfix/fix-token-expiry
git branch -d hotfix/fix-token-expiry

git push origin main develop --tags
```

---

## Ramas activas — Phase 1

| Rama | Responsable | Estado |
|------|------------|--------|
| `main` | Tech Lead | ✅ producción |
| `develop` | Todos | ✅ activa — integración |
| `feature/backend/phase-1` | Backend Lead | ✅ completa — pendiente PR→develop |
| `feature/frontend/phase-1` | Frontend Lead | 🟡 en desarrollo |
| `feature/mobile/phase-1` | Mobile Lead | 🟡 en desarrollo |

---

## Reglas de protección de ramas (GitHub)

Configurar en **GitHub → Settings → Branches** para `main` y `develop`:

| Regla | main | develop |
|-------|------|---------|
| Require pull request before merging | ✅ | ✅ |
| Required approving reviews | 1 | 1 |
| Dismiss stale reviews on push | ✅ | ✅ |
| Require status checks to pass | ✅ (cuando haya CI) | ✅ |
| Restrict direct pushes | ✅ | ✅ |
| Include administrators | ✅ | — |

---

## Formato de commits

**Conventional Commits** en inglés:

```
<tipo>(<scope>): <descripción en imperativo, max 72 chars>

<cuerpo: qué cambió y por qué — opcional pero recomendado>

<footer: Closes ISSUE-XX, breaking changes — opcional>
```

### Tipos

| Tipo | Cuándo |
|------|--------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Solo documentación |
| `refactor` | Sin nueva funcionalidad ni fix |
| `test` | Tests nuevos o corregidos |
| `chore` | Mantenimiento (deps, config) |
| `perf` | Mejora de rendimiento |

### Scopes recomendados

`auth` · `natilleras` · `socios` · `pagos` · `distribuciones` · `reportes`  
`frontend` · `mobile` · `db` · `ci` · `deps` · `release`

### Ejemplos

```
feat(pagos): implement payment reversal with immutable audit trail (RN-06)

fix(auth): correct PasswordResetToken field name: used → usado

test(natilleras): add unit tests for period calendar generation

chore(deps): upgrade FastAPI to 0.111.0

docs(traceability): update commit history for phase 1 backend completion
```

---

## Labels de GitHub recomendados

| Label | Color | Descripción |
|-------|-------|-------------|
| `backend` | `#0075ca` | Cambios en backend/ |
| `frontend` | `#e4e669` | Cambios en frontend/ |
| `mobile` | `#cfd3d7` | Cambios en mobile/ |
| `bug` | `#d73a4a` | Bug confirmado |
| `enhancement` | `#a2eeef` | Nueva funcionalidad |
| `documentation` | `#0075ca` | Solo docs |
| `ready-for-review` | `#0e8a16` | PR listo para revisión |
| `in-progress` | `#e99695` | Trabajo en curso |

---

## Pull Request — template

Crear `.github/pull_request_template.md` con:

```markdown
## Descripción
<!-- Qué cambió y por qué -->

## Issues cerrados
Closes #<!-- número -->

## Tipo de cambio
- [ ] feat — nueva funcionalidad
- [ ] fix — corrección de bug
- [ ] refactor
- [ ] docs
- [ ] chore

## Sub-proyecto
- [ ] backend
- [ ] frontend
- [ ] mobile

## Checklist
- [ ] El código sigue las convenciones del proyecto (ver AGENTS.md)
- [ ] Se probó localmente sin errores
- [ ] Se actualizó documentación si aplica
- [ ] Conventional Commit en el título del PR
```
