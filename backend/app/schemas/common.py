"""Shared Pydantic schemas: consistent response envelope and enums."""
from typing import Any, Generic, Literal, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

Lang = Literal["en", "fa"]


class Envelope(BaseModel, Generic[T]):
    """Standard response wrapper: {"data": ..., "meta": {...}}."""

    data: T
    meta: Optional[dict[str, Any]] = None


class Message(BaseModel):
    message: str


class HealthStatus(BaseModel):
    status: str = "ok"
    service: str
    version: str
