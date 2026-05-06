# AGENTS.md

Monorepo con tres sub-proyectos **independientes** — sin workspace manager en la raíz.

## Estructura

| Directorio  | Stack                                                                 |
|-------------|-----------------------------------------------------------------------|
| `frontend/` | React 18 + Vite 5 + Tailwind CSS 3 (JSX puro, **sin TypeScript**)    |
| `mobile/`   | React Native 0.72 + Expo ~49 + React Navigation v6                   |
| `backend/`  | FastAPI 0.104 + Python 3.11+ + SQLAlchemy 2 + Alembic + PostgreSQL   |

## Comandos

### Frontend (`frontend/`)
```sh
npm install
npm run dev      # Vite dev server en :5173
npm run build
npm run lint     # ESLint — cero warnings permitidos (--max-warnings 0)
npm test         # Vitest
```
Vite proxea `/api` → `http://localhost:8000` (o `VITE_API_BASE_URL`).

### Mobile (`mobile/`)
```sh
npm install
npm start        # expo start
npm run android
npm run ios
```
URL del API configurada en `mobile/app.json` → `expo.extra.apiBaseUrl` (default `http://localhost:8000`).

### Backend (`backend/`)
```sh
pip install -r requirements.txt
uvicorn app.main:app --reload   # dev server en :8000
pytest                          # usa backend/pytest.ini
```

## Hechos clave

- **Sin lockfiles comprometidos** — `node_modules/` y entornos Python están en `.gitignore`.
- **Frontend es JSX puro** — no hay `tsconfig.json` ni TypeScript en ningún sub-proyecto.
- **Sin CI/CD** — el directorio `.github/` no existe aún pese a lo que menciona el README.
- **Pruebas scaffoldeadas pero vacías** — `backend/tests/__init__.py` existe pero no hay tests; Vitest está instalado en frontend pero sin archivos de prueba.
- **Markers de pytest** disponibles: `auth`, `natillera`, `transaction`, `integration`.
- **Estilo de commits**: semántico — `feat:`, `fix:`, `docs:`, `refactor:`.
