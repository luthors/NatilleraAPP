"""
Common Pydantic schemas shared across the application.
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated API response envelope."""
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class MessageResponse(BaseModel):
    """Generic success message response."""
    message: str
    detail: Optional[str] = None
