"""
Database configuration and initialization
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Create async engine
if settings.DATABASE_URL.startswith("sqlite"):
    # Convert sqlite:/// to sqlite+aiosqlite:/// for async support
    async_database_url = settings.DATABASE_URL.replace(
        "sqlite:///", "sqlite+aiosqlite:///")
    engine = create_async_engine(
        async_database_url,
        echo=settings.LOG_LEVEL == "DEBUG",
        pool_pre_ping=True,
    )
else:
    # PostgreSQL with asyncpg driver
    async_database_url = settings.DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        async_database_url,
        echo=settings.LOG_LEVEL == "DEBUG",
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=300,
    )

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for database models
Base = declarative_base()


async def init_db() -> None:
    """Initialize database tables for MVP - Skip for now"""
    try:
        logger.info("Database initialization skipped for MVP (in-memory storage)")
        # For MVP, we'll use in-memory storage in the agent service
        # This avoids all foreign key and model complexity
        return
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        logger.warning("Database unavailable, continuing without database...")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
