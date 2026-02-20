"""
DealFinder Database Connection & Session Management
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session

from src.config import get_database_url


# Synchronous engine (for migrations, testing)
sync_engine = create_engine(
    get_database_url(), pool_pre_ping=True, pool_size=5, max_overflow=10
)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


# Asynchronous engine (for API)
async_database_url = get_database_url().replace(
    "postgresql://", "postgresql+asyncpg://"
)

async_engine = create_async_engine(
    async_database_url, pool_pre_ping=True, pool_size=5, max_overflow=10
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI - provides async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session() -> Session:
    """Get synchronous session for scripts/CLI"""
    return SyncSessionLocal()


@asynccontextmanager
async def get_async_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for async sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_async_engine():
    """Cleanup async engine on shutdown"""
    await async_engine.dispose()
