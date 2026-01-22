"""
Fall Detection Module.

Detects falls using:
- Aspect ratio analysis (horizontal orientation when fallen)
- Vertical velocity (rapid downward movement)
- Ground proximity (bbox near bottom of frame)
- Post-fall stationary duration
"""

from typing import List, Tuple

import numpy as np

from backend.config import settings
from backend.core.tracker import TrackState


class FallDetector:
    """
    Detect falls from track history using heuristic analysis.

    Detection criteria:
    1. Aspect ratio: Width > Height (person lying down)
    2. Vertical velocity: Rapid descent detected
    3. Ground proximity: Person near bottom of frame
    4. Post-fall: Stationary after rapid descent
    """

    def __init__(
        self,
        aspect_ratio_threshold: float = None,
        vertical_velocity_threshold: float = None,
        ground_proximity_threshold: float = None,
        stationary_duration: int = None,
        frame_height: int = 720,  # Default frame height
    ):
        """
        Initialize fall detector.

        Args:
            aspect_ratio_threshold: Min width/height ratio for fallen person (default: 0.8)
            vertical_velocity_threshold: Min downward velocity in px/frame (default: 20.0)
            ground_proximity_threshold: Max distance from bottom (0-1, default: 0.8)
            stationary_duration: Min frames stationary after fall (default: 150 = 5s @ 30fps)
            frame_height: Video frame height in pixels
        """
        self.aspect_ratio_threshold = (
            aspect_ratio_threshold
            if aspect_ratio_threshold is not None
            else settings.FALL_ASPECT_RATIO_THRESHOLD
        )
        self.vertical_velocity_threshold = (
            vertical_velocity_threshold
            if vertical_velocity_threshold is not None
            else settings.FALL_VERTICAL_VELOCITY_THRESHOLD
        )
        self.ground_proximity_threshold = (
            ground_proximity_threshold
            if ground_proximity_threshold is not None
            else settings.FALL_GROUND_PROXIMITY_THRESHOLD
        )
        self.stationary_duration = (
            stationary_duration
            if stationary_duration is not None
            else settings.FALL_STATIONARY_DURATION
        )
        self.frame_height = frame_height

        # Track fall states
        self.fallen_tracks: set = set()  # Track IDs confirmed as fallen

    def detect_fall(self, track_state: TrackState, frame_height: int = None) -> Tuple[bool, float]:
        """
        Detect if a track represents a fallen person.

        Args:
            track_state: TrackState object with history
            frame_height: Current frame height (overrides default)

        Returns:
            (is_fallen, confidence): Bool and confidence score (0-1)
        """
        if frame_height is not None:
            self.frame_height = frame_height

        # Need sufficient history
        if len(track_state.history) < 5:
            return False, 0.0

        # Get current bbox
        current_bbox = track_state.get_current_bbox()

        # Check 1: Aspect ratio (lying down)
        aspect_ratio_score = self._check_aspect_ratio(current_bbox)

        # Check 2: Vertical velocity (rapid descent)
        vertical_velocity_score = self._check_vertical_velocity(track_state)

        # Check 3: Ground proximity
        ground_proximity_score = self._check_ground_proximity(current_bbox)

        # Check 4: Post-fall stationary
        stationary_score = self._check_stationary(track_state)

        # Combine scores
        # Fall requires: aspect ratio OR (vertical velocity + stationary)
        # Ground proximity is a bonus

        # Method 1: Lying down + near ground + stationary
        lying_down_score = (aspect_ratio_score * 0.5 +
                           ground_proximity_score * 0.3 +
                           stationary_score * 0.2)

        # Method 2: Rapid descent + stationary + near ground
        rapid_descent_score = (vertical_velocity_score * 0.5 +
                              stationary_score * 0.3 +
                              ground_proximity_score * 0.2)

        # Take maximum of both methods
        confidence = max(lying_down_score, rapid_descent_score)

        # Threshold for fall detection
        is_fallen = confidence > 0.6

        # Update fallen tracks set
        if is_fallen:
            self.fallen_tracks.add(track_state.track_id)
        elif track_state.track_id in self.fallen_tracks and confidence < 0.3:
            # Person got up
            self.fallen_tracks.discard(track_state.track_id)

        return is_fallen, float(confidence)

    def _check_aspect_ratio(self, bbox: List[float]) -> float:
        """
        Check if bbox has horizontal orientation (lying down).

        Returns:
            Score 0-1 (1 = definitely horizontal)
        """
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1

        if height == 0:
            return 0.0

        aspect_ratio = width / height

        # When lying down, width > height (aspect ratio > 1.0)
        # Normal standing person: aspect ratio ~ 0.4-0.6
        # Sitting: aspect ratio ~ 0.6-0.8
        # Lying down: aspect ratio > 1.0

        if aspect_ratio >= self.aspect_ratio_threshold:
            # Normalize to 0-1 range
            # aspect_ratio of 1.2 = full score
            score = min(1.0, (aspect_ratio - self.aspect_ratio_threshold) / 0.4)
            return score

        return 0.0

    def _check_vertical_velocity(self, track_state: TrackState) -> float:
        """
        Check for rapid downward movement.

        Returns:
            Score 0-1 (1 = rapid descent detected)
        """
        if len(track_state.history) < 3:
            return 0.0

        # Look at last 5 frames for vertical movement
        recent = list(track_state.history)[-5:]

        vertical_velocities = []
        for i in range(1, len(recent)):
            prev_y = recent[i - 1]["centroid"][1]
            curr_y = recent[i]["centroid"][1]
            v_velocity = curr_y - prev_y  # Positive = downward
            vertical_velocities.append(v_velocity)

        if not vertical_velocities:
            return 0.0

        avg_vertical_velocity = np.mean(vertical_velocities)

        # Check for downward movement
        if avg_vertical_velocity > self.vertical_velocity_threshold:
            # Normalize to 0-1 range
            # 30 px/frame = full score
            score = min(1.0, avg_vertical_velocity / 30.0)
            return score

        return 0.0

    def _check_ground_proximity(self, bbox: List[float]) -> float:
        """
        Check if person is near the bottom of the frame.

        Returns:
            Score 0-1 (1 = very close to ground)
        """
        x1, y1, x2, y2 = bbox

        # Bottom of bbox relative to frame height
        bottom_position = y2 / self.frame_height

        # Near ground if bottom is at threshold or below
        if bottom_position >= self.ground_proximity_threshold:
            # Normalize to 0-1
            # 1.0 (frame bottom) = full score
            score = min(1.0, (bottom_position - self.ground_proximity_threshold) /
                       (1.0 - self.ground_proximity_threshold))
            return score

        return 0.0

    def _check_stationary(self, track_state: TrackState) -> float:
        """
        Check if person has been stationary (after potential fall).

        Returns:
            Score 0-1 (1 = stationary for full duration)
        """
        # Use stationary_frames from track state
        stationary_frames = track_state.stationary_frames

        # Normalize to 0-1
        score = min(1.0, stationary_frames / self.stationary_duration)

        return score

    def is_track_fallen(self, track_id: int) -> bool:
        """
        Check if a track ID is currently marked as fallen.

        Args:
            track_id: Track identifier

        Returns:
            True if track is fallen
        """
        return track_id in self.fallen_tracks

    def reset(self):
        """Reset fallen tracks state."""
        self.fallen_tracks.clear()
