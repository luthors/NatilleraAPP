# 🚀 GUÍA PARA SUBIR A GITHUB

## ✅ Checklist Antes de Subir

### 1. Preparar Repositorio Local
```bash
cd natillera-app

# Inicializar git si no está
git init

# Agregar todos los archivos
git add .

# Crear primer commit
git commit -m "Initial commit: Natillera App project structure and documentation"

# Ver status
git status
```

### 2. Crear Repositorio en GitHub
1. Ve a https://github.com/new
2. Nombre: `natillera-app` o tu variante
3. Descripción: "Digital platform for Colombian savings groups (natilleras)"
4. Selecciona: Public (para proyecto académico)
5. NO inicialices con README.md (ya tenemos uno)
6. Clic en "Create repository"

### 3. Conectar y Pushear

```bash
# Conectar repositorio remoto
git remote add origin https://github.com/TU_USUARIO/natillera-app.git

# Cambiar rama default a main si está como master
git branch -M main

# Pushear
git push -u origin main

# Verificar
git remote -v
```

---

## 📋 Archivos a Incluir en GitHub

**Incluir:**
- ✅ README.md
- ✅ CLIENT_BRIEF.md
- ✅ ARCHITECTURE.md
- ✅ CONTRIBUTING.md
- ✅ ISSUES.md
- ✅ ENTREGA_INICIAL.md
- ✅ .gitignore
- ✅ Carpeta backend/ (código + configs)
- ✅ Carpeta frontend/ (código + configs)
- ✅ Carpeta mobile/ (código + configs)
- ✅ Carpeta docs/ (documentación)
- ✅ Carpeta .github/ (para CI/CD futuro)

**NO Incluir:**
- ❌ .env (usar .env.example)
- ❌ node_modules/
- ❌ __pycache__/
- ❌ venv/ o env/
- ❌ .DS_Store

*(Estos ya están en .gitignore)*

---

## 🏷️ Crear Labels en GitHub

Después de crear el repositorio, ve a la pestaña "Issues" y crea estos labels:

| Label | Color | Descripción |
|-------|-------|-------------|
| `backend` | 1f77b4 | Trabajo en backend |
| `frontend` | 0e7c0e | Trabajo en frontend |
| `mobile` | 6f42c1 | Trabajo en mobile |
| `docs` | ffd700 | Documentación |
| `bug` | d73a49 | Bug report |
| `feature` | a2eeef | Nueva funcionalidad |
| `enhancement` | 84b6eb | Mejora a feature existente |
| `good first issue` | 7057ff | Para nuevos contribuidores |
| `devops` | 0366d6 | CI/CD, deployment |
| `testing` | e10c02 | Testing y QA |
| `security` | 5319e7 | Seguridad |
| `UI/UX` | d4af37 | Interfaz de usuario |
| `help wanted` | ff1493 | Se necesita ayuda |

---

## 🎯 Crear Issues en GitHub

Después de pushear, crea los 30 issues documentados en `ISSUES.md`:

```bash
# Puedes hacerlo manualmente desde la interfaz:
# 1. Ve a Issues tab
# 2. Click "New Issue"
# 3. Copia del archivo ISSUES.md
# 4. Pega los detalles
# 5. Asigna labels y complejidad
```

**O automatizado con GitHub CLI:**
```bash
# Instalar gh CLI
# Luego autenticar:
gh auth login

# Crear issue (ejemplo)
gh issue create \
  --title "Setup FastAPI base with CORS" \
  --body "Tareas:..." \
  --label backend,setup \
  --projects "Natillera MVP"
```

---

## 📊 Configurar Tablero de Proyecto

1. Ve a "Projects" en GitHub
2. Haz click en "New project"
3. Usa template "Table"
4. Nombre: "Natillera MVP - Fase 1"
5. Agrega columns: To Do, In Progress, In Review, Done
6. Linkea todos los issues creados

---

## 🔐 Proteger Ramas

Para un proyecto profesional:

1. Ve a Settings → Branches
2. Haz click "Add rule"
3. Nombre de rama: `main`
4. Habilita:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1)
   - ✅ Require status checks to pass

