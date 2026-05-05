# 🤝 Guía de Contribución - Natillera App

Gracias por tu interés en contribuir a Natillera App. Este documento explica nuestro proceso de desarrollo y cómo puedes participar.

## 📋 Tabla de Contenidos

1. [Filosofía del Proyecto](#filosofía-del-proyecto)
2. [Como Empezar](#como-empezar)
3. [Flujo de Desarrollo](#flujo-de-desarrollo)
4. [Commits y PRs](#commits-y-prs)
5. [Estándares de Código](#estándares-de-código)
6. [Testing](#testing)

---

## 🎯 Filosofía del Proyecto

**Natillera App** se desarrolla con estos principios:

- **Velocidad MVP**: Priorizar features funcionales sobre perfección
- **Documentación Clara**: Todo debe ser fácil de entender
- **Desarrollo Ágil**: Iteraciones cortas, feedback rápido
- **Metodología OpenCode**: Planificación → Arquitectura → Desarrollo → Testing → Deploy
- **Comunidad**: Acogemos diferentes niveles de experiencia

---

## 🚀 Como Empezar

### 1. Fork y Clone

```bash
# Fork en GitHub
# Luego clona tu fork
git clone https://github.com/TU_USUARIO/natillera-app.git
cd natillera-app
```

### 2. Setup Local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Mobile
cd ../mobile
npm install
```

### 3. Crea una rama

```bash
# Siempre desde dev
git checkout dev
git pull origin dev
git checkout -b feat/tu-feature-name
```

---

## 🔄 Flujo de Desarrollo

### 1. Selecciona un Issue

- Ve a [Issues](https://github.com/tu-repo/natillera-app/issues)
- Busca issues con label `good first issue` si es tu primer PR
- Comenta: "Estoy trabajando en esto"
- Se asignará automáticamente

### 2. Entiende el Contexto

- Lee el Issue completamente
- Revisa los Criterios de Aceptación
- Lee documentación relacionada
- Pregunta si tienes dudas (no es vergüenza)

### 3. Develop Localmente

```bash
# Backend example
cd backend

# Crea un archivo para tu feature
touch app/services/mi_feature.py

# Escribe código
# Corre tests localmente
pytest

# Verifica estilos
black app/
pylint app/
```

### 4. Commiteate

```bash
# Commits semánticos:
git add .
git commit -m "feat: add natillera distribution logic"
# o
git commit -m "fix: incorrect balance calculation"
# o
git commit -m "docs: update API endpoints"
```

### 5. Pushea tu rama

```bash
git push origin feat/tu-feature-name
```

### 6. Crea Pull Request

- En GitHub, verás un botón "Create Pull Request"
- Llena la descripción (usa template si existe)
- Proporciona contexto y referencias (Issue #123)
- Aguarda revisión

---

## 💬 Commits y PRs

### Tipos de Commits (Conventional Commits)

```
feat:     Nueva funcionalidad
fix:      Arregla un bug
docs:     Cambios en documentación
style:    Cambios de formato (no afecta lógica)
refactor: Refactorización de código
test:     Agregar o actualizar tests
chore:    Cambios en build, deps, etc
```

### Ejemplos

```bash
git commit -m "feat: add JWT authentication endpoints"
git commit -m "fix: resolve null pointer in transaction calculation"
git commit -m "docs: update README with setup instructions"
git commit -m "test: add tests for natillera creation"
git commit -m "refactor: extract auth logic to separate module"
```

### Pull Request Template

```markdown
## Descripción
Breve descripción de los cambios

## Issue Relacionado
Fixes #123

## Cambios Realizados
- [ ] Cambio 1
- [ ] Cambio 2
- [ ] Cambio 3

## Como Testear
1. Paso 1
2. Paso 2

## Checklist
- [ ] Los tests pasan
- [ ] Code está formateado
- [ ] Documentación actualizada
- [ ] No hay warnings
```

---

## 📝 Estándares de Código

### Backend (Python + FastAPI)

```python
# ✅ Good
def calculate_total_collected(natillera_id: int) -> float:
    """
    Calculate total amount collected for a natillera.
    
    Args:
        natillera_id: The natillera identifier
        
    Returns:
        Total amount as float
    """
    transactions = db.query(Transaction).filter(
        Transaction.natillera_id == natillera_id,
        Transaction.status == "confirmed"
    ).all()
    return sum(t.amount for t in transactions)

# ❌ Bad
def calc(nid):
    t = db.query(Transaction).filter(Transaction.natillera_id == nid).all()
    return sum([x.amount for x in t])
```

**Reglas:**
- Usa type hints: `def func(param: int) -> str:`
- Docstrings en cada función
- Max 88 caracteres por línea (Black formatter)
- Nombres descriptivos de variables
- Manejo de excepciones explícito

### Frontend (React + JavaScript)

```javascript
// ✅ Good
export const NatilleraCard = ({ natillera, onEdit, onDelete }) => {
  const handleDelete = async () => {
    if (window.confirm('Are you sure?')) {
      await api.delete(`/natilleras/${natillera.id}`)
      onDelete(natillera.id)
    }
  }

  return (
    <div className="p-4 border rounded-lg">
      <h3 className="text-lg font-bold">{natillera.name}</h3>
      <p>{natillera.description}</p>
      <button onClick={onEdit}>Edit</button>
      <button onClick={handleDelete}>Delete</button>
    </div>
  )
}

// ❌ Bad
export const Card = (props) => {
  return (
    <div>
      <h3>{props.n.nm}</h3>
      <button onClick={() => delete_item(props.n.id)}>X</button>
    </div>
  )
}
```

**Reglas:**
- Nombres de componentes en PascalCase
- Props descriptivos
- Comments en lógica compleja
- Destructuring cuando sea posible
- Evitar inline styles (usa Tailwind)

### Mobile (React Native)

```javascript
// ✅ Good
const DashboardScreen = ({ navigation }) => {
  const [natilleras, setNatilleras] = React.useState([])
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    fetchNatilleras()
  }, [])

  const fetchNatilleras = async () => {
    try {
      const response = await api.get('/natilleras')
      setNatilleras(response.data)
    } catch (error) {
      console.error('Error fetching natilleras:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <View style={styles.container}>
      {loading ? <ActivityIndicator /> : <NatilleraList data={natilleras} />}
    </View>
  )
}
```

---

## 🧪 Testing

### Backend

```bash
# Corre todos los tests
pytest

# Específico test
pytest tests/test_auth.py::test_login_success

# Con coverage
pytest --cov=app --cov-report=html
```

**Escribe tests para:**
- Nuevos endpoints
- Lógica de negocio compleja
- Edge cases

### Frontend

```bash
# Corre tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

### Checklist Pre-Push

Antes de hacer push:

```bash
# 1. Backend
cd backend
pytest --cov=app
black app/
pylint app/

# 2. Frontend  
cd ../frontend
npm run lint
npm test

# 3. Mobile
cd ../mobile
npm run lint
```

---

## ✅ Checklist para Revisor

Cuando hagas review de otros PRs:

- ¿El código cumple el Issue?
- ¿Hay tests?
- ¿Está documentado?
- ¿Hay errores de lógica?
- ¿El código es mantenible?
- ¿Sigue los estándares?

---

## 📚 Recursos Útiles

- [CLIENT_BRIEF.md](./CLIENT_BRIEF.md) - Contexto del proyecto
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Diseño técnico
- [API_DOCS.md](./docs/API_DOCS.md) - Endpoints
- [DEVELOPMENT.md](./docs/DEVELOPMENT.md) - Setup local
- [Issues](https://github.com/tu-repo/natillera-app/issues) - Tareas

---

## 💪 Tips para Contribuidores

1. **Comienza pequeño**: Primeros PRs deben ser simples
2. **Pregunta dudas**: Es mejor preguntar que asumir
3. **Revisa otros PRs**: Aprende del código de otros
4. **Rebase antes de PR**: `git rebase origin/dev`
5. **Actualiza frecuentemente**: `git pull origin dev`
6. **Comunica progreso**: Comenta en issues regularmente

---

## 🐛 Reportar Bugs

Si encuentras un bug:

1. Verifica que no esté reportado
2. Crea un Issue con template "Bug Report"
3. Describe: Qué pasó, qué esperabas, pasos para reproducir
4. Añade screenshots si es posible
5. Incluye versión y SO

---

## 💬 Preguntas

- Discord: [Enlace]
- Discussions en GitHub
- Email: [email del proyecto]

---

**¡Gracias por contribuir! 🙌**

Cada PR, no importa cuán pequeño, hace a Natillera App mejor.

---

*Última actualización: Mayo 2026*
