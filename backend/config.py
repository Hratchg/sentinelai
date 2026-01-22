"""
Configuration management for SentinelAI backend.
Uses pydantic-settings for environment-based config.
"""

import os
from pathlib import Path
from typing import Literal

import torch
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Project info
    PROJECT_NAME: str = "SentinelAI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    EVENTS_DIR: Path = DATA_DIR / "events"
    MODEL_DIR: Path = BASE_DIR / "backend" / "models"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sentinelai.db"

    # Model settings
    DETECTOR_MODEL: str = "yolov8n.pt"
    DETECTOR_CONFIDENCE: float = 0.25
    DETECTOR_IOU: float = 0.45
    DETECTOR_DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    DETECTOR_FP16: bool = torch.cuda.is_available()

    # Tracker settings
    TRACKER_TYPE: Literal["bytetrack", "botsort"] = "bytetrack"
    TRACK_THRESH: float = 0.5
    TRACK_BUFFER: int = 30
    MATCH_THRESH: float = 0.8

    # Processing settings
    FRAME_SKIP: int = 2  # Process every Nth frame
    MAX_DETECTIONS: int = 100
    OUTPUT_FPS: int = 15
    OUTPUT_CODEC: str = "mp4v"

    # Action recognition (rule-based)
    VELOCITY_WALKING_THRESHOLD: float = 3.0  # px/frame
    VELOCITY_RUNNING_THRESHOLD: float = 12.0  # px/frame
    LOITERING_THRESHOLD: int = 90  # frames (~3 seconds at 30fps)
    STATIONARY_VELOCITY_THRESHOLD: float = 2.0  # px/frame

    # Fall detection
    FALL_DETECTION_ENABLED: bool = True
    FALL_ASPECT_RATIO_THRESHOLD: float = 0.8  # Width/height ratio for horizontal person
    FALL_VERTICAL_VELOCITY_THRESHOLD: float = 20.0  # px/frame downward
    FALL_GROUND_PROXIMITY_THRESHOLD: float = 0.8  # Distance from bottom (0-1)
    FALL_STATIONARY_DURATION: int = 150  # frames (~5s @ 30fps)

    # Fight detection
    FIGHT_DETECTION_ENABLED: bool = True
    FIGHT_PROXIMITY_IOU_THRESHOLD: float = 0.3  # Bbox overlap
    FIGHT_RAPID_MOVEMENT_THRESHOLD: float = 15.0  # px/frame
    FIGHT_MIN_DURATION_FRAMES: int = 60  # 2s @ 30fps
    FIGHT_MIN_PARTICIPANTS: int = 2

    # Heatmap generation
    HEATMAP_ENABLED: bool = True
    HEATMAP_CELL_SIZE: int = 32  # Grid cell size in pixels
    HEATMAP_COLORMAP: str = "JET"  # OpenCV colormap
    HEATMAP_ALPHA: float = 0.4  # Overlay transparency

    # Alerting
    ALERTS_ENABLED: bool = True
    ALERT_WEBHOOK_URL: str = ""  # Optional webhook URL
    ALERT_DEDUPLICATION_WINDOW: int = 30  # seconds

    # Real-time surveillance (Week 4)
    FACE_SIMILARITY_THRESHOLD: float = 0.6  # Face matching threshold
    GESTURE_CONFIDENCE_THRESHOLD: float = 0.7  # Gesture detection threshold
    CLIP_RETENTION_DAYS: int = 30  # Video clip retention period
    PERSON_RETENTION_DAYS: int = 180  # Archive inactive persons after 6 months
    EVENT_RETENTION_DAYS: int = 365  # Delete events after 1 year
    ARCHIVED_PERSON_RETENTION_DAYS: int = 730  # Delete archived persons after 2 years

    # LLM Integration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_MODEL: str = "claude-3-5-sonnet-20241022"

    # Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production-use-long-random-string")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days

    # Performance
    MAX_WORKERS: int = 2  # Concurrent video processing jobs
    JOB_TIMEOUT: int = 3600  # 1 hour max per job

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Replit mode detection
    IS_REPLIT: bool = os.environ.get("REPLIT") is not None

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create directories if they don't exist
        clips_dir = self.DATA_DIR / "clips"
        database_dir = self.DATA_DIR / "database"

        for directory in [
            self.DATA_DIR,
            self.UPLOAD_DIR,
            self.PROCESSED_DIR,
            self.EVENTS_DIR,
            self.MODEL_DIR,
            clips_dir,
            database_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Replit optimizations
        if self.IS_REPLIT:
            self.DETECTOR_DEVICE = "cpu"
            self.DETECTOR_FP16 = False
            self.FRAME_SKIP = 3  # More aggressive frame skipping
            print("⚠️  Replit mode detected: CPU-only, optimized settings")


# Global settings instance
settings = Settings()


# Performance monitoring config
class PerformanceConfig:
    """Performance optimization parameters."""

    # Frame processing
    FRAME_SKIP = settings.FRAME_SKIP
    BATCH_SIZE = 1  # YOLO batch size
    FP16 = settings.DETECTOR_FP16

    # Detection
    DETECTION_CONF = settings.DETECTOR_CONFIDENCE
    IOU_THRESHOLD = settings.DETECTOR_IOU
    MAX_DETECTIONS = settings.MAX_DETECTIONS

    # Tracking
    TRACK_BUFFER = settings.TRACK_BUFFER
    MATCH_THRESHOLD = settings.MATCH_THRESH

    # Video I/O
    CODEC = settings.OUTPUT_CODEC
    OUTPUT_FPS = settings.OUTPUT_FPS

    # GPU
    DEVICE = settings.DETECTOR_DEVICE


perf_config = PerformanceConfig()
