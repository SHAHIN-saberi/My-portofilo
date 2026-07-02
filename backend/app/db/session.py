"""Async SQLAlchemy engine, session factory, and FastAPI dependency.

Engine creation is deferred to startup (via init_db) to avoid import-time
DB connection attempts. This fixes TestClient + runtime stability when
no live database is present at import.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_engine = None
_AsyncSessionLocal = None


def init_db() -> None:
    """Initialize engine and sessionmaker. Safe to call multiple times.
    Called from app lifespan so creation happens at startup, not import.
    """
    global _engine, _AsyncSessionLocal
    if _engine is not None:
        return
    settings = get_settings()
    _engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
    )
    _AsyncSessionLocal = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for the duration of a request."""
    if _AsyncSessionLocal is None:
        init_db()
    async with _AsyncSessionLocal() as session:
        yield session


# Backwards-compatible aliases (existing code may reference them)
def get_engine():
    if _engine is None:
        init_db()
    return _engine


def _get_async_session_local():
    if _AsyncSessionLocal is None:
        init_db()
    return _AsyncSessionLocal

# Make AsyncSessionLocal available for any legacy direct imports
# (will be the sessionmaker after first use)
class _AsyncSessionLocalProxy:
    def __getattr__(self, name):
        return getattr(_get_async_session_local(), name)

    def __call__(self, *args, **kwargs):
        return _get_async_session_local()(*args, **kwargs)

AsyncSessionLocal = _AsyncSessionLocalProxy()
