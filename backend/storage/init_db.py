"""
Initialize Database with All Tables.

Creates the database and all tables from the current schema.
Safe to run multiple times - will only create missing tables/columns.
"""

import asyncio
import logging
from backend.storage.database import init_db, DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Initialize the database."""
    logger.info("Initializing SentinelAI database...")
    logger.info(f"Database URL: {DATABASE_URL}")

    try:
        await init_db()
        logger.info("\n✓ Database initialized successfully!")
        logger.info("All tables created with Week 3 schema.")
    except Exception as e:
        logger.error(f"\n✗ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
