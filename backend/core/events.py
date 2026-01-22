"""
Event Generation and Management.
Creates structured event logs from track actions.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from backend.core.tracker import TrackState


class EventLogger:
    """
    Event logger for surveillance events.

    Features:
    - Action change detection (only log when action changes)
    - Structured event format with metadata
    - Filtering by action, track, time range
    - JSON export
    """

    def __init__(self, job_id: str = None, fps: float = 30.0):
        """
        Initialize event logger.

        Args:
            job_id: Job identifier for this processing session
            fps: Video frames per second (for timestamp conversion)
        """
        self.job_id = job_id or "unknown"
        self.fps = fps
        self.events: List[dict] = []
        self.last_action: Dict[int, str] = {}  # track_id -> last action
        self.event_counts: Dict[str, int] = {
            "standing": 0,
            "walking": 0,
            "running": 0,
            "loitering": 0,
            "fallen": 0,  # Week 3
            "fight": 0,  # Week 3
        }

    def create_event(
        self,
        frame_id: int,
        track: dict,
        action: str,
        confidence: float,
    ) -> Optional[dict]:
        """
        Create an event if action has changed.

        Args:
            frame_id: Current frame number
            track: Track dictionary with bbox, state, etc.
            action: Action label (standing, walking, running, loitering)
            confidence: Action confidence score

        Returns:
            Event dict if created, None if action unchanged
        """
        track_id = track["track_id"]
        state: TrackState = track["state"]

        # Only log if action changed (reduce noise)
        if track_id in self.last_action and self.last_action[track_id] == action:
            return None

        self.last_action[track_id] = action
        self.event_counts[action] = self.event_counts.get(action, 0) + 1

        # Create event
        event = {
            "job_id": self.job_id,
            "timestamp": self._frame_to_timestamp(frame_id),
            "frame_number": frame_id,
            "time_seconds": round(frame_id / self.fps, 2),
            "track_id": track_id,
            "bbox": [round(x, 1) for x in track["bbox"]],
            "action": action,
            "confidence": round(confidence, 3),
            "metadata": {
                "velocity_px_per_frame": round(state.get_velocity(), 2),
                "stationary_frames": state.stationary_frames,
                "bbox_area": self._compute_area(track["bbox"]),
                "track_duration_frames": state.get_duration_frames(),
                "detection_confidence": round(track.get("confidence", 1.0), 3),
            },
        }

        self.events.append(event)
        return event

    def create_fight_event(
        self,
        frame_id: int,
        participant_ids: List[int],
        confidence: float,
        metadata: dict = None,
    ) -> dict:
        """
        Create a fight event (Week 3).

        Args:
            frame_id: Current frame number
            participant_ids: List of track IDs involved in fight
            confidence: Fight confidence score
            metadata: Additional fight metadata (iou, velocities, etc.)

        Returns:
            Fight event dict
        """
        self.event_counts["fight"] = self.event_counts.get("fight", 0) + 1

        event = {
            "job_id": self.job_id,
            "event_type": "fight",
            "timestamp": self._frame_to_timestamp(frame_id),
            "frame_number": frame_id,
            "time_seconds": round(frame_id / self.fps, 2),
            "participant_track_ids": participant_ids,
            "confidence": round(confidence, 3),
            "severity": "high",
            "metadata": metadata or {},
        }

        self.events.append(event)
        return event

    def get_events(self) -> List[dict]:
        """Get all events."""
        return self.events

    def filter_events(
        self,
        actions: Optional[List[str]] = None,
        track_ids: Optional[List[int]] = None,
        time_range: Optional[tuple] = None,
    ) -> List[dict]:
        """
        Filter events by criteria.

        Args:
            actions: Filter by action labels
            track_ids: Filter by track IDs
            time_range: (start_sec, end_sec) time range

        Returns:
            Filtered event list
        """
        filtered = self.events

        if actions:
            filtered = [e for e in filtered if e["action"] in actions]

        if track_ids:
            filtered = [e for e in filtered if e["track_id"] in track_ids]

        if time_range:
            start_sec, end_sec = time_range
            filtered = [
                e
                for e in filtered
                if start_sec <= e["time_seconds"] <= end_sec
            ]

        return filtered

    def get_summary(self) -> dict:
        """
        Get event summary statistics.

        Returns:
            Summary dict with counts and distributions
        """
        total_events = len(self.events)
        unique_tracks = len(set(e["track_id"] for e in self.events))

        return {
            "total_events": total_events,
            "unique_tracks": unique_tracks,
            "action_counts": self.event_counts.copy(),
            "action_distribution": {
                action: round(count / total_events, 3) if total_events > 0 else 0.0
                for action, count in self.event_counts.items()
            },
        }

    def save_to_json(self, output_path: Path):
        """
        Save events to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        output_data = {
            "job_id": self.job_id,
            "total_events": len(self.events),
            "summary": self.get_summary(),
            "events": self.events,
        }

        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"✓ Events saved to {output_path}")

    def _frame_to_timestamp(self, frame_id: int) -> str:
        """
        Convert frame number to ISO timestamp.

        Args:
            frame_id: Frame number

        Returns:
            ISO format timestamp string
        """
        # For now, just use current time + offset
        # In production, would use video start time
        return datetime.utcnow().isoformat() + "Z"

    def _compute_area(self, bbox: List[float]) -> int:
        """Compute bounding box area."""
        x1, y1, x2, y2 = bbox
        return int((x2 - x1) * (y2 - y1))

    def reset(self):
        """Reset logger state."""
        self.events.clear()
        self.last_action.clear()
        self.event_counts = {
            "standing": 0,
            "walking": 0,
            "running": 0,
            "loitering": 0,
            "fallen": 0,
            "fight": 0,
        }
