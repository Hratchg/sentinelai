"""
Video Processor Worker
Background worker that processes videos from the queue.
"""

import asyncio
import logging
from pathlib import Path
import traceback
from sqlalchemy.ext.asyncio import AsyncSession

from backend.workers.queue import job_queue
from backend.storage.database import AsyncSessionLocal
from backend.storage import crud
from backend.core.pipeline import VideoPipeline
from backend.config import settings

logger = logging.getLogger(__name__)


async def process_video_job(job_id: str):
    """
    Process a single video job.

    Args:
        job_id: Job identifier to process

    This function:
    1. Retrieves job from database
    2. Updates status to 'processing'
    3. Runs the video pipeline
    4. Updates progress periodically
    5. Saves results and updates status to 'completed'
    6. Handles errors and updates status to 'failed'
    """
    db: AsyncSession = None

    try:
        # Get database session
        db = AsyncSessionLocal()

        # Get job from database
        job = await crud.get_job(db, job_id)
        if not job:
            logger.error(f"Job {job_id} not found in database")
            return

        logger.info(f"Processing job {job_id}: {job.filename}")

        # Update status to processing
        await crud.update_job_status(db, job_id, status="processing", progress=0.0)

        # Setup output paths
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)

        events_dir = Path("data/events")
        events_dir.mkdir(parents=True, exist_ok=True)

        heatmaps_dir = Path("data/heatmaps")
        heatmaps_dir.mkdir(parents=True, exist_ok=True)

        alerts_dir = Path("data/alerts")
        alerts_dir.mkdir(parents=True, exist_ok=True)

        output_video_path = output_dir / f"{job_id}_processed.mp4"
        output_events_path = events_dir / f"{job_id}_events.json"
        output_heatmap_path = heatmaps_dir / f"{job_id}_heatmap.png"
        output_alerts_path = alerts_dir / f"{job_id}_alerts.json"

        # Initialize pipeline
        pipeline = VideoPipeline()

        # Progress callback to update database
        async def progress_callback(current_frame: int, total_frames: int):
            """Update job progress in database"""
            if total_frames > 0:
                progress = (current_frame / total_frames) * 100
                # Update every 10% to avoid too many DB writes
                if int(progress) % 10 == 0:
                    await crud.update_job_status(
                        db, job_id, status="processing", progress=progress
                    )
                    logger.debug(f"Job {job_id} progress: {progress:.1f}%")

        # Process the video
        logger.info(f"Starting pipeline for job {job_id}")
        results = await asyncio.to_thread(
            pipeline.process_video,
            input_path=Path(job.input_path),
            output_path=output_video_path,
            events_path=output_events_path,
            heatmap_path=output_heatmap_path if settings.HEATMAP_ENABLED else None,
            alerts_path=output_alerts_path if settings.ALERTS_ENABLED else None,
            job_id=job_id
        )

        logger.info(f"Pipeline completed for job {job_id}: {results}")

        # Update job with results
        await crud.update_job_results(
            db, job_id,
            output_video_path=str(output_video_path),
            output_events_path=str(output_events_path),
            output_heatmap_path=str(output_heatmap_path) if settings.HEATMAP_ENABLED else None,
            output_alerts_path=str(output_alerts_path) if settings.ALERTS_ENABLED else None
        )

        # Mark as completed
        await crud.update_job_status(db, job_id, status="completed", progress=100.0)

        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        error_msg = f"Failed to process job {job_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        logger.error(traceback.format_exc())

        # Update job status to failed
        if db:
            try:
                await crud.update_job_status(
                    db, job_id,
                    status="failed",
                    error_message=str(e)
                )
            except Exception as db_error:
                logger.error(f"Failed to update job status: {db_error}")

    finally:
        if db:
            await db.close()


def start_worker():
    """
    Start the background worker that processes jobs from the queue.
    Runs in a separate thread.
    """
    logger.info("Background worker started")

    # Create event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        while True:
            # Get job from queue (blocking)
            job_id = job_queue.get()

            logger.info(f"Worker picked up job {job_id} (queue size: {job_queue.qsize()})")

            try:
                # Process the job
                loop.run_until_complete(process_video_job(job_id))

            except Exception as e:
                logger.error(f"Worker error processing job {job_id}: {e}", exc_info=True)

            finally:
                # Mark task as done
                job_queue.task_done()

    except KeyboardInterrupt:
        logger.info("Worker interrupted, shutting down")
    except Exception as e:
        logger.error(f"Worker crashed: {e}", exc_info=True)
    finally:
        loop.close()
