# Natillera Frontend

React 18 + Vite + Tailwind CSS web application for Natillera platform.

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env with API_BASE_URL

# 3. Start dev server
npm run dev
```

App runs on `http://localhost:5173`

## Structure

```
src/
├── main.jsx             # Entry point
├── App.jsx              # Root component
├── components/          # Reusable components
│   ├── Auth/           # Login, Register
│   ├── Natilleras/     # Natillera management
│   ├── Transactions/   # Transaction components
│   └── Layout/         # Header, Footer, Sidebar
├── pages/              # Page components (routed)
│   ├── Dashboard.jsx
│   ├── NatilleraDetail.jsx
│   ├── Login.jsx
│   └── Register.jsx
├── services/           # API calls
│   └── api.js         # Axios configuration
├── hooks/              # Custom React hooks
│   ├── useAuth.js
│   └── useNatilleras.js
├── context/            # Context API
│   └── AuthContext.jsx
└── utils/              # Utilities
```

## Development

```bash
# Dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint

# Tests
npm test
```

## Configuration

Environment variables in `.env`:
- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000)
- `VITE_APP_NAME` - Application name

## Dependencies

- React 18 - UI library
- Vite - Build tool
- TailwindCSS - Styling
- React Router - Navigation
- TanStack Query - Data fetching
- Axios - HTTP client

## Contributing

1. Create feature branch: `git checkout -b feat/feature-name`
2. Make changes
3. Run lint and tests: `npm run lint && npm test`
4. Commit: `git commit -m "feat: description"`
5. Push: `git push origin feat/feature-name`
6. Create Pull Request

## Deployment

Frontend deploys to Vercel automatically on push to main branch.

See DEPLOYMENT.md for details.
