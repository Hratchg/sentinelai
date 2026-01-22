"""
Results Route - Retrieve processed video and event data
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import json
import logging

from backend.storage.database import get_db
from backend.storage import crud
from backend.api.models import EventsResponse, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/results/{job_id}/video",
    response_class=FileResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Video not found or not ready"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_result_video(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download the processed video with annotations.

    **Returns:**
    - Video file with bounding boxes, track IDs, and action labels
    - Same format as input (MP4, AVI, etc.)

    **Status Requirements:**
    - Job must have status 'completed'
    - Output video file must exist

    **Notes:**
    - Large files may take time to download
    - Video includes all visual annotations
    - Original video remains unchanged in uploads folder
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

        if job.status != "completed":
            logger.warning(f"Job {job_id} not completed yet (status: {job.status})")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NotReady",
                    "message": f"Video not ready. Job status: {job.status}",
                    "details": {"status": job.status, "progress": job.progress}
                }
            )

        if not job.output_video_path or not Path(job.output_video_path).exists():
            logger.error(f"Output video missing for job {job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NotFound",
                    "message": "Processed video file not found",
                    "details": {"job_id": job_id}
                }
            )

        video_path = Path(job.output_video_path)
        filename = f"processed_{job.filename}"

        logger.info(f"Serving video for job {job_id}: {video_path}")

        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=filename,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get result video: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "Failed to retrieve video",
                "details": {"error": str(e)}
            }
        )


@router.get(
    "/results/{job_id}/heatmap",
    response_class=FileResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Heatmap not found or not ready"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_result_heatmap(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download the activity heatmap visualization (Week 3).

    **Returns:**
    - PNG image showing activity zones
    - Hot colors (red/yellow) indicate high activity
    - Cool colors (blue/purple) indicate low activity

    **Status Requirements:**
    - Job must have status 'completed'
    - Heatmap generation must be enabled
    - Output heatmap file must exist

    **Notes:**
    - Heatmap shows cumulative activity across entire video
    - Useful for identifying high-traffic areas
    - Generated only if HEATMAP_ENABLED=true in config
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

        if job.status != "completed":
            logger.warning(f"Job {job_id} not completed yet (status: {job.status})")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NotReady",
                    "message": f"Heatmap not ready. Job status: {job.status}",
                    "details": {"status": job.status, "progress": job.progress}
                }
            )

        if not job.output_heatmap_path or not Path(job.output_heatmap_path).exists():
            logger.error(f"Heatmap not generated for job {job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NotFound",
                    "message": "Heatmap not generated (ensure HEATMAP_ENABLED=true)",
                    "details": {"job_id": job_id}
                }
            )

        heatmap_path = Path(job.output_heatmap_path)
        filename = f"heatmap_{job.filename.rsplit('.', 1)[0]}.png"

        logger.info(f"Serving heatmap for job {job_id}: {heatmap_path}")

        return FileResponse(
            path=str(heatmap_path),
            media_type="image/png",
            filename=filename,
            headers={
                "Content-Disposition": f'inline; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get heatmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "Failed to retrieve heatmap",
                "details": {"error": str(e)}
            }
        )


@router.get(
    "/results/{job_id}/alerts",
    response_class=JSONResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Alerts not found or not ready"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_result_alerts(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the alerts JSON with critical event notifications (Week 3).

    **Returns:**
    - summary: Alert statistics by severity and type
    - alerts: List of alert objects with details

    **Alert Structure:**
    Each alert contains:
    - alert_id: Unique alert identifier
    - alert_type: Type (fall_detected, fight_detected, prolonged_loitering, crowd_detected)
    - severity: Severity level (low, medium, high, critical)
    - message: Human-readable alert message
    - timestamp: When alert was triggered
    - frame_id: Frame number where alert occurred
    - track_ids: List of involved person track IDs
    - metadata: Additional context-specific data

    **Alert Types:**
    - fall_detected (CRITICAL): Person has fallen down
    - fight_detected (HIGH): Physical altercation detected
    - prolonged_loitering (MEDIUM): Person stationary for extended time
    - crowd_detected (MEDIUM): Large group of people detected

    **Status Requirements:**
    - Job must have status 'completed'
    - Alerts generation must be enabled
    - Output alerts file must exist
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

        if job.status != "completed":
            logger.warning(f"Job {job_id} not completed yet (status: {job.status})")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NotReady",
                    "message": f"Alerts not ready. Job status: {job.status}",
                    "details": {"status": job.status, "progress": job.progress}
                }
            )

        if not job.output_alerts_path or not Path(job.output_alerts_path).exists():
            logger.error(f"Alerts not generated for job {job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NotFound",
                    "message": "Alerts not generated (ensure ALERTS_ENABLED=true)",
                    "details": {"job_id": job_id}
                }
            )

        # Read and parse alerts JSON
        alerts_path = Path(job.output_alerts_path)
        with open(alerts_path, 'r') as f:
            alerts_data = json.load(f)

        logger.info(f"Serving alerts for job {job_id}: {alerts_data['summary']['total_alerts']} alerts")

        return JSONResponse(content=alerts_data)

    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse alerts JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ParseError",
                "message": "Failed to parse alerts file",
                "details": {"error": str(e)}
            }
        )
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "Failed to retrieve alerts",
                "details": {"error": str(e)}
            }
        )


@router.get(
    "/results/{job_id}/events",
    response_model=EventsResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Events not found or not ready"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def get_result_events(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the events JSON with action detections.

    **Returns:**
    - job_id: Job identifier
    - video_info: Metadata about the video (duration, FPS, etc.)
    - events: List of action events with timestamps
    - summary: Statistics about actions detected

    **Event Structure:**
    Each event contains:
    - frame_id: Frame number where action occurred
    - timestamp: Time in video (seconds)
    - track_id: Unique person identifier
    - action: Action type (standing, walking, running, loitering)
    - confidence: Action confidence score (0-1)
    - bbox: Bounding box coordinates [x1, y1, x2, y2]
    - velocity: Person velocity in pixels/frame

    **Status Requirements:**
    - Job must have status 'completed'
    - Events JSON file must exist
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

        if job.status != "completed":
            logger.warning(f"Job {job_id} not completed yet (status: {job.status})")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NotReady",
                    "message": f"Events not ready. Job status: {job.status}",
                    "details": {"status": job.status, "progress": job.progress}
                }
            )

        if not job.output_events_path or not Path(job.output_events_path).exists():
            logger.error(f"Output events missing for job {job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NotFound",
                    "message": "Events file not found",
                    "details": {"job_id": job_id}
                }
            )

        # Read and parse events JSON
        events_path = Path(job.output_events_path)
        with open(events_path, 'r') as f:
            events_data = json.load(f)

        logger.info(f"Serving events for job {job_id}: {len(events_data.get('events', []))} events")

        # Transform events to match API model (remove extra fields)
        transformed_events = []
        for event in events_data.get('events', []):
            transformed_events.append({
                'timestamp': event['timestamp'],
                'track_id': event['track_id'],
                'action': event['action'],
                'confidence': event['confidence'],
                'bbox': event['bbox']
            })

        # Transform summary (rename action_counts to actions)
        summary = events_data.get('summary', {})
        transformed_summary = {
            'total_events': summary.get('total_events', 0),
            'unique_tracks': summary.get('unique_tracks', 0),
            'actions': summary.get('action_counts', {})
        }

        # Video info is now optional (metadata not stored in Job model)
        # TODO: Add metadata column to Job model in future migration
        video_info = None

        return EventsResponse(
            job_id=job_id,
            video_info=video_info,
            events=transformed_events,
            summary=transformed_summary
        )

    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse events JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ParseError",
                "message": "Failed to parse events file",
                "details": {"error": str(e)}
            }
        )
    except Exception as e:
        logger.error(f"Failed to get result events: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalError",
                "message": "Failed to retrieve events",
                "details": {"error": str(e)}
            }
        )
