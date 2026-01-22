"""
Action Classification Module.
Rule-based action recognition from track velocity and state.
"""

from typing import Tuple, Optional

from backend.config import settings
from backend.core.tracker import TrackState


class ActionClassifier:
    """
    Rule-based action classifier.

    Actions:
    - standing: velocity < walking_threshold, not loitering
    - walking: walking_threshold <= velocity < running_threshold
    - running: velocity >= running_threshold
    - loitering: stationary for > loitering_threshold frames
    - fallen: detected by fall detector (Week 3)
    """

    def __init__(
        self,
        walking_threshold: float = None,
        running_threshold: float = None,
        loitering_threshold: int = None,
        stationary_threshold: float = None,
        fall_detector = None,
        frame_height: int = 720,
    ):
        """
        Initialize action classifier.

        Args:
            walking_threshold: Min velocity (px/frame) for walking
            running_threshold: Min velocity (px/frame) for running
            loitering_threshold: Min stationary frames for loitering
            stationary_threshold: Max velocity to be considered stationary
            fall_detector: Optional FallDetector instance
            frame_height: Video frame height for fall detection
        """
        self.walking_threshold = (
            walking_threshold or settings.VELOCITY_WALKING_THRESHOLD
        )
        self.running_threshold = (
            running_threshold or settings.VELOCITY_RUNNING_THRESHOLD
        )
        self.loitering_threshold = (
            loitering_threshold or settings.LOITERING_THRESHOLD
        )
        self.stationary_threshold = (
            stationary_threshold or settings.STATIONARY_VELOCITY_THRESHOLD
        )
        self.frame_height = frame_height

        # Fall detection (Week 3)
        self.fall_detector = fall_detector
        if self.fall_detector is None and settings.FALL_DETECTION_ENABLED:
            from backend.core.fall_detector import FallDetector
            self.fall_detector = FallDetector(frame_height=frame_height)

        print(
            f"✓ Action classifier initialized (walk>{self.walking_threshold}, "
            f"run>{self.running_threshold}, loiter>{self.loitering_threshold}, "
            f"fall_detection={'ON' if self.fall_detector else 'OFF'})"
        )

    def classify(self, track_dict: dict) -> Tuple[str, float]:
        """
        Classify action for a track.

        Args:
            track_dict: Track dictionary containing 'state' (TrackState)

        Returns:
            Tuple of (action_label, confidence)
        """
        state: TrackState = track_dict["state"]
        velocity = state.get_velocity()

        # Update stationary frame counter
        if velocity < self.stationary_threshold:
            state.stationary_frames += 1
        else:
            state.stationary_frames = 0

        # PRIORITY 1: Check for fall (CRITICAL event)
        if self.fall_detector is not None:
            is_fallen, fall_confidence = self.fall_detector.detect_fall(
                state, frame_height=self.frame_height
            )
            if is_fallen:
                return "fallen", fall_confidence

        # PRIORITY 2: Check for loitering
        if state.stationary_frames > self.loitering_threshold:
            return "loitering", 0.95

        # PRIORITY 3: Movement-based actions
        elif velocity >= self.running_threshold:
            return "running", 0.85

        elif velocity >= self.walking_threshold:
            return "walking", 0.80

        else:
            return "standing", 0.75

    def classify_batch(self, tracks: list[dict]) -> list[Tuple[str, float]]:
        """
        Classify actions for multiple tracks.

        Args:
            tracks: List of track dictionaries

        Returns:
            List of (action, confidence) tuples
        """
        return [self.classify(track) for track in tracks]

    def get_config(self) -> dict:
        """Get classifier configuration."""
        return {
            "type": "rule_based",
            "walking_threshold": self.walking_threshold,
            "running_threshold": self.running_threshold,
            "loitering_threshold": self.loitering_threshold,
            "stationary_threshold": self.stationary_threshold,
        }


class MLActionClassifier:
    """
    Placeholder for ML-based action classifier (Phase 2).

    Will use X3D or MoViNet for clip-based action recognition.
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None
        raise NotImplementedError(
            "ML action classifier not yet implemented (Week 4+)"
        )

    def classify(self, clip: list) -> Tuple[str, float]:
        """Classify action from video clip."""
        raise NotImplementedError()