---

## 📝 Crear Primeros Archivos Auxiliares

### 1. LICENSE

```bash
# Descargar licencia MIT
curl https://opensource.org/licenses/MIT > LICENSE
```

O crear manualmente con licencia MIT.

### 2. .github/PULL_REQUEST_TEMPLATE.md

```markdown
## Descripción
Breve descripción de cambios

## Issue Relacionado
Fixes #123

## Tipo de Cambio
- [ ] Bug fix
- [ ] Nueva feature
- [ ] Breaking change
- [ ] Documentación

## Checklist
- [ ] Tests pasan
- [ ] Documentación actualizada
- [ ] Code formateado
```

### 3. .github/ISSUE_TEMPLATE/bug_report.md

Crear template para reportar bugs.

---

## 🔔 Configurar Notificaciones

1. Ve a Settings de tu cuenta GitHub
2. Notificaciones → Email
3. Configura alertas para:
   - Issues donde se menciona tu usuario
   - Pull requests asignados a ti
   - Discusiones en tu repositorio

---

## 📈 Primeros Commits

Despues de crear el repo, puedes hacer commits temáticos:

```bash
# Commit 1: Documentación
git commit -m "docs: Add project documentation and client brief"

# Commit 2: Backend setup
git commit -m "feat: Add backend project structure with FastAPI"

# Commit 3: Frontend setup
git commit -m "feat: Add frontend project structure with React + Vite"

# Commit 4: Mobile setup
git commit -m "feat: Add mobile project structure with React Native + Expo"

# Ver historial
git log --oneline
```

---

## 🚀 Verificar en GitHub

Después de pushear, verifica que todo esté bien:

1. ✅ README.md se muestra en la página principal
2. ✅ Todos los archivos están presentes
3. ✅ .gitignore funciona (no hay node_modules/ etc)
4. ✅ Puedes navegar las carpetas
5. ✅ Code view muestra el código correctamente

---

## 🔗 Compartir Enlace del Proyecto

Una vez en GitHub, comparte el link:
```
https://github.com/TU_USUARIO/natillera-app
```

---

## 📋 Entregar Proyecto Académico

### En la plataforma educativa, entrega:

1. **Link del Repositorio**
   ```
   https://github.com/tu-usuario/natillera-app
   ```

2. **Resumen en README**
   - ✅ Ya está completo en `README.md`

3. **Link a Issues**
   ```
   https://github.com/tu-usuario/natillera-app/issues
   ```

4. **Resumen de Estructura**
   - ✅ Documentado en `ARCHITECTURE.md`

5. **Client Brief**
   - ✅ Disponible en `CLIENT_BRIEF.md`

---

## ⚠️ Cosas a Recordar

- **NO subas .env** - Solo .env.example
- **NO subas node_modules/** - Git lo ignora
- **NO subas venv/** - Git lo ignora
- **Documenta TODO** - Código sin documentar es código muerto
- **Commits claros** - Usa semantic commits
- **README actualizado** - Primera impresión
- **Issues bien escritas** - Facilita contribuciones

---

## 🎓 Criterios de Evaluación Verificados

✅ **Client Brief (25%)**
- Documento `CLIENT_BRIEF.md` - 200+ líneas
- Usuarios, features, timeline definidos

✅ **Estructura del Proyecto (50%)**
- Profesional y escalable
- README claro con 400+ líneas
- ARCHITECTURE.md con diagramas
- Carpetas bien organizadas

✅ **Avance Inicial del Código (25%)**
- Backend: main.py, database.py, config.py funcionales
- Frontend: App.jsx, contextos, servicios básicos
- Mobile: app.json, package.json listos
- Todos los archivos de configuración presentes

---

## 🎉 ¡Listo!

Tu proyecto Natillera App está 100% listo para:
1. Subirlo a GitHub
2. Presentarlo académicamente
3. Continuar desarrollando
4. Invitar colaboradores

**Próximo paso**: Comenzar a trabajar en los Issues del Numeral 1 (Backend core)

---

*Guía creada: Mayo 2026*  
*Versión: 1.0*  
*Estado: Listo para GitHub*
