"""
Pydantic Models for API Request/Response Validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UploadResponse(BaseModel):
    """Response model for video upload"""
    job_id: str = Field(..., description="Unique job identifier")
    filename: str = Field(..., description="Original filename")
    status: JobStatus = Field(..., description="Initial job status")
    message: str = Field(..., description="Success message")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "filename": "surveillance_video.mp4",
            "status": "queued",
            "message": "Video uploaded successfully and queued for processing"
        }
    })


class JobResponse(BaseModel):
    """Response model for job status"""
    job_id: str = Field(..., description="Unique job identifier")
    filename: str = Field(..., description="Original filename")
    status: JobStatus = Field(..., description="Current job status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Processing progress percentage")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "filename": "surveillance_video.mp4",
            "status": "processing",
            "progress": 45.5,
            "created_at": "2025-01-16T10:30:00",
            "updated_at": "2025-01-16T10:31:30",
            "completed_at": None,
            "error_message": None
        }
    })


class JobListResponse(BaseModel):
    """Response model for listing jobs"""
    jobs: List[JobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")
    skip: int = Field(..., description="Number of jobs skipped")
    limit: int = Field(..., description="Maximum number of jobs returned")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "jobs": [],
            "total": 42,
            "skip": 0,
            "limit": 20
        }
    })


class EventData(BaseModel):
    """Model for a single action event"""
    timestamp: str = Field(..., description="Event timestamp (ISO datetime)")
    track_id: int = Field(..., description="Person track ID")
    action: str = Field(..., description="Detected action (standing, walking, running, loitering)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Action confidence score")
    bbox: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "timestamp": "2026-01-17T19:08:34.629174Z",
            "track_id": 5,
            "action": "walking",
            "confidence": 0.87,
            "bbox": [320.5, 180.2, 425.8, 450.6]
        }
    })


class EventsResponse(BaseModel):
    """Response model for events data"""
    job_id: str = Field(..., description="Job identifier")
    video_info: Optional[dict] = Field(None, description="Video metadata")
    events: List[EventData] = Field(..., description="List of action events")
    summary: dict = Field(..., description="Summary statistics")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_id": "550e8400-e29b-41d4-a716-446655440000",
            "video_info": {
                "filename": "surveillance_video.mp4",
                "duration": 30.5,
                "fps": 30,
                "total_frames": 915
            },
            "events": [],
            "summary": {
                "total_events": 24,
                "unique_tracks": 3,
                "actions": {
                    "walking": 15,
                    "standing": 6,
                    "running": 2,
                    "loitering": 1
                }
            }
        }
    })


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "error": "ValidationError",
            "message": "Invalid file format. Only MP4, AVI, and MOV are supported.",
            "details": {"supported_formats": ["mp4", "avi", "mov"]}
        }
    })
