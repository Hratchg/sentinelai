"""
CRUD Operations for Database Models
Create, Read, Update, Delete operations for jobs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from datetime import datetime
import logging

from backend.storage.models import Job, Person, PersonEvent, GestureTemplate, EventClip

logger = logging.getLogger(__name__)


async def create_job(
    db: AsyncSession,
    filename: str,
    input_path: str
) -> Job:
    """
    Create a new job in the database.

    Args:
        db: Database session
        filename: Original video filename
        input_path: Path to uploaded video file

    Returns:
        Created Job object
    """
    try:
        job = Job(
            filename=filename,
            status="queued",
            progress=0.0,
            input_path=input_path
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        logger.info(f"Created job {job.id} for file {filename}")
        return job

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create job: {e}")
        raise


async def get_job(db: AsyncSession, job_id: str) -> Optional[Job]:
    """
    Get a job by ID.

    Args:
        db: Database session
        job_id: Job identifier

    Returns:
        Job object or None if not found
    """
    try:
        result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        return job

    except Exception as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise


async def list_jobs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None
) -> tuple[List[Job], int]:
    """
    List jobs with pagination and optional status filter.

    Args:
        db: Database session
        skip: Number of jobs to skip (offset)
        limit: Maximum number of jobs to return
        status_filter: Optional status filter (queued, processing, completed, failed)

    Returns:
        Tuple of (list of jobs, total count)
    """
    try:
        # Build query
        query = select(Job)

        if status_filter:
            query = query.where(Job.status == status_filter)

        # Get total count
        count_query = select(func.count()).select_from(Job)
        if status_filter:
            count_query = count_query.where(Job.status == status_filter)

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results (ordered by creation time, newest first)
        query = query.order_by(desc(Job.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        jobs = result.scalars().all()

        return jobs, total

    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise


async def update_job_status(
    db: AsyncSession,
    job_id: str,
    status: str,
    progress: Optional[float] = None,
    error_message: Optional[str] = None
) -> Optional[Job]:
    """
    Update job status and progress.

    Args:
        db: Database session
        job_id: Job identifier
        status: New status (queued, processing, completed, failed)
        progress: Optional progress percentage (0-100)
        error_message: Optional error message (for failed status)

    Returns:
        Updated Job object or None if not found
    """
    try:
        job = await get_job(db, job_id)
        if not job:
            logger.warning(f"Job {job_id} not found")
            return None

        job.status = status
        job.updated_at = datetime.utcnow()

        if progress is not None:
            job.progress = max(0.0, min(100.0, progress))  # Clamp between 0-100

        if error_message:
            job.error_message = error_message

        if status == "completed":
            job.completed_at = datetime.utcnow()
            job.progress = 100.0

        await db.commit()
        await db.refresh(job)

        logger.info(f"Updated job {job_id}: status={status}, progress={job.progress}%")
        return job

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update job {job_id}: {e}")
        raise


async def update_job_results(
    db: AsyncSession,
    job_id: str,
    output_video_path: str,
    output_events_path: str,
    output_heatmap_path: Optional[str] = None,
    output_alerts_path: Optional[str] = None
) -> Optional[Job]:
    """
    Update job with output file paths.

    Args:
        db: Database session
        job_id: Job identifier
        output_video_path: Path to processed video
        output_events_path: Path to events JSON
        output_heatmap_path: Path to heatmap PNG (Week 3, optional)
        output_alerts_path: Path to alerts JSON (Week 3, optional)

    Returns:
        Updated Job object or None if not found
    """
    try:
        job = await get_job(db, job_id)
        if not job:
            logger.warning(f"Job {job_id} not found")
            return None

        job.output_video_path = output_video_path
        job.output_events_path = output_events_path

        # Week 3 outputs (optional)
        if output_heatmap_path:
            job.output_heatmap_path = output_heatmap_path
        if output_alerts_path:
            job.output_alerts_path = output_alerts_path

        job.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(job)

        logger.info(f"Updated job {job_id} with result paths")
        return job

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update job results {job_id}: {e}")
        raise


async def delete_job(db: AsyncSession, job_id: str) -> bool:
    """
    Delete a job from the database.

    Args:
        db: Database session
        job_id: Job identifier

    Returns:
        True if deleted, False if not found
    """
    try:
        job = await get_job(db, job_id)
        if not job:
            logger.warning(f"Job {job_id} not found")
            return False

        await db.delete(job)
        await db.commit()

        logger.info(f"Deleted job {job_id}")
        return True

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete job {job_id}: {e}")
        raise


# ===========================
# Person CRUD Operations
# ===========================

async def create_person(
    db: AsyncSession,
    person_id: str,
    display_name: str,
    face_embedding: bytes,
    name: Optional[str] = None,
    name_source: str = 'auto-generated'
) -> Person:
    """
    Create a new person in the database.

    Args:
        db: Database session
        person_id: Unique person identifier
        display_name: Display name
        face_embedding: Serialized face embedding
        name: Actual name (if known)
        name_source: How name was obtained

    Returns:
        Created Person object
    """
    try:
        person = Person(
            id=person_id,
            name=name,
            display_name=display_name,
            face_embedding=face_embedding,
            name_source=name_source,
            total_appearances=1
        )
        db.add(person)
        await db.commit()
        await db.refresh(person)

        logger.info(f"Created person {person_id} ({display_name})")
        return person

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create person: {e}")
        raise


async def get_person(db: AsyncSession, person_id: str) -> Optional[Person]:
    """Get person by ID"""
    try:
        result = await db.execute(select(Person).where(Person.id == person_id))
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Failed to get person {person_id}: {e}")
        return None


async def get_all_persons(
    db: AsyncSession,
    include_archived: bool = False
) -> List[Person]:
    """
    Get all persons from database.

    Args:
        db: Database session
        include_archived: Whether to include archived persons

    Returns:
        List of Person objects
    """
    try:
        query = select(Person)
        if not include_archived:
            query = query.where(Person.archived == False)

        query = query.order_by(desc(Person.last_seen_at))

        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Failed to get all persons: {e}")
        return []


async def update_person_last_seen(
    db: AsyncSession,
    person_id: str
) -> Optional[Person]:
    """Update person's last_seen_at timestamp and increment appearances"""
    try:
        person = await get_person(db, person_id)
        if not person:
            return None

        person.last_seen_at = datetime.utcnow()
        person.total_appearances += 1

        await db.commit()
        await db.refresh(person)

        return person

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update person last_seen: {e}")
        raise


