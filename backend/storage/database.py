"""
Database Connection and Session Management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_DIR = Path(__file__).parent.parent.parent / "data" / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_DIR}/sentinelai.db"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def init_db():
    """
    Initialize database - create tables if they don't exist.
    """
    try:
        from backend.storage.models import Job  # Import here to avoid circular imports

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info(f"Database initialized at {DATABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """
    Close database connections.
    """
    await engine.dispose()
    logger.info("Database connections closed")


async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.

    Usage in FastAPI routes:
        @app.get("/")
        async def route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
