"""
Upload Route - Handle video file uploads
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import aiofiles
import logging

from backend.storage.database import get_db
from backend.storage import crud
from backend.api.models import UploadResponse, ErrorResponse
from backend.workers.queue import add_job_to_queue

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}


def validate_video_file(filename: str) -> bool:
    """
    Validate video file extension.

    Args:
        filename: Name of the file

    Returns:
        True if valid, False otherwise
    """
    extension = Path(filename).suffix.lower()
    return extension in ALLOWED_EXTENSIONS


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file format or size"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def upload_video(
    file: UploadFile = File(..., description="Video file to process"),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a video file for processing.

    **Accepts:**
    - Video files in MP4, AVI, MOV, or MKV format
    - Maximum file size: 100 MB

    **Returns:**
    - job_id: Unique identifier to track processing status
    - filename: Original filename
    - status: Initial status (queued)
    - message: Success message

    **Process:**
    1. Validates file format and size
    2. Saves file to uploads directory
    3. Creates job record in database
    4. Adds job to processing queue
    5. Returns job_id for tracking
    """
    try:
        # Validate file extension
        if not validate_video_file(file.filename):
            logger.warning(f"Invalid file format: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "ValidationError",
                    "message": f"Invalid file format. Only {', '.join(ALLOWED_EXTENSIONS)} are supported.",
                    "details": {"supported_formats": list(ALLOWED_EXTENSIONS)}
                }
            )

        # Read file and check size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            logger.warning(f"File too large: {len(content)} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "ValidationError",
                    "message": f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)} MB",
                    "details": {"max_size_mb": MAX_FILE_SIZE // (1024 * 1024)}
                }
            )

        # Create job in database first to get job_id
        job = await crud.create_job(
            db=db,
            filename=file.filename,
            input_path=""  # Will be updated after file save
        )

        # Save file with job_id in filename to avoid collisions
        file_extension = Path(file.filename).suffix
        safe_filename = f"{job.id}{file_extension}"
        file_path = UPLOAD_DIR / safe_filename

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        # Update job with actual file path
        job.input_path = str(file_path)
        await db.commit()
        await db.refresh(job)

        logger.info(f"Saved uploaded file: {file_path} (job_id: {job.id})")

        # Add job to processing queue
        await add_job_to_queue(job.id)

        return UploadResponse(
            job_id=job.id,
            filename=file.filename,
            status="queued",
            message="Video uploaded successfully and queued for processing"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "Failed to upload video. Please try again.",
                "details": {"error": str(e)}
            }
        )
