# Clean Code — Convenciones del Proyecto

**Aplica a**: todos los sub-proyectos  
**Última actualización**: Junio 2026

---

## Principio guía

> El código se lee 10 veces más de lo que se escribe. En una app financiera, el código ambiguo genera bugs que cuestan dinero real.

---

## Python / Backend

### Nombres

```python
# MAL
def proc(n_id, a_id, m):
    ...

# BIEN
def confirmar_pago(natillera_id: int, admin_id: int, monto: int) -> Pago:
    ...
```

```python
# MAL — variable de loop sin semántica
for x in natilleras:
    if x.status == 1:
        ...

# BIEN
for natillera in natilleras:
    if natillera.esta_activa():
        ...
```

**Reglas de nomenclatura:**

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| Variables y funciones | `snake_case` | `confirmar_pago` |
| Clases | `PascalCase` | `NatilleraService` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_SOCIOS_POR_NATILLERA = 50` |
| Archivos | `snake_case` | `pago_service.py` |
| Tablas en BD | `snake_case` plural | `natilleras`, `pagos` |

---

### Funciones

**Una función = una responsabilidad.** Si necesitas escribir "y" para describir qué hace, sepárala.

```python
# MAL — hace demasiado
def confirmar_pago_y_notificar_y_actualizar_saldo(pago_id, admin_id):
    ...

# BIEN — tres funciones, cada una con su responsabilidad
def confirmar_pago(pago_id: int, admin_id: int) -> Pago: ...
def actualizar_saldo_fondo(natillera_id: int, monto: int) -> None: ...
def notificar_confirmacion(pago: Pago) -> None: ...
```

**Longitud máxima recomendada**: 20 líneas. Si supera eso, probablemente hay que extraer lógica.

**Argumentos**: máximo 3-4 parámetros. Si necesitas más, usa un objeto Pydantic.

```python
# MAL
def crear_natillera(nombre, descripcion, monto, periodicidad, fecha_inicio, fecha_fin, max_socios, admin_id):
    ...

# BIEN
def crear_natillera(datos: NatilleraCreate, admin_id: int) -> Natillera:
    ...
```

---

### Condiciones

```python
# MAL — negaciones difíciles de leer
if not not usuario.activo:
    ...

if not (pago.estado != "confirmado"):
    ...

# BIEN — afirmativo y explícito
if usuario.esta_activo():
    ...

if pago.esta_confirmado():
    ...
```

```python
# MAL — magic numbers
if natillera.socios.count() >= 50:
    raise Exception("Lleno")

# BIEN — constante nombrada con semántica
MAX_SOCIOS_POR_NATILLERA = 50

if natillera.socios.count() >= MAX_SOCIOS_POR_NATILLERA:
    raise CupoMaximoAlcanzadoError(natillera.id)
```

---

### Comentarios

Los comentarios explican el **por qué**, no el **qué**. El código explica el qué.

```python
# MAL — el comentario repite el código
# Verificar si el pago está confirmado
if pago.estado == EstadoPago.CONFIRMADO:
    ...

# BIEN — el comentario explica la decisión de negocio
# RN-06: los pagos confirmados no se pueden eliminar,
# solo revertir con justificación (auditoría obligatoria)
if pago.esta_confirmado():
    raise PagoYaConfirmadoError(pago.id)
```

```python
# BIEN — referencia a la regla de negocio del dominio
def puede_recibir_distribucion(self, socio: Socio) -> bool:
    # RN-04: socio en mora no puede recibir distribuciones parciales
    return not socio.tiene_mora_activa()
```

---

### Manejo de errores

**Nunca silencies errores en operaciones financieras.**

```python
# MAL — el error desaparece silenciosamente
try:
    actualizar_saldo_fondo(natillera_id, monto)
except Exception:
    pass

# MAL — captura demasiado genérica
try:
    resultado = stripe.charge(monto)
except Exception as e:
    logger.error(e)  # ¿qué pasó exactamente?

# BIEN — captura específica, fallo explícito
try:
    resultado = stripe.charge(monto)
except stripe.CardError as e:
    raise PagoRechazadoError(razon=e.user_message)
except stripe.APIConnectionError:
    raise ServicioExternoNoDisponibleError("Stripe")
```

---

### Type hints (obligatorios en backend)

```python
# MAL
def calcular_saldo(natillera_id, incluir_mora=False):
    ...

# BIEN
def calcular_saldo(natillera_id: int, incluir_mora: bool = False) -> Decimal:
    ...
