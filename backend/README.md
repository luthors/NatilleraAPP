"""
Backend setup documentation
"""
# Natillera Backend

## Quick Start

```bash
# 1. Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# 4. Run migrations
alembic upgrade head

# 5. Start server
python -m uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`  
API Docs: `http://localhost:8000/docs`

## Structure

```
app/
├── main.py              # FastAPI app initialization
├── core/
│   ├── config.py        # Settings, env variables
│   └── security.py      # JWT, password hashing
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic validation schemas
├── api/
│   └── v1/
│       ├── endpoints/   # API routes
│       └── router.py    # v1 router
├── services/            # Business logic
├── database.py          # Database configuration
└── dependencies.py      # Dependency injection
```

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov

# Format code
black app/

# Lint
pylint app/
```

## Database

Uses PostgreSQL with SQLAlchemy ORM and Alembic migrations.

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## API Endpoints (MVP)

```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh

GET    /natilleras
POST   /natilleras
GET    /natilleras/{id}
PUT    /natilleras/{id}
DELETE /natilleras/{id}

GET    /transactions
POST   /transactions
```

See API_DOCS.md for full endpoint reference.
