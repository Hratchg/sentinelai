"""
Fight Detection Module.

Detects potential fights using:
- Proximity detection (bbox IoU overlap)
- Rapid movement analysis (both participants)
- Multi-person requirement (minimum 2 people)
- Duration threshold (sustained interaction)
"""

from typing import Dict, List, Tuple
import time

import numpy as np

from backend.config import settings
from backend.core.tracker import TrackState


class FightDetector:
    """
    Detect fights between multiple people using heuristic analysis.

    Detection criteria:
    1. Proximity: High IoU overlap between bboxes
    2. Rapid movement: Both participants moving quickly
    3. Duration: Interaction sustained for minimum duration
    4. Participant count: At least 2 people involved
    """

    def __init__(
        self,
        proximity_iou_threshold: float = None,
        rapid_movement_threshold: float = None,
        min_duration_frames: int = None,
        min_participants: int = None,
    ):
        """
        Initialize fight detector.

        Args:
            proximity_iou_threshold: Min IoU between bboxes (default: 0.3)
            rapid_movement_threshold: Min velocity for rapid movement (default: 15.0)
            min_duration_frames: Min frames for sustained fight (default: 60 = 2s @ 30fps)
            min_participants: Min people involved (default: 2)
        """
        self.proximity_iou_threshold = (
            proximity_iou_threshold
            if proximity_iou_threshold is not None
            else settings.FIGHT_PROXIMITY_IOU_THRESHOLD
        )
        self.rapid_movement_threshold = (
            rapid_movement_threshold
            if rapid_movement_threshold is not None
            else settings.FIGHT_RAPID_MOVEMENT_THRESHOLD
        )
        self.min_duration_frames = (
            min_duration_frames
            if min_duration_frames is not None
            else settings.FIGHT_MIN_DURATION_FRAMES
        )
        self.min_participants = (
            min_participants
            if min_participants is not None
            else settings.FIGHT_MIN_PARTICIPANTS
        )

        # Track potential fight pairs
        # Format: {(track_id1, track_id2): {'start_frame': int, 'last_frame': int, 'confidence': float}}
        self.potential_fights: Dict[Tuple[int, int], dict] = {}

    def detect_fights(
        self, tracks: List[dict], frame_id: int
    ) -> List[dict]:
        """
        Detect potential fights between tracks.

        Args:
            tracks: List of track dicts with bbox, track_id, state
            frame_id: Current frame number

        Returns:
            List of fight event dicts with participants and confidence
        """
        if len(tracks) < self.min_participants:
            return []

        fight_events = []

        # Check all pairs of tracks
        for i, track1 in enumerate(tracks):
            for track2 in tracks[i + 1:]:
                fight_info = self._check_fight_conditions(track1, track2, frame_id)

                if fight_info is not None:
                    fight_events.append(fight_info)

        # Clean up old potential fights
        self._cleanup_potential_fights(frame_id)

        return fight_events

    def _check_fight_conditions(
        self, track1: dict, track2: dict, frame_id: int
    ) -> dict:
        """
        Check if two tracks meet fight criteria.

        Args:
            track1: First track dict
            track2: Second track dict
            frame_id: Current frame

        Returns:
            Fight event dict if detected, None otherwise
        """
        track_id1 = track1["track_id"]
        track_id2 = track2["track_id"]
        bbox1 = track1["bbox"]
        bbox2 = track2["bbox"]
        state1: TrackState = track1["state"]
        state2: TrackState = track2["state"]

        # Criterion 1: Proximity (IoU overlap)
        iou = self._compute_iou(bbox1, bbox2)
        proximity_score = min(1.0, iou / self.proximity_iou_threshold) if iou > 0 else 0.0

        # Criterion 2: Rapid movement (both participants)
        velocity1 = state1.get_velocity()
        velocity2 = state2.get_velocity()

        movement_score = 0.0
        if velocity1 >= self.rapid_movement_threshold or velocity2 >= self.rapid_movement_threshold:
            # At least one person moving quickly
            avg_velocity = (velocity1 + velocity2) / 2
            movement_score = min(1.0, avg_velocity / self.rapid_movement_threshold)

        # Criterion 3: Duration (sustained interaction)
        pair_key = tuple(sorted([track_id1, track_id2]))

        if pair_key not in self.potential_fights:
            # New potential fight
            if proximity_score > 0.5 and movement_score > 0.5:
                self.potential_fights[pair_key] = {
                    "start_frame": frame_id,
                    "last_frame": frame_id,
                    "max_confidence": proximity_score * movement_score,
                }
            duration_score = 0.0
        else:
            # Existing potential fight
            fight_data = self.potential_fights[pair_key]
            fight_data["last_frame"] = frame_id
            duration_frames = frame_id - fight_data["start_frame"]
            duration_score = min(1.0, duration_frames / self.min_duration_frames)

            # Update max confidence
            current_conf = proximity_score * movement_score
            if current_conf > fight_data["max_confidence"]:
                fight_data["max_confidence"] = current_conf

        # Combined confidence
        confidence = (proximity_score * 0.4 +
                     movement_score * 0.4 +
                     duration_score * 0.2)

        # Threshold for fight detection
        if confidence > 0.6 and duration_score > 0.0:
            return {
                "event_type": "fight",
                "participants": [track_id1, track_id2],
                "confidence": float(confidence),
                "frame_id": frame_id,
                "iou": float(iou),
                "velocities": [float(velocity1), float(velocity2)],
                "duration_frames": int(frame_id - self.potential_fights[pair_key]["start_frame"]),
            }

        return None

    def _compute_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """
        Compute Intersection over Union between two bboxes.

        Args:
            bbox1: [x1, y1, x2, y2]
            bbox2: [x1, y1, x2, y2]

        Returns:
            IoU score (0-1)
        """
        x1_min, y1_min, x1_max, y1_max = bbox1
        x2_min, y2_min, x2_max, y2_max = bbox2

        # Intersection area
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)

        inter_width = max(0, inter_x_max - inter_x_min)
        inter_height = max(0, inter_y_max - inter_y_min)
        inter_area = inter_width * inter_height

        # Union area
        bbox1_area = (x1_max - x1_min) * (y1_max - y1_min)
        bbox2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = bbox1_area + bbox2_area - inter_area

        if union_area == 0:
            return 0.0

        return inter_area / union_area

    def _cleanup_potential_fights(self, current_frame: int, max_gap: int = 30):
        """
        Remove stale potential fights that haven't been updated recently.

        Args:
            current_frame: Current frame number
            max_gap: Maximum frames without update before removal
        """
        stale_pairs = []

        for pair_key, fight_data in self.potential_fights.items():
            if current_frame - fight_data["last_frame"] > max_gap:
                stale_pairs.append(pair_key)

        for pair_key in stale_pairs:
            del self.potential_fights[pair_key]

    def reset(self):
        """Reset potential fights state."""
        self.potential_fights.clear()

    def get_stats(self) -> dict:
        """Get current fight detector statistics."""
        return {
            "active_potential_fights": len(self.potential_fights),
            "fight_pairs": list(self.potential_fights.keys()),
        }