```

Los type hints permiten que el IDE detecte errores antes de ejecutar, especialmente importante en operaciones con montos de dinero (`int` vs `Decimal` vs `float`).

**Importante**: los montos de dinero siempre en `int` (centavos) o `Decimal`. Nunca `float` (imprecisión de punto flotante).

---

## JavaScript / Frontend y Mobile

### Nombres

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| Variables y funciones | `camelCase` | `confirmarPago` |
| Componentes React | `PascalCase` | `NatilleraCard` |
| Hooks | `useCamelCase` | `useNatilleras` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_SOCIOS` |
| Archivos de componentes | `PascalCase.jsx` | `PagoForm.jsx` |
| Archivos de hooks/utils | `camelCase.js` | `useConfirmarPago.js` |

---

### Componentes React

**Un componente = una responsabilidad.** Si el componente hace fetching, formateo, renderizado Y manejo de estado, hay que dividirlo.

```jsx
// MAL — componente que hace todo
function NatilleraDetalle({ natilleraId }) {
  const [natillera, setNatillera] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`/api/natilleras/${natilleraId}`)
      .then(r => r.json())
      .then(data => {
        setNatillera(data)
        setLoading(false)
      })
  }, [natilleraId])

  if (loading) return <div>Cargando...</div>

  return (
    <div>
      <h1>{natillera.nombre}</h1>
      {/* 200 líneas de JSX... */}
    </div>
  )
}
```

```jsx
// BIEN — separación clara

// hooks/useNatillera.js  ← fetching y estado del servidor
function useNatillera(natilleraId) {
  return useQuery({
    queryKey: ['natillera', natilleraId],
    queryFn: () => api.natilleras.getById(natilleraId),
  })
}

// features/natilleras/components/NatilleraDetalle.jsx  ← solo renderizado
function NatilleraDetalle({ natilleraId }) {
  const { data: natillera, isLoading } = useNatillera(natilleraId)

  if (isLoading) return <LoadingSpinner />

  return (
    <div>
      <NatilleraHeader natillera={natillera} />
      <SociosList natilleraId={natilleraId} />
      <PagosPendientes natilleraId={natilleraId} />
    </div>
  )
}
```

---

### Estado: servidor vs UI

**Regla estricta para este proyecto:**

| Tipo de estado | Herramienta | Ejemplos |
|---------------|-------------|---------|
| Datos del servidor | TanStack Query | natilleras, pagos, socios |
| Estado UI local | `useState` | modal abierto, tab activo |
| Estado UI global | Zustand | usuario autenticado, tema |

```jsx
// MAL — datos del servidor en Zustand
const useStore = create((set) => ({
  natilleras: [],
  fetchNatilleras: async () => {
    const data = await api.get('/natilleras')
    set({ natilleras: data })
  }
}))

// BIEN — datos del servidor en TanStack Query
function useNatilleras() {
  return useQuery({
    queryKey: ['natilleras'],
    queryFn: api.natilleras.list,
    staleTime: 1000 * 60, // 1 minuto
  })
}
```

---

### Nunca confíes en el cliente para montos

```jsx
// MAL — el frontend calcula cuánto debe pagar
const montoPago = natillera.montoPorPeriodo * periodosPendientes
await api.post('/pagos', { monto: montoPago })

// BIEN — el backend determina el monto, el frontend solo muestra
const { data: infoPago } = useQuery({
  queryKey: ['pago-pendiente', socioId, natilleraId],
  queryFn: () => api.pagos.calcularPendiente(socioId, natilleraId),
})
// infoPago.monto viene del servidor, no se calcula en el cliente
await api.post('/pagos', { natillera_id: natilleraId, periodo_id: periodoId })
```

---

## Principios SOLID aplicados al proyecto

| Principio | Aplicación concreta |
|-----------|-------------------|
| **S** — Single Responsibility | `PagoService` solo gestiona pagos. `NotificacionService` solo notificaciones. |
| **O** — Open/Closed | Nuevos métodos de pago se agregan con Strategy, sin modificar `PagoService`. |
| **L** — Liskov Substitution | `FakeNatilleraRepository` puede reemplazar a `NatilleraRepository` en tests. |
| **I** — Interface Segregation | Un endpoint de solo lectura no recibe las mismas dependencias que uno de escritura. |
| **D** — Dependency Inversion | Los servicios dependen de abstracciones (repos), no de SQLAlchemy directamente. |

---

## Lo que no se hace en este proyecto

| Anti-patrón | Consecuencia | Alternativa |
|-------------|-------------|-------------|
| `float` para montos de dinero | Imprecisión: `0.1 + 0.2 = 0.30000000000000004` | `Decimal` en Python, `int` (centavos) |
| `except Exception: pass` en servicios financieros | Errores silenciosos, saldo inconsistente | Captura específica + log + relanzar |
| Lógica de negocio en modelos SQLAlchemy | Difícil de testear, viola SRP | Mover a services |
| `console.log` en producción | Expone datos sensibles en logs del browser | Usar librería de logging controlada |
| Hardcodear IDs o montos en el código | Frágil ante cambios de datos | Constantes nombradas o configuración |
