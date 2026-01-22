"""
ByteTrack Multi-Object Tracker.
Wraps BoxMOT's ByteTrack implementation for person tracking.
"""

from collections import deque
from typing import Dict, List

import numpy as np
from boxmot import ByteTrack

from backend.config import settings


class TrackState:
    """
    State history for a single track.
    Stores bbox history, computes velocity, and tracks stationary time.
    """

    def __init__(self, track_id: int, max_history: int = 30):
        """
        Initialize track state.

        Args:
            track_id: Unique track identifier
            max_history: Maximum frames to store in history (default: 30 = 1s @ 30fps)
        """
        self.track_id = track_id
        self.history = deque(maxlen=max_history)
        self.stationary_frames = 0
        self.total_frames = 0
        self.first_seen_frame = None
        self.last_seen_frame = None

    def update(self, bbox: List[float], frame_id: int):
        """
        Update track with new detection.

        Args:
            bbox: [x1, y1, x2, y2]
            frame_id: Current frame number
        """
        centroid = self._get_centroid(bbox)

        self.history.append(
            {"frame_id": frame_id, "bbox": bbox, "centroid": centroid}
        )

        if self.first_seen_frame is None:
            self.first_seen_frame = frame_id

        self.last_seen_frame = frame_id
        self.total_frames += 1

    def get_velocity(self) -> float:
        """
        Compute average velocity over recent history.

        Returns:
            Average velocity in pixels per frame
        """
        if len(self.history) < 2:
            return 0.0

        # Use last 10 frames for smoothing
        recent = list(self.history)[-10:]
        distances = []

        for i in range(1, len(recent)):
            prev_centroid = np.array(recent[i - 1]["centroid"])
            curr_centroid = np.array(recent[i]["centroid"])
            dist = np.linalg.norm(curr_centroid - prev_centroid)
            distances.append(dist)

        return float(np.mean(distances)) if distances else 0.0

    def get_current_bbox(self) -> List[float]:
        """Get most recent bounding box."""
        if not self.history:
            return [0, 0, 0, 0]
        return self.history[-1]["bbox"]

    def get_duration_frames(self) -> int:
        """Get total track duration in frames."""
        return self.total_frames

    def _get_centroid(self, bbox: List[float]) -> tuple:
        """Compute bbox centroid."""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)


class ByteTracker:
    """
    ByteTrack wrapper for multi-object tracking.

    Features:
    - Motion-based tracking (no ReID)
    - Track state management with history
    - Velocity computation per track
    """

    def __init__(
        self,
        track_thresh: float = None,
        track_buffer: int = None,
        match_thresh: float = None,
    ):
        """
        Initialize ByteTrack tracker.

        Args:
            track_thresh: Detection confidence threshold for tracking
            track_buffer: Number of frames to buffer lost tracks
            match_thresh: IoU threshold for matching
        """
        self.track_thresh = track_thresh or settings.TRACK_THRESH
        self.track_buffer = track_buffer or settings.TRACK_BUFFER
        self.match_thresh = match_thresh or settings.MATCH_THRESH

        # Initialize ByteTrack
        self.tracker = ByteTrack(
            track_thresh=self.track_thresh,
            track_buffer=self.track_buffer,
            match_thresh=self.match_thresh,
            frame_rate=30,  # Default, will be adjusted per video
        )

        # Track state management
        self.track_states: Dict[int, TrackState] = {}
        self.active_track_ids = set()

        print(
            f"✓ Tracker initialized (thresh={self.track_thresh}, buffer={self.track_buffer})"
        )

    def update(self, detections: np.ndarray, frame_id: int, frame: np.ndarray = None) -> List[dict]:
        """
        Update tracker with new detections.

        Args:
            detections: Nx6 array of [x1, y1, x2, y2, conf, cls]
            frame_id: Current frame number
            frame: Current frame image (required by ByteTrack)

        Returns:
            List of track dictionaries with state
        """
        if len(detections) == 0:
            # No detections, return empty
            return []

        # Run ByteTrack
        # ByteTrack expects format: [x1, y1, x2, y2, conf, cls]
        # Returns: [x1, y1, x2, y2, track_id, conf, class_id, index]
        # Note: ByteTrack requires the image parameter
        tracks = self.tracker.update(detections, frame)

        # Process tracks
        updated_tracks = []

        if len(tracks) > 0:
            current_track_ids = set()

            for track in tracks:
                x1, y1, x2, y2 = track[:4]
                track_id = int(track[4])
                conf = track[5] if len(track) > 5 else 1.0

                current_track_ids.add(track_id)

                # Initialize or update track state
                if track_id not in self.track_states:
                    self.track_states[track_id] = TrackState(track_id)

                state = self.track_states[track_id]
                state.update([x1, y1, x2, y2], frame_id)

                updated_tracks.append(
                    {
                        "track_id": track_id,
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "confidence": float(conf),
                        "state": state,
                    }
                )

            self.active_track_ids = current_track_ids

        return updated_tracks

    def get_track_state(self, track_id: int) -> TrackState:
        """Get state for a specific track."""
        return self.track_states.get(track_id)

    def get_all_tracks(self) -> Dict[int, TrackState]:
        """Get all track states."""
        return self.track_states

    def reset(self):
        """Reset tracker state."""
        self.tracker = ByteTrack(
            track_thresh=self.track_thresh,
            track_buffer=self.track_buffer,
            match_thresh=self.match_thresh,
            frame_rate=30,
        )
        self.track_states.clear()
        self.active_track_ids.clear()

    def get_tracker_info(self) -> dict:
        """Get tracker configuration."""
        return {
            "type": "ByteTrack",
            "track_thresh": self.track_thresh,
            "track_buffer": self.track_buffer,
            "match_thresh": self.match_thresh,
            "total_tracks": len(self.track_states),
            "active_tracks": len(self.active_track_ids),
        }
