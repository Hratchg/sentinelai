"""
Jobs Route - Manage job status and listings
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from backend.storage.database import get_db
from backend.storage import crud
from backend.api.models import JobResponse, JobListResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status of a specific job.

    **Returns:**
    - job_id: Job identifier
    - filename: Original video filename
    - status: Current status (queued, processing, completed, failed)
    - progress: Processing progress (0-100%)
    - created_at: When the job was created
    - updated_at: When the job was last updated
    - completed_at: When the job completed (if finished)
    - error_message: Error details (if failed)

    **Status Values:**
    - `queued`: Job is waiting to be processed
    - `processing`: Job is currently being processed
    - `completed`: Job finished successfully
    - `failed`: Job failed due to an error
    """
    try:
        job = await crud.get_job(db, job_id)

        if not job:
            logger.warning(f"Job not found: {job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NotFound",
                    "message": f"Job {job_id} not found",
                    "details": {"job_id": job_id}
                }
            )

        return JobResponse(**job.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "Failed to retrieve job status",
                "details": {"error": str(e)}
            }
        )


@router.get(
    "/jobs",
    response_model=JobListResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip (pagination offset)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of jobs to return"),
    status: Optional[str] = Query(None, description="Filter by status (queued, processing, completed, failed)"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all jobs with pagination and optional status filter.

    **Query Parameters:**
    - skip: Number of jobs to skip (default: 0)
    - limit: Maximum jobs to return (default: 20, max: 100)
    - status: Filter by status (optional)

    **Returns:**
    - jobs: List of job objects
    - total: Total number of jobs (matching filter)
    - skip: Number of jobs skipped
    - limit: Maximum jobs returned

    **Example:**
    - `/api/v1/jobs?skip=0&limit=20` - Get first 20 jobs
    - `/api/v1/jobs?status=completed` - Get all completed jobs
    - `/api/v1/jobs?status=processing&limit=10` - Get first 10 processing jobs
    """
    try:
        # Validate status if provided
        if status and status not in ["queued", "processing", "completed", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "ValidationError",
                    "message": f"Invalid status: {status}",
                    "details": {"valid_statuses": ["queued", "processing", "completed", "failed"]}
                }
            )

        jobs, total = await crud.list_jobs(db, skip=skip, limit=limit, status_filter=status)

        jobs_data = [JobResponse(**job.to_dict()) for job in jobs]

        return JobListResponse(
            jobs=jobs_data,
            total=total,
            skip=skip,
            limit=limit
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "Failed to retrieve jobs",
                "details": {"error": str(e)}
            }
        )


@router.delete(
    "/jobs/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a job and its associated files.

    **Warning:** This action is irreversible. All job data and results will be deleted.

    **Returns:**
    - 204 No Content on success
    - 404 Not Found if job doesn't exist
    """
    try:
        deleted = await crud.delete_job(db, job_id)

        if not deleted:
            logger.warning(f"Job not found for deletion: {job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NotFound",
                    "message": f"Job {job_id} not found",
                    "details": {"job_id": job_id}
                }
            )

        # TODO: Delete associated files (input video, output video, events JSON)
        # This will be implemented when we add file cleanup logic

        logger.info(f"Deleted job: {job_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "Failed to delete job",
                "details": {"error": str(e)}
            }
        )
