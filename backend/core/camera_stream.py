"""
Real-time camera stream manager for webcam surveillance.

Handles:
- Multi-camera capture
- Frame buffering
- Stream control (start/stop)
- Integration with processing pipeline
"""

import cv2
import asyncio
import threading
import logging
import sys
from typing import Dict, Optional, Callable, List
from collections import deque
import time
import numpy as np

logger = logging.getLogger(__name__)

# Use DirectShow on Windows for better compatibility
CAMERA_BACKEND = cv2.CAP_DSHOW if sys.platform == 'win32' else cv2.CAP_ANY


class CameraStreamManager:
    """
    Manages multiple camera streams for real-time surveillance.

    Features:
    - Capture from multiple webcams simultaneously
    - Frame rate control (30 FPS target)
    - Async frame processing
    - Stream health monitoring
    """

    def __init__(self, camera_ids: List[int] = [0]):
        """
        Initialize camera stream manager.

        Args:
            camera_ids: List of camera device IDs (0 = default webcam)
        """
        self.camera_ids = camera_ids
        self.cameras: Dict[int, cv2.VideoCapture] = {}
        self.running: Dict[int, bool] = {}
        self.threads: Dict[int, threading.Thread] = {}
        self.frame_callbacks: Dict[int, Callable] = {}

        # Frame buffers for each camera
        self.frame_buffers: Dict[int, deque] = {}
        self.latest_frames: Dict[int, Optional[np.ndarray]] = {}

        # Stream statistics
        self.frame_counts: Dict[int, int] = {}
        self.fps_counters: Dict[int, float] = {}
        self.last_fps_update: Dict[int, float] = {}

        # Initialize cameras
        self._initialize_cameras()

    def _initialize_cameras(self):
        """Initialize all camera devices."""
        for cam_id in self.camera_ids:
            try:
                # Use DirectShow on Windows for better compatibility
                cap = cv2.VideoCapture(cam_id, CAMERA_BACKEND)

                if cap.isOpened():
                    # Set camera properties for optimal performance
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffering for real-time

                    self.cameras[cam_id] = cap
                    self.running[cam_id] = False
                    self.frame_buffers[cam_id] = deque(maxlen=150)  # 5 seconds @ 30 FPS
                    self.latest_frames[cam_id] = None
                    self.frame_counts[cam_id] = 0
                    self.fps_counters[cam_id] = 0.0
                    self.last_fps_update[cam_id] = time.time()

                    logger.info(f"Initialized camera {cam_id} (resolution: 1280x720, fps: 30)")
                else:
                    logger.error(f"Failed to open camera {cam_id}")

            except Exception as e:
                logger.error(f"Error initializing camera {cam_id}: {e}")

    def start_stream(self, camera_id: int, frame_callback: Optional[Callable] = None):
        """
        Start capturing frames from camera.

        Args:
            camera_id: Camera device ID
            frame_callback: Optional async callback function(camera_id, frame, frame_idx)
        """
        if camera_id not in self.cameras:
            logger.error(f"Camera {camera_id} not initialized")
            return

        if self.running.get(camera_id, False):
            logger.warning(f"Camera {camera_id} already running")
            return

        self.running[camera_id] = True

        if frame_callback:
            self.frame_callbacks[camera_id] = frame_callback

        # Start capture thread
        thread = threading.Thread(
            target=self._capture_loop,
            args=(camera_id,),
            daemon=True,
            name=f"Camera-{camera_id}"
        )
        thread.start()
        self.threads[camera_id] = thread

        logger.info(f"Started camera stream {camera_id}")

    def _capture_loop(self, camera_id: int):
        """
        Continuously capture frames from camera.

        Args:
            camera_id: Camera device ID
        """
        cap = self.cameras[camera_id]
        frame_idx = 0
        target_fps = 30
        frame_time = 1.0 / target_fps

        logger.info(f"Capture loop started for camera {camera_id}")

        while self.running.get(camera_id, False):
            loop_start = time.time()

            # Capture frame
            ret, frame = cap.read()

            if not ret:
                logger.warning(f"Failed to read frame from camera {camera_id}")
                time.sleep(0.1)
                continue

            # Store frame in buffer
            self.frame_buffers[camera_id].append(frame.copy())
            self.latest_frames[camera_id] = frame
            self.frame_counts[camera_id] += 1

            # Update FPS counter
            current_time = time.time()
            if current_time - self.last_fps_update[camera_id] >= 1.0:
                self.fps_counters[camera_id] = self.frame_counts[camera_id] - self.fps_counters[camera_id]
                self.fps_counters[camera_id] = self.frame_counts[camera_id]
                self.last_fps_update[camera_id] = current_time

            # Call frame callback if provided
            if camera_id in self.frame_callbacks:
                callback = self.frame_callbacks[camera_id]
                try:
                    # Run async callback
                    asyncio.run(callback(camera_id, frame, frame_idx))
                except Exception as e:
                    logger.error(f"Frame callback error: {e}")

            frame_idx += 1

            # Frame rate limiting
            elapsed = time.time() - loop_start
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

    def stop_stream(self, camera_id: int):
        """
        Stop camera stream.

        Args:
            camera_id: Camera device ID
        """
        if camera_id in self.running:
            self.running[camera_id] = False

            # Wait for thread to finish
            if camera_id in self.threads:
                self.threads[camera_id].join(timeout=2.0)

            logger.info(f"Stopped camera stream {camera_id}")

    def start_all_streams(self, frame_callback: Optional[Callable] = None):
        """
        Start all camera streams.

        Args:
            frame_callback: Optional async callback function(camera_id, frame, frame_idx)
        """
        for camera_id in self.camera_ids:
            if camera_id in self.cameras:
                self.start_stream(camera_id, frame_callback)
            else:
                logger.warning(f"Camera {camera_id} not available, skipping")

    def stop_all_streams(self):
        """Stop all camera streams."""
        for camera_id in list(self.running.keys()):
            self.stop_stream(camera_id)

    def release_all(self):
        """Release all camera resources."""
        self.stop_all_streams()

        for cam_id, cap in self.cameras.items():
            cap.release()
            logger.info(f"Released camera {cam_id}")

        self.cameras.clear()

    def get_latest_frame(self, camera_id: int) -> Optional[np.ndarray]:
        """
        Get most recent frame from camera.

        Args:
            camera_id: Camera device ID

        Returns:
            Latest frame or None if not available
        """
        return self.latest_frames.get(camera_id)

    def get_frame_buffer(self, camera_id: int) -> Optional[deque]:
        """
        Get frame buffer for camera (last 5 seconds).

        Args:
            camera_id: Camera device ID

        Returns:
            Frame buffer (deque) or None
        """
        return self.frame_buffers.get(camera_id)

    def get_fps(self, camera_id: int) -> float:
        """
        Get current FPS for camera.

        Args:
            camera_id: Camera device ID

        Returns:
            Current FPS
        """
        return self.fps_counters.get(camera_id, 0.0)

    def get_stream_stats(self, camera_id: int) -> dict:
        """
        Get stream statistics.

        Args:
            camera_id: Camera device ID

        Returns:
            Statistics dictionary
        """
        return {
            "camera_id": camera_id,
            "running": self.running.get(camera_id, False),
            "total_frames": self.frame_counts.get(camera_id, 0),
            "current_fps": self.fps_counters.get(camera_id, 0.0),
            "buffer_size": len(self.frame_buffers.get(camera_id, [])),
            "has_latest_frame": self.latest_frames.get(camera_id) is not None
        }

    def __del__(self):
        """Cleanup on deletion."""
        self.release_all()
