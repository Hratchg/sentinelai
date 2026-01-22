"""
Job Queue Manager
Simple in-memory queue for background video processing.
For production, consider Redis-backed queue (RQ, Celery).
"""

import asyncio
import logging
from queue import Queue
from typing import Optional
import threading

logger = logging.getLogger(__name__)

# Global job queue
job_queue: Queue = Queue()

# Worker thread reference
worker_thread: Optional[threading.Thread] = None
worker_running = False


async def add_job_to_queue(job_id: str):
    """
    Add a job to the processing queue.

    Args:
        job_id: Job identifier to process
    """
    global worker_running, worker_thread

    job_queue.put(job_id)
    logger.info(f"Added job {job_id} to queue (queue size: {job_queue.qsize()})")

    # Start worker thread if not already running
    if not worker_running:
        from backend.workers.video_processor import start_worker
        worker_thread = threading.Thread(target=start_worker, daemon=True)
        worker_thread.start()
        worker_running = True
        logger.info("Started background worker thread")


def get_queue_size() -> int:
    """Get the current size of the job queue"""
    return job_queue.qsize()


def is_worker_running() -> bool:
    """Check if the worker is running"""
    return worker_running
