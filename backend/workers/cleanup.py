"""
Automated cleanup worker for data retention.

Runs scheduled cleanup tasks:
- Archive inactive persons (6 months)
- Delete old events (1 year)
- Delete old video clips (30 days)
- Delete archived persons (2 years)
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Tuple
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.storage.database import get_db
from backend.storage.models import Person, PersonEvent, EventClip
from backend.config import settings

logger = logging.getLogger(__name__)


class DataCleanupWorker:
    """
    Automated data cleanup worker.

    Configurable retention policies:
    - PERSON_RETENTION_DAYS: Archive inactive persons
    - EVENT_RETENTION_DAYS: Delete old events
    - CLIP_RETENTION_DAYS: Delete old video clips
    """

    def __init__(self):
        """Initialize cleanup worker."""
        self.person_retention_days = getattr(settings, 'PERSON_RETENTION_DAYS', 180)
        self.event_retention_days = getattr(settings, 'EVENT_RETENTION_DAYS', 365)
        self.clip_retention_days = getattr(settings, 'CLIP_RETENTION_DAYS', 30)
        self.archived_person_retention_days = getattr(settings, 'ARCHIVED_PERSON_RETENTION_DAYS', 730)  # 2 years

        logger.info(
            f"Cleanup worker initialized "
            f"(person_retention={self.person_retention_days}d, "
            f"event_retention={self.event_retention_days}d, "
            f"clip_retention={self.clip_retention_days}d)"
        )

    async def run_cleanup(self, db: AsyncSession) -> Dict:
        """
        Run all cleanup tasks.

        Args:
            db: Database session

        Returns:
            Cleanup statistics
        """
        logger.info("Starting automated cleanup...")

        stats = {
            'archived_persons': 0,
            'deleted_events': 0,
            'deleted_clips': 0,
            'deleted_persons': 0,
            'freed_disk_space_mb': 0
        }

        try:
            # 1. Archive inactive persons
            archived_count = await self._archive_inactive_persons(db)
            stats['archived_persons'] = archived_count

            # 2. Delete old events
            deleted_events = await self._delete_old_events(db)
            stats['deleted_events'] = deleted_events

            # 3. Delete old video clips
            deleted_clips, freed_space = await self._delete_old_clips(db)
            stats['deleted_clips'] = deleted_clips
            stats['freed_disk_space_mb'] = freed_space

            # 4. Delete archived persons not seen in 2 years
            deleted_persons = await self._delete_archived_persons(db)
            stats['deleted_persons'] = deleted_persons

            logger.info(f"Cleanup completed: {stats}")

            return stats

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise

    async def _archive_inactive_persons(self, db: AsyncSession) -> int:
        """
        Archive persons not seen in X days.

        Args:
            db: Database session

        Returns:
            Number of persons archived
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.person_retention_days)

        # Update persons to archived status
        result = await db.execute(
            update(Person)
            .where(Person.last_seen_at < cutoff_date)
            .where(Person.archived == False)
            .values(archived=True, archived_at=datetime.utcnow())
        )

        await db.commit()

        count = result.rowcount
        logger.info(f"Archived {count} inactive persons (not seen since {cutoff_date})")

        return count

    async def _delete_old_events(self, db: AsyncSession) -> int:
        """
        Delete events older than X days.

        Args:
            db: Database session

        Returns:
            Number of events deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.event_retention_days)

        result = await db.execute(
            delete(PersonEvent)
            .where(PersonEvent.created_at < cutoff_date)
        )

        await db.commit()

        count = result.rowcount
        logger.info(f"Deleted {count} old events (older than {cutoff_date})")

        return count

    async def _delete_old_clips(self, db: AsyncSession) -> Tuple[int, float]:
        """
        Delete video clips older than X days.

        Args:
            db: Database session

        Returns:
            (number_deleted, freed_space_mb)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.clip_retention_days)

        # Get old clips
        result = await db.execute(
            select(EventClip)
            .where(EventClip.created_at < cutoff_date)
        )

        old_clips = result.scalars().all()

        deleted_count = 0
        freed_space = 0

        for clip in old_clips:
            # Delete physical file
            if os.path.exists(clip.clip_path):
                try:
                    file_size = os.path.getsize(clip.clip_path)
                    os.remove(clip.clip_path)
                    freed_space += file_size
                    logger.debug(f"Deleted clip: {clip.clip_path}")
                except Exception as e:
                    logger.error(f"Failed to delete clip {clip.clip_path}: {e}")

            # Delete database record
            await db.delete(clip)
            deleted_count += 1

        await db.commit()

        freed_space_mb = freed_space / (1024 * 1024)

        logger.info(
            f"Deleted {deleted_count} old clips (older than {cutoff_date}), "
            f"freed {freed_space_mb:.2f} MB"
        )

        return deleted_count, freed_space_mb

    async def _delete_archived_persons(self, db: AsyncSession) -> int:
        """
        Delete archived persons not seen in 2 years.

        Args:
            db: Database session

        Returns:
            Number of persons deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.archived_person_retention_days)

        result = await db.execute(
            delete(Person)
            .where(Person.archived == True)
            .where(Person.last_seen_at < cutoff_date)
        )

        await db.commit()

        count = result.rowcount
        logger.info(f"Deleted {count} archived persons (not seen since {cutoff_date})")

        return count


async def run_scheduled_cleanup():
    """
    Run scheduled cleanup task.

    Called by scheduler (e.g., cron or background task).
    """
    async for db in get_db():
        worker = DataCleanupWorker()
        stats = await worker.run_cleanup(db)
        logger.info(f"Scheduled cleanup completed: {stats}")
        break  # Only need one session


if __name__ == "__main__":
    # Run cleanup manually
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_scheduled_cleanup())
