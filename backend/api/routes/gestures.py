"""
Gesture teaching API endpoints.

Allows users to:
- Teach new gestures to the system
- List learned gestures
- Delete gestures
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
import numpy as np
import base64

from backend.storage.database import get_db
from backend.storage.crud import (
    create_gesture_template,
    get_all_gesture_templates,
    update_gesture_detection_count
)
from backend.core.gesture_learner import GestureLearner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/gestures", tags=["gestures"])


class TeachGestureRequest(BaseModel):
    """Request to teach a new gesture."""
    label: str
    pose_sequence_b64: str  # Base64 encoded numpy array
    num_frames: int
    created_by: Optional[str] = None


class GestureInfo(BaseModel):
    """Information about a learned gesture."""
    gesture_id: str
    label: str
    num_frames: int
    created_by: Optional[str]
    created_at: str
    detection_count: int


@router.post("/teach")
async def teach_gesture(
    request: TeachGestureRequest,
    db = Depends(get_db)
):
    """
    Teach the system a new gesture.

    The frontend records a gesture sequence (30 frames of pose data)
    and sends it to this endpoint to be saved.

    Args:
        request: Gesture teaching request
        db: Database session

    Returns:
        Created gesture info
    """
    try:
        # Decode pose sequence from base64
        pose_sequence_bytes = base64.b64decode(request.pose_sequence_b64)

        # Create gesture template in database
        gesture = await create_gesture_template(
            db,
            label=request.label,
            pose_sequence=pose_sequence_bytes,
            num_frames=request.num_frames,
            created_by=request.created_by
        )

        logger.info(f"Taught new gesture: {request.label}")

        return {
            "status": "success",
            "message": f"Gesture '{request.label}' learned successfully!",
            "gesture": {
                "gesture_id": gesture.id,
                "label": gesture.label,
                "num_frames": gesture.num_frames
            }
        }

    except Exception as e:
        logger.error(f"Gesture teaching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[GestureInfo])
async def list_gestures(db = Depends(get_db)):
    """
    List all learned gestures.

    Returns:
        List of gesture information
    """
    try:
        templates = await get_all_gesture_templates(db)

        return [
            GestureInfo(
                gesture_id=t.id,
                label=t.label,
                num_frames=t.num_frames,
                created_by=t.created_by,
                created_at=t.created_at.isoformat(),
                detection_count=t.detection_count
            )
            for t in templates
        ]

    except Exception as e:
        logger.error(f"Failed to list gestures: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{gesture_id}")
async def get_gesture(gesture_id: str, db = Depends(get_db)):
    """
    Get details about a specific gesture.

    Args:
        gesture_id: Gesture ID
        db: Database session

    Returns:
        Gesture information
    """
    # TODO: Implement get_gesture_by_id in CRUD
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.delete("/{gesture_id}")
async def delete_gesture(gesture_id: str, db = Depends(get_db)):
    """
    Delete a learned gesture.

    Args:
        gesture_id: Gesture ID
        db: Database session

    Returns:
        Success message
    """
    # TODO: Implement delete_gesture in CRUD
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/stats/summary")
async def gesture_stats(db = Depends(get_db)):
    """
    Get gesture statistics.

    Returns:
        Gesture usage statistics
    """
    try:
        templates = await get_all_gesture_templates(db)

        total_detections = sum(t.detection_count for t in templates)

        most_used = max(templates, key=lambda t: t.detection_count) if templates else None

        return {
            "total_gestures": len(templates),
            "total_detections": total_detections,
            "most_used_gesture": {
                "label": most_used.label,
                "count": most_used.detection_count
            } if most_used else None
        }

    except Exception as e:
        logger.error(f"Failed to get gesture stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
