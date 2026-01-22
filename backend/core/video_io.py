"""
Video I/O utilities.
Handles video reading, writing, and frame extraction.
"""

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np


class VideoReader:
    """
    Video reader with frame extraction.

    Features:
    - Iterator interface for frame-by-frame processing
    - Frame skipping support
    - Video metadata extraction
    """

    def __init__(self, video_path: Path, frame_skip: int = 1):
        """
        Initialize video reader.

        Args:
            video_path: Path to input video
            frame_skip: Process every Nth frame (default: 1 = all frames)
        """
        self.video_path = Path(video_path)
        self.frame_skip = frame_skip

        if not self.video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        # Open video
        self.cap = cv2.VideoCapture(str(video_path))

        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")

        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.duration_sec = self.total_frames / self.fps if self.fps > 0 else 0

        self.current_frame = 0

        print(f"✓ Video loaded: {self.width}x{self.height} @ {self.fps:.1f} fps, "
              f"{self.total_frames} frames ({self.duration_sec:.1f}s)")

    def __iter__(self):
        """Make reader iterable."""
        return self

    def __next__(self) -> Tuple[int, np.ndarray]:
        """
        Get next frame.

        Returns:
            Tuple of (frame_id, frame_array)

        Raises:
            StopIteration when video ends
        """
        while True:
            ret, frame = self.cap.read()

            if not ret:
                raise StopIteration

            frame_id = self.current_frame
            self.current_frame += 1

            # Apply frame skipping
            if frame_id % self.frame_skip == 0:
                return frame_id, frame

    def read_frame(self, frame_id: int) -> Optional[np.ndarray]:
        """
        Read a specific frame by ID.

        Args:
            frame_id: Frame number to read

        Returns:
            Frame array or None if failed
        """
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = self.cap.read()
        return frame if ret else None

    def get_metadata(self) -> dict:
        """Get video metadata."""
        return {
            "path": str(self.video_path),
            "fps": self.fps,
            "total_frames": self.total_frames,
            "width": self.width,
            "height": self.height,
            "duration_sec": self.duration_sec,
            "frame_skip": self.frame_skip,
        }

    def release(self):
        """Release video capture."""
        if self.cap is not None:
            self.cap.release()

    def __del__(self):
        """Cleanup on deletion."""
        self.release()


class VideoWriter:
    """
    Video writer with annotation support.

    Features:
    - Configurable codec and FPS
    - Automatic resolution handling
    """

    def __init__(
        self,
        output_path: Path,
        fps: float,
        frame_size: Tuple[int, int],
        codec: str = "mp4v",
    ):
        """
        Initialize video writer.

        Args:
            output_path: Path to output video
            fps: Output frames per second
            frame_size: (width, height) of output video
            codec: FourCC codec (default: mp4v)
        """
        self.output_path = Path(output_path)
        self.fps = fps
        self.frame_size = frame_size
        self.codec = codec

        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.writer = cv2.VideoWriter(
            str(output_path), fourcc, fps, frame_size
        )

        if not self.writer.isOpened():
            raise ValueError(f"Failed to create video writer: {output_path}")

        self.frame_count = 0
        print(f"✓ Video writer created: {output_path}")

    def write(self, frame: np.ndarray):
        """
        Write a frame to video.

        Args:
            frame: Frame array (H, W, 3) in BGR format
        """
        # Ensure frame matches expected size
        if frame.shape[:2] != (self.frame_size[1], self.frame_size[0]):
            frame = cv2.resize(frame, self.frame_size)

        self.writer.write(frame)
        self.frame_count += 1

    def release(self):
        """Release video writer."""
        if self.writer is not None:
            self.writer.release()
            print(f"✓ Video written: {self.frame_count} frames to {self.output_path}")

    def __del__(self):
        """Cleanup on deletion."""
        self.release()


def extract_frame_at_time(video_path: Path, time_sec: float) -> Optional[np.ndarray]:
    """
    Extract a single frame at a specific time.

    Args:
        video_path: Path to video
        time_sec: Time in seconds

    Returns:
        Frame array or None if failed
    """
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        return None

    # Seek to time
    cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)
    ret, frame = cap.read()

    cap.release()

    return frame if ret else None
