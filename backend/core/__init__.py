"""
Core processing modules for SentinelAI.

Imports are conditional to allow basic functionality (like camera streaming)
even when ML dependencies (ultralytics, etc.) are not installed.
"""

# Camera streaming always available (only needs opencv)
from .camera_stream import CameraStreamManager

__all__ = ["CameraStreamManager"]

# Optional ML-dependent imports
try:
    from .detector import YOLOv8Detector
    from .tracker import ByteTracker
    from .actions import ActionClassifier
    from .events import EventLogger
    from .video_io import VideoReader, VideoWriter
    from .pipeline import VideoPipeline

    __all__.extend([
        "YOLOv8Detector",
        "ByteTracker",
        "ActionClassifier",
        "EventLogger",
        "VideoReader",
        "VideoWriter",
        "VideoPipeline",
    ])
except ImportError:
    pass  # ML features not available
