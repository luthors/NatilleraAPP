"""
Abstract base repository.

All concrete repositories extend BaseRepository[T].
This allows services to depend on abstractions, making them
fully testable with in-memory fakes (FakeRepository).

Reference: docs/design/02-patrones-diseno.md — Repository Pattern
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Abstract CRUD repository.

    Subclasses receive a SQLAlchemy Session injected via __init__.
    They must NOT call db.commit() or db.rollback() — that is handled
    by the Unit of Work (get_db dependency in database.py).
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        ...

    def save(self, entity: T) -> T:
        """Add a new entity and flush to get its auto-generated ID."""
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: T) -> None:
        """Remove an entity from the session (commit handled by UoW)."""
        self.db.delete(entity)
        self.db.flush()
