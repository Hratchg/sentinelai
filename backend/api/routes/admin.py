"""
Admin API endpoints for system health and maintenance.

Provides:
- System health statistics (database size, persons, events, clips)
- Manual cleanup trigger
- Storage monitoring
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
import logging
import os
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.storage.database import get_db
from backend.storage.models import Person, PersonEvent, EventClip, GestureTemplate
from backend.workers.cleanup import DataCleanupWorker
from backend.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class HealthStats(BaseModel):
    """System health statistics."""
    database_size_mb: float
    total_persons: int
    active_persons: int
    archived_persons: int
    total_events: int
    total_clips: int
    total_gestures: int
    clips_size_gb: float


class CleanupResult(BaseModel):
    """Cleanup operation result."""
    status: str
    archived_persons: int
    deleted_events: int
    deleted_clips: int
    deleted_persons: int
    freed_disk_space_mb: float


@router.get("/health", response_model=HealthStats)
async def get_system_health(db: AsyncSession = Depends(get_db)):
    """
    Get system health statistics.

    Returns:
        HealthStats with database size, persons, events, clips, etc.
    """
    try:
        # Count persons
        total_persons_result = await db.execute(select(func.count(Person.id)))
        total_persons = total_persons_result.scalar() or 0

        active_persons_result = await db.execute(
            select(func.count(Person.id)).where(Person.archived == False)
        )
        active_persons = active_persons_result.scalar() or 0

        archived_persons_result = await db.execute(
            select(func.count(Person.id)).where(Person.archived == True)
        )
        archived_persons = archived_persons_result.scalar() or 0

        # Count events
        total_events_result = await db.execute(select(func.count(PersonEvent.id)))
        total_events = total_events_result.scalar() or 0

        # Count clips
        total_clips_result = await db.execute(select(func.count(EventClip.id)))
        total_clips = total_clips_result.scalar() or 0

        # Count gestures
        total_gestures_result = await db.execute(select(func.count(GestureTemplate.id)))
        total_gestures = total_gestures_result.scalar() or 0

        # Calculate database size
        database_size_mb = _get_database_size()

        # Calculate clips storage size
        clips_size_gb = _get_clips_storage_size()

        return HealthStats(
            database_size_mb=database_size_mb,
            total_persons=total_persons,
            active_persons=active_persons,
            archived_persons=archived_persons,
            total_events=total_events,
            total_clips=total_clips,
            total_gestures=total_gestures,
            clips_size_gb=clips_size_gb
        )

    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup", response_model=CleanupResult)
async def run_cleanup(db: AsyncSession = Depends(get_db)):
    """
    Manually trigger data cleanup.

    Performs:
    - Archive inactive persons (6 months)
    - Delete old events (1 year)
    - Delete old video clips (30 days)
    - Delete archived persons (2 years)

    Returns:
        CleanupResult with statistics about what was cleaned
    """
    try:
        logger.info("Manual cleanup triggered via API")

        worker = DataCleanupWorker()
        stats = await worker.run_cleanup(db)

        return CleanupResult(
            status="success",
            archived_persons=stats['archived_persons'],
            deleted_events=stats['deleted_events'],
            deleted_clips=stats['deleted_clips'],
            deleted_persons=stats['deleted_persons'],
            freed_disk_space_mb=stats['freed_disk_space_mb']
        )

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/storage/breakdown")
async def get_storage_breakdown(db: AsyncSession = Depends(get_db)):
    """
    Get detailed storage breakdown.

    Returns:
        Storage statistics by category
    """
    try:
        # Get database size
        database_size = _get_database_size()

        # Get clips size
        clips_size = _get_clips_storage_size()

        # Get individual clip sizes
        clips_result = await db.execute(select(EventClip))
        clips = clips_result.scalars().all()

        clip_sizes_by_type = {}
        for clip in clips:
            if os.path.exists(clip.clip_path):
                size_mb = os.path.getsize(clip.clip_path) / (1024 * 1024)
                event_type = clip.event_type
                clip_sizes_by_type[event_type] = clip_sizes_by_type.get(event_type, 0) + size_mb

        return {
            "total_size_gb": database_size / 1024 + clips_size,
            "database_size_mb": database_size,
            "clips_size_gb": clips_size,
            "clips_by_type": clip_sizes_by_type,
            "retention_policies": {
                "person_retention_days": settings.PERSON_RETENTION_DAYS,
                "event_retention_days": settings.EVENT_RETENTION_DAYS,
                "clip_retention_days": settings.CLIP_RETENTION_DAYS,
                "archived_person_retention_days": settings.ARCHIVED_PERSON_RETENTION_DAYS
            }
        }

    except Exception as e:
        logger.error(f"Failed to get storage breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _get_database_size() -> float:
    """
    Get database file size in MB.

    Returns:
        Database size in megabytes
    """
    try:
        # Extract database path from DATABASE_URL
        # Format: sqlite+aiosqlite:///./sentinelai.db
        db_url = settings.DATABASE_URL
        if db_url.startswith("sqlite"):
            db_path = db_url.split("///")[-1]
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                return size_bytes / (1024 * 1024)  # Convert to MB
        return 0.0
    except Exception as e:
        logger.error(f"Failed to get database size: {e}")
        return 0.0


def _get_clips_storage_size() -> float:
    """
    Get total size of all video clips in GB.

    Returns:
        Total clips size in gigabytes
    """
    try:
        clips_dir = settings.DATA_DIR / "clips"
        if not clips_dir.exists():
            return 0.0

        total_size = 0
        for file_path in clips_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size / (1024 * 1024 * 1024)  # Convert to GB
    except Exception as e:
        logger.error(f"Failed to get clips storage size: {e}")
        return 0.0


@router.get("/config")
async def get_system_config():
    """
    Get current system configuration.

    Returns:
        System configuration settings
    """
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "face_similarity_threshold": settings.FACE_SIMILARITY_THRESHOLD,
        "gesture_confidence_threshold": settings.GESTURE_CONFIDENCE_THRESHOLD,
        "retention": {
            "person_retention_days": settings.PERSON_RETENTION_DAYS,
            "event_retention_days": settings.EVENT_RETENTION_DAYS,
            "clip_retention_days": settings.CLIP_RETENTION_DAYS,
            "archived_person_retention_days": settings.ARCHIVED_PERSON_RETENTION_DAYS
        },
        "llm": {
            "model": settings.LLM_MODEL,
            "api_key_configured": bool(settings.ANTHROPIC_API_KEY)
        },
        "detector": {
            "device": settings.DETECTOR_DEVICE,
            "confidence": settings.DETECTOR_CONFIDENCE,
            "fp16": settings.DETECTOR_FP16
        }
    }
