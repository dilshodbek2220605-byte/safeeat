"""Async engine va session factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

_settings = get_settings()


def _build_engine():
    """Dialektga mos engine yaratadi (SQLite test uchun alohida sozlamalar)."""
    url = _settings.database_url
    kwargs: dict = {"echo": _settings.db_echo}

    if url.startswith("sqlite"):
        # Test / lokal xotira uchun — pool parametrlari qo'llab-quvvatlanmaydi
        kwargs["connect_args"] = {"check_same_thread": False}
        kwargs["poolclass"] = StaticPool
    else:
        kwargs.update(pool_pre_ping=True, pool_size=10, max_overflow=20)

    return create_async_engine(url, **kwargs)


engine = _build_engine()

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — har so'rov uchun yangi session."""
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
