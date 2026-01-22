"""
Event-based video clip recorder.

Records short video clips (5-10 seconds) for important events:
- Person first appears
- Gesture detected
- Voice detected
"""

import cv2
import numpy as np
from typing import List, Optional
from collections import deque
from pathlib import Path
import logging
import time
import os

logger = logging.getLogger(__name__)


class EventClipRecorder:
    """
    Records short video clips for important surveillance events.

    Features:
    - Rolling frame buffer (captures 5 seconds before event)
    - H.264 video encoding
    - Automatic clip generation on events
    - File size optimization
    """

    def __init__(
        self,
        output_dir: str = "data/clips",
        buffer_seconds: int = 5,
        fps: int = 30,
        codec: str = "h264"
    ):
        """
        Initialize event clip recorder.

        Args:
            output_dir: Directory to save clips
            buffer_seconds: Seconds of video to keep in buffer (before event)
            fps: Target frames per second
            codec: Video codec (h264, mp4v, xvid)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.buffer_seconds = buffer_seconds
        self.fps = fps
        self.codec = codec

        # Frame buffer (circular buffer)
        buffer_size = buffer_seconds * fps
        self.frame_buffer = deque(maxlen=buffer_size)

        # Codec configuration
        self.fourcc = self._get_fourcc(codec)

        logger.info(f"Initialized EventClipRecorder (buffer: {buffer_seconds}s, fps: {fps}, codec: {codec})")

    def _get_fourcc(self, codec: str) -> int:
        """Get OpenCV FourCC code for codec."""
        codec_map = {
            "h264": cv2.VideoWriter_fourcc(*'H264'),
            "x264": cv2.VideoWriter_fourcc(*'X264'),
            "mp4v": cv2.VideoWriter_fourcc(*'mp4v'),
            "xvid": cv2.VideoWriter_fourcc(*'XVID'),
            "mjpeg": cv2.VideoWriter_fourcc(*'MJPG')
        }
        return codec_map.get(codec.lower(), cv2.VideoWriter_fourcc(*'H264'))

    def add_frame(self, frame: np.ndarray):
        """
        Add frame to rolling buffer.

        Args:
            frame: Video frame (H, W, 3)
        """
        self.frame_buffer.append(frame.copy())

    def record_event_clip(
        self,
        person_id: str,
        event_type: str,
        camera_id: int = 0,
        post_event_frames: int = 150,
        timestamp: Optional[float] = None
    ) -> Optional[str]:
        """
        Record video clip for event.

        Combines buffered frames (before event) + post-event frames.

        Args:
            person_id: Person identifier
            event_type: Event type (person_appeared, gesture_detected, voice_detected)
            camera_id: Camera source ID
            post_event_frames: Frames to capture after event (default: 150 = 5s @ 30fps)
            timestamp: Event timestamp (default: current time)

        Returns:
            Path to saved clip file, or None if failed
        """
        if len(self.frame_buffer) == 0:
            logger.warning("No frames in buffer, cannot record clip")
            return None

        try:
            # Generate filename
            if timestamp is None:
                timestamp = time.time()

            timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(timestamp))
            filename = f"{person_id}_{timestamp_str}_{event_type}_cam{camera_id}.mp4"
            clip_path = self.output_dir / filename

            # Get all buffered frames
            buffered_frames = list(self.frame_buffer)

            # Total frames = buffered + post-event
            # (In practice, post_event_frames would come from live stream)
            # For now, we just use buffered frames
            all_frames = buffered_frames

            if len(all_frames) == 0:
                logger.warning("No frames to write")
                return None

            # Get frame dimensions
            height, width = all_frames[0].shape[:2]

            # Create video writer
            writer = cv2.VideoWriter(
                str(clip_path),
                self.fourcc,
                self.fps,
                (width, height)
            )

            if not writer.isOpened():
                logger.error(f"Failed to open video writer for {clip_path}")
                return None

            # Write frames
            for frame in all_frames:
                writer.write(frame)

            writer.release()

            # Get file size
            file_size = os.path.getsize(clip_path)
            duration = len(all_frames) / self.fps

            logger.info(
                f"Saved event clip: {filename} "
                f"(duration: {duration:.1f}s, size: {file_size / 1024 / 1024:.2f} MB, frames: {len(all_frames)})"
            )

            return str(clip_path)

        except Exception as e:
            logger.error(f"Failed to record event clip: {e}")
            return None

    def record_clip_from_frames(
        self,
        frames: List[np.ndarray],
        person_id: str,
        event_type: str,
        camera_id: int = 0,
        timestamp: Optional[float] = None
    ) -> Optional[str]:
        """
        Record clip directly from list of frames (alternative method).

        Args:
            frames: List of video frames
            person_id: Person identifier
            event_type: Event type
            camera_id: Camera source ID
            timestamp: Event timestamp

        Returns:
            Path to saved clip file, or None if failed
        """
        if not frames:
            logger.warning("No frames provided")
            return None

        try:
            # Generate filename
            if timestamp is None:
                timestamp = time.time()

            timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(timestamp))
            filename = f"{person_id}_{timestamp_str}_{event_type}_cam{camera_id}.mp4"
            clip_path = self.output_dir / filename

            # Get frame dimensions
            height, width = frames[0].shape[:2]

            # Create video writer
            writer = cv2.VideoWriter(
                str(clip_path),
                self.fourcc,
                self.fps,
                (width, height)
            )

            if not writer.isOpened():
                logger.error(f"Failed to open video writer for {clip_path}")
                return None

            # Write frames
            for frame in frames:
                writer.write(frame)

            writer.release()

            # Get file size
            file_size = os.path.getsize(clip_path)
            duration = len(frames) / self.fps

            logger.info(
                f"Saved event clip: {filename} "
                f"(duration: {duration:.1f}s, size: {file_size / 1024 / 1024:.2f} MB, frames: {len(frames)})"
            )

            return str(clip_path)

        except Exception as e:
            logger.error(f"Failed to record clip from frames: {e}")
            return None

    def get_buffer_stats(self) -> dict:
        """Get statistics about frame buffer."""
        return {
            "buffer_size": len(self.frame_buffer),
            "max_buffer_size": self.frame_buffer.maxlen,
            "buffer_duration_seconds": len(self.frame_buffer) / self.fps if self.fps > 0 else 0,
            "fps": self.fps,
            "codec": self.codec
        }

    def clear_buffer(self):
        """Clear frame buffer."""
        self.frame_buffer.clear()
        logger.info("Cleared frame buffer")
