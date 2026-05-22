"""
Database engine, session factory and Unit of Work dependency.

The `get_db()` generator implements the Unit of Work pattern:
- One SQLAlchemy Session per HTTP request.
- Auto-commit on success, auto-rollback on any exception.
- Services and repositories use flush() to get IDs without committing.
- The commit/rollback is always controlled here, never inside a service.

Reference: docs/design/02-patrones-diseno.md — Unit of Work
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from app.core.config import settings

# ─── Engine ───────────────────────────────────────────────────────────────────

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,           # reconnect if connection was dropped
    pool_size=5,
    max_overflow=10,
    connect_args=(
        {"check_same_thread": False}
        if "sqlite" in settings.DATABASE_URL
        else {}
    ),
)

# ─── Session factory ──────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ─── Declarative base ─────────────────────────────────────────────────────────

Base = declarative_base()

# ─── Unit of Work dependency ──────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides one database session per request.

    Lifecycle:
        1. Open a new session.
        2. Yield it to the endpoint / service.
        3. Commit if no exception was raised.
        4. Rollback on any exception (including domain exceptions from services).
        5. Always close the session.

    Usage in endpoints:
        def my_endpoint(db: Session = Depends(get_db)):
            ...

    Never call db.commit() or db.rollback() inside services or repositories.
    Use db.flush() to get auto-generated IDs within the same transaction.
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
