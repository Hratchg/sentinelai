"""
Database Migration for Week 3 Features.

Adds output_heatmap_path and output_alerts_path columns to jobs table.
"""

import asyncio
import logging
from sqlalchemy import text
from backend.storage.database import engine, DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_week3():
    """Add Week 3 columns to jobs table."""

    migrations = [
        """
        ALTER TABLE jobs
        ADD COLUMN output_heatmap_path VARCHAR(512);
        """,
        """
        ALTER TABLE jobs
        ADD COLUMN output_alerts_path VARCHAR(512);
        """
    ]

    async with engine.begin() as conn:
        for i, migration in enumerate(migrations, 1):
            try:
                await conn.execute(text(migration))
                logger.info(f"✓ Migration {i}/2 completed")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    logger.info(f"⊘ Migration {i}/2 skipped - column already exists")
                else:
                    logger.error(f"✗ Migration {i}/2 failed: {e}")
                    raise

    logger.info(f"\n✓ Week 3 migration completed successfully!")
    logger.info(f"Database: {DATABASE_URL}")


async def rollback_week3():
    """Remove Week 3 columns (SQLite doesn't support DROP COLUMN easily)."""
    logger.warning("SQLite doesn't support DROP COLUMN natively.")
    logger.warning("To rollback, delete the database and reinitialize:")
    logger.warning("  rm data/database/sentinelai.db")
    logger.warning("  python -m backend.main  # Will auto-create new DB")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(rollback_week3())
    else:
        asyncio.run(migrate_week3())
