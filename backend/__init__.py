"""
SentinelAI Backend
Smart Surveillance System with AI-powered Detection, Tracking, and Action Recognition

Version: 0.1.0 (Day 1-2 MVP)
"""

__version__ = "0.1.0"
__author__ = "SentinelAI Contributors"

# Core imports for easy access (optional - allow API to start without ML dependencies)
__all__ = ["settings"]

try:
    from backend.core import (
        VideoPipeline,
        YOLOv8Detector,
        ByteTracker,
        ActionClassifier,
        EventLogger,
        VideoReader,
        VideoWriter,
    )

    from backend.utils import (
        PerformanceMonitor,
        draw_annotations,
    )

    __all__.extend([
        "VideoPipeline",
        "YOLOv8Detector",
        "ByteTracker",
        "ActionClassifier",
        "EventLogger",
        "VideoReader",
        "VideoWriter",
        "PerformanceMonitor",
        "draw_annotations",
    ])
except ImportError as e:
    import warnings
    warnings.warn(f"ML dependencies not available: {e}. Some features will be disabled.")

from backend.config import settings