async def update_person_name(
    db: AsyncSession,
    person_id: str,
    name: str,
    name_source: str = 'audio'
) -> Optional[Person]:
    """Update person's name from audio or manual input"""
    try:
        person = await get_person(db, person_id)
        if not person:
            return None

        person.name = name
        person.display_name = name
        person.name_source = name_source

        await db.commit()
        await db.refresh(person)

        logger.info(f"Updated person {person_id} name to '{name}' (source: {name_source})")
        return person

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update person name: {e}")
        raise


# ===========================
# PersonEvent CRUD Operations
# ===========================

async def create_person_event(
    db: AsyncSession,
    person_id: str,
    camera_id: int,
    event_type: str,
    action: Optional[str] = None,
    confidence: Optional[float] = None,
    frame_number: Optional[int] = None,
    bbox: Optional[str] = None,
    event_metadata: Optional[str] = None
) -> PersonEvent:
    """Create a new person event"""
    try:
        event = PersonEvent(
            person_id=person_id,
            camera_id=camera_id,
            event_type=event_type,
            action=action,
            confidence=confidence,
            frame_number=frame_number,
            bbox=bbox,
            event_metadata=event_metadata
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)

        return event

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create person event: {e}")
        raise


async def get_person_events(
    db: AsyncSession,
    person_id: Optional[str] = None,
    limit: int = 100
) -> List[PersonEvent]:
    """Get person events, optionally filtered by person_id"""
    try:
        query = select(PersonEvent)

        if person_id:
            query = query.where(PersonEvent.person_id == person_id)

        query = query.order_by(desc(PersonEvent.created_at)).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    except Exception as e:
        logger.error(f"Failed to get person events: {e}")
        return []


# ===========================
# GestureTemplate CRUD Operations
# ===========================

async def create_gesture_template(
    db: AsyncSession,
    label: str,
    pose_sequence: bytes,
    num_frames: int,
    created_by: Optional[str] = None
) -> GestureTemplate:
    """Create a new gesture template"""
    try:
        gesture = GestureTemplate(
            label=label,
            pose_sequence=pose_sequence,
            num_frames=num_frames,
            created_by=created_by
        )
        db.add(gesture)
        await db.commit()
        await db.refresh(gesture)

        logger.info(f"Created gesture template '{label}' ({num_frames} frames)")
        return gesture

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create gesture template: {e}")
        raise


async def get_all_gesture_templates(db: AsyncSession) -> List[GestureTemplate]:
    """Get all gesture templates"""
    try:
        result = await db.execute(select(GestureTemplate))
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Failed to get gesture templates: {e}")
        return []


async def update_gesture_detection_count(
    db: AsyncSession,
    gesture_id: str
) -> Optional[GestureTemplate]:
    """Increment gesture detection count and update last_detected_at"""
    try:
        result = await db.execute(select(GestureTemplate).where(GestureTemplate.id == gesture_id))
        gesture = result.scalar_one_or_none()

        if not gesture:
            return None

        gesture.detection_count += 1
        gesture.last_detected_at = datetime.utcnow()

        await db.commit()
        await db.refresh(gesture)

        return gesture

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update gesture detection count: {e}")
        raise


# ===========================
# EventClip CRUD Operations
# ===========================

async def create_event_clip(
    db: AsyncSession,
    person_id: str,
    camera_id: int,
    event_type: str,
    clip_path: str,
    duration_seconds: float,
    file_size_bytes: Optional[int] = None,
    thumbnail_path: Optional[str] = None
) -> EventClip:
    """Create a new event clip record"""
    try:
        clip = EventClip(
            person_id=person_id,
            camera_id=camera_id,
            event_type=event_type,
            clip_path=clip_path,
            duration_seconds=duration_seconds,
            file_size_bytes=file_size_bytes,
            thumbnail_path=thumbnail_path
        )
        db.add(clip)
        await db.commit()
        await db.refresh(clip)

        logger.info(f"Created event clip for person {person_id} ({event_type}, {duration_seconds}s)")
        return clip

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create event clip: {e}")
        raise


async def get_person_clips(
    db: AsyncSession,
    person_id: str,
    limit: int = 50
) -> List[EventClip]:
    """Get event clips for a specific person"""
    try:
        query = select(EventClip).where(EventClip.person_id == person_id)
        query = query.order_by(desc(EventClip.created_at)).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    except Exception as e:
        logger.error(f"Failed to get person clips: {e}")
        return []


async def get_recent_clips(
    db: AsyncSession,
    limit: int = 20
) -> List[EventClip]:
    """Get most recent event clips across all persons"""
    try:
        query = select(EventClip).order_by(desc(EventClip.created_at)).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    except Exception as e:
        logger.error(f"Failed to get recent clips: {e}")
        return []
