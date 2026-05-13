# Arquitectura Frontend — React + Vite

**Aplica a**: `frontend/` y con adaptaciones a `mobile/`  
**Última actualización**: Junio 2026

---

## Estructura de carpetas: feature-based

El scaffolding inicial organiza por tipo de archivo (`components/`, `hooks/`, `services/`). Eso escala mal. A partir de la segunda feature, todo es ambiguo: ¿en qué `components/` vive este componente?

**La estructura correcta para este proyecto:**

```
frontend/src/
├── features/                    ← cada feature es un módulo independiente
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.jsx
│   │   │   └── RegisterForm.jsx
│   │   ├── hooks/
│   │   │   ├── useLogin.js
│   │   │   └── useRegister.js
│   │   ├── services/
│   │   │   └── authApi.js       ← llamadas API específicas de auth
│   │   └── index.js             ← API pública del módulo
│   │
│   ├── natilleras/
│   │   ├── components/
│   │   │   ├── NatilleraCard.jsx
│   │   │   ├── NatilleraDetalle.jsx
│   │   │   ├── CrearNatilleraForm.jsx
│   │   │   └── SociosList.jsx
│   │   ├── hooks/
│   │   │   ├── useNatilleras.js
│   │   │   ├── useNatilleraDetalle.js
│   │   │   └── useCrearNatillera.js
│   │   ├── services/
│   │   │   └── natillerasApi.js
│   │   └── index.js
│   │
│   ├── pagos/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── index.js
│   │
│   └── reportes/
│       ├── components/
│       ├── hooks/
│       └── index.js
│
├── shared/                      ← solo lo genuinamente compartido
│   ├── components/
│   │   ├── Button.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── Modal.jsx
│   │   └── ErrorBoundary.jsx
│   ├── hooks/
│   │   ├── useDebounce.js
│   │   └── usePagination.js
│   └── utils/
│       ├── formatCurrency.js
│       ├── formatDate.js
│       └── validators.js
│
├── pages/                       ← solo ensamblado de features, mínima lógica
│   ├── Dashboard.jsx
│   ├── NatilleraDetalle.jsx
│   └── Perfil.jsx
│
├── store/                       ← Zustand: solo estado UI global
│   └── authStore.js
│
├── lib/
│   └── apiClient.js             ← instancia de Axios con interceptors
│
└── App.jsx
```

**Regla del `index.js`**: otros módulos solo importan desde el `index.js` de una feature, nunca directo a un archivo interno.

```js
// MAL — importación desde archivo interno de otra feature
import { useNatilleras } from '../natilleras/hooks/useNatilleras'

// BIEN — importación desde la API pública del módulo
import { useNatilleras } from '../natilleras'
```

---

## Capa de API: Axios + interceptors

```js
// lib/apiClient.js
import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

// Adjuntar token en cada request
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Manejar token expirado globalmente
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // intentar refresh token...
      const refreshed = await tryRefreshToken()
      if (!refreshed) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

```js
// features/pagos/services/pagosApi.js
import apiClient from '../../../lib/apiClient'

export const pagosApi = {
  list: (natilleraId) =>
    apiClient.get(`/natilleras/${natilleraId}/pagos`).then(r => r.data),

  confirmar: (pagoId) =>
    apiClient.put(`/pagos/${pagoId}/confirmar`).then(r => r.data),

  registrar: (datos) =>
    apiClient.post('/pagos', datos).then(r => r.data),
}
```

---

## TanStack Query: server state

Cada entidad tiene sus query keys estandarizadas:

```js
// features/natilleras/hooks/useNatilleras.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { natillerasApi } from '../services/natillerasApi'

// Query keys como constantes para evitar typos
export const natilleraKeys = {
  all: ['natilleras'],
  detail: (id) => ['natilleras', id],
  socios: (id) => ['natilleras', id, 'socios'],
}

export function useNatilleras() {
  return useQuery({
    queryKey: natilleraKeys.all,
    queryFn: natillerasApi.list,
    staleTime: 1000 * 60,     // 1 min antes de re-fetch
  })
}

export function useNatilleraDetalle(id) {
  return useQuery({
    queryKey: natilleraKeys.detail(id),
    queryFn: () => natillerasApi.getById(id),
    enabled: !!id,            // no ejecutar si id es undefined
  })
}

export function useActivarNatillera() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (natilleraId) => natillerasApi.activar(natilleraId),
    onSuccess: (data) => {
      // invalidar para re-fetch automático
      queryClient.invalidateQueries({ queryKey: natilleraKeys.all })
      queryClient.invalidateQueries({ queryKey: natilleraKeys.detail(data.id) })
    },
  })
}
```

```jsx
// uso en componente — limpio, sin useEffect ni useState para server state
function NatilleraCard({ natilleraId }) {
  const { data, isLoading, isError } = useNatilleraDetalle(natilleraId)
  const activar = useActivarNatillera()

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorMessage />

  return (
    <div>
      <h2>{data.nombre}</h2>
      <button
        onClick={() => activar.mutate(natilleraId)}
        disabled={activar.isPending}
      >
        {activar.isPending ? 'Activando...' : 'Activar'}
      </button>
    </div>
  )
}
```

---

## Zustand: solo estado UI global

```js
// store/authStore.js
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      usuario: null,
      accessToken: null,

      login: (usuario, token) => set({ usuario, accessToken: token }),
      logout: () => set({ usuario: null, accessToken: null }),
    }),
    { name: 'auth-storage' }
  )
)
```

**Lo que NO va en Zustand**: listas de natilleras, pagos, socios, cualquier cosa que venga de la API. Eso es TanStack Query.

---

## Formateo de dinero (crítico)

Todos los montos del backend vienen en centavos (enteros). El frontend los formatea al mostrar, nunca los modifica para enviar.

```js
// shared/utils/formatCurrency.js
export function formatCOP(centavos) {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
  }).format(centavos / 100)
}

// uso
formatCOP(150000)  // → "$ 1.500"
formatCOP(5000)    // → "$ 50"
```

---

## Manejo de errores en formularios

```jsx
// MAL — error genérico
catch (error) {
  setError('Algo salió mal')
}

// BIEN — usar el mensaje del backend
catch (error) {
  const mensaje = error.response?.data?.detail || 'Error al procesar la solicitud'
  setError(mensaje)
}
```

---

## Mobile: diferencias con frontend web

| Aspecto | Frontend Web | Mobile (RN + Expo) |
|---------|-------------|-------------------|
| Almacenamiento de tokens | `localStorage` (vía Zustand persist) | `expo-secure-store` (cifrado) |
| Notificaciones | Email (backend) | Push con `expo-notifications` |
| Navegación | React Router v6 | React Navigation v6 |
| Estilos | Tailwind CSS | `StyleSheet.create()` |
| Llamadas API | misma `apiClient.js` (compartible) | misma lógica, diferente import path |

Los hooks de TanStack Query y la lógica de servicios pueden compartirse entre web y mobile si se estructura como módulo común. Por ahora se duplican, pero con la misma interfaz para facilitar una futura unificación.
