"""
Alert Generation and Management Module.

Generates alerts for critical events (falls, fights, loitering, crowds).
"""

import json
import time
import uuid
from collections import Counter
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional

from backend.config import settings


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert:
    """
    Represents a single alert.

    Attributes:
        id: Unique alert identifier
        alert_type: Type of alert (fall_detected, fight_detected, etc.)
        severity: Alert severity level
        frame_id: Frame number where alert occurred
        track_ids: Track IDs involved in the alert
        message: Human-readable alert message
        timestamp: When alert was created
        acknowledged: Whether alert has been acknowledged
        metadata: Additional alert data
    """

    def __init__(
        self,
        alert_type: str,
        severity: AlertSeverity,
        frame_id: int,
        track_ids: List[int],
        message: str,
        metadata: dict = None,
    ):
        """
        Initialize alert.

        Args:
            alert_type: Type of alert
            severity: Alert severity level
            frame_id: Frame number
            track_ids: Involved track IDs
            message: Alert message
            metadata: Additional data
        """
        self.id = str(uuid.uuid4())
        self.alert_type = alert_type
        self.severity = severity
        self.frame_id = frame_id
        self.track_ids = track_ids
        self.message = message
        self.timestamp = datetime.now()
        self.acknowledged = False
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "severity": self.severity.value,
            "frame_id": self.frame_id,
            "track_ids": self.track_ids,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "metadata": self.metadata,
        }

    def acknowledge(self):
        """Mark alert as acknowledged."""
        self.acknowledged = True


class AlertGenerator:
    """
    Alert generator for surveillance events.

    Features:
    - Multiple alert types (fall, fight, loitering, crowd)
    - Severity-based prioritization
    - Alert deduplication (prevent spam)
    - Callback system for external notifications
    - Alert history and statistics
    """

    def __init__(
        self,
        deduplication_window: int = None,
        fps: float = 30.0,
    ):
        """
        Initialize alert generator.

        Args:
            deduplication_window: Seconds to wait before re-alerting (default from config)
            fps: Video FPS for time calculations
        """
        self.deduplication_window = (
            deduplication_window
            if deduplication_window is not None
            else settings.ALERT_DEDUPLICATION_WINDOW
        )
        self.fps = fps

        self.alerts: List[Alert] = []
        self.alert_callbacks: Dict[str, List[Callable]] = {}
        self.last_alert_time: Dict[str, float] = {}  # alert_type -> timestamp

    def register_callback(self, alert_type: str, callback: Callable):
        """
        Register a callback for an alert type.

        Args:
            alert_type: Type of alert to listen for
            callback: Function to call when alert is triggered
        """
        if alert_type not in self.alert_callbacks:
            self.alert_callbacks[alert_type] = []
        self.alert_callbacks[alert_type].append(callback)

    def check_alerts(
        self,
        frame_id: int,
        tracks: List[dict],
        events: List[dict],
        fight_events: List[dict],
    ):
        """
        Check for alert conditions and generate alerts.

        Args:
            frame_id: Current frame number
            tracks: List of track dicts
            events: List of action events
            fight_events: List of fight events
        """
        # Alert 1: Fall detection (CRITICAL)
        for event in events:
            if event.get("action") == "fallen":
                self._create_alert(
                    alert_type="fall_detected",
                    severity=AlertSeverity.CRITICAL,
                    frame_id=frame_id,
                    track_ids=[event["track_id"]],
                    message=f"Person fallen detected - Track #{event['track_id']}",
                    metadata={
                        "confidence": event.get("confidence", 0.0),
                        "bbox": event.get("bbox", []),
                    },
                )

        # Alert 2: Fight detection (HIGH)
        for fight in fight_events:
            self._create_alert(
                alert_type="fight_detected",
                severity=AlertSeverity.HIGH,
                frame_id=frame_id,
                track_ids=fight["participants"],
                message=f"Fight detected between tracks {fight['participants']}",
                metadata={
                    "confidence": fight.get("confidence", 0.0),
                    "iou": fight.get("iou", 0.0),
                    "duration_frames": fight.get("duration_frames", 0),
                },
            )

        # Alert 3: Prolonged loitering (MEDIUM)
        for track in tracks:
            state = track.get("state")
            if state and state.stationary_frames > 900:  # 30 seconds @ 30fps
                self._create_alert(
                    alert_type="prolonged_loitering",
                    severity=AlertSeverity.MEDIUM,
                    frame_id=frame_id,
                    track_ids=[track["track_id"]],
                    message=f"Prolonged loitering detected - Track #{track['track_id']} ({state.stationary_frames / self.fps:.1f}s)",
                    metadata={
                        "duration_seconds": state.stationary_frames / self.fps,
                        "bbox": track.get("bbox", []),
                    },
                )

        # Alert 4: Crowd detection (MEDIUM)
        if len(tracks) > 10:
            # Only alert once per crowd (not every frame)
            if not self._should_suppress("crowd_detected"):
                self._create_alert(
                    alert_type="crowd_detected",
                    severity=AlertSeverity.MEDIUM,
                    frame_id=frame_id,
                    track_ids=[t["track_id"] for t in tracks],
                    message=f"High crowd density detected - {len(tracks)} people in frame",
                    metadata={"crowd_size": len(tracks)},
                )

    def _create_alert(
        self,
        alert_type: str,
        severity: AlertSeverity,
        frame_id: int,
        track_ids: List[int],
        message: str,
        metadata: dict = None,
    ):
        """
        Create and dispatch an alert.

        Args:
            alert_type: Type of alert
            severity: Alert severity
            frame_id: Frame number
            track_ids: Involved track IDs
            message: Alert message
            metadata: Additional data
        """
        # Check deduplication
        if self._should_suppress(alert_type):
            return

        # Create alert
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            frame_id=frame_id,
            track_ids=track_ids,
            message=message,
            metadata=metadata,
        )

        self.alerts.append(alert)

        # Update last alert time
        self.last_alert_time[alert_type] = time.time()

        # Trigger callbacks
        if alert_type in self.alert_callbacks:
            for callback in self.alert_callbacks[alert_type]:
                try:
                    callback(alert)
                except Exception as e:
                    print(f"⚠️  Alert callback error: {e}")

        # Log alert
        severity_emoji = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.HIGH: "⚠️",
            AlertSeverity.MEDIUM: "⚡",
            AlertSeverity.LOW: "ℹ️",
        }
        emoji = severity_emoji.get(severity, "📢")
        print(f"{emoji} ALERT [{severity.value.upper()}]: {message}")

    def _should_suppress(self, alert_type: str) -> bool:
        """
        Check if alert should be suppressed due to deduplication.

        Args:
            alert_type: Type of alert

        Returns:
            True if should suppress
        """
        if alert_type not in self.last_alert_time:
            return False

        time_since_last = time.time() - self.last_alert_time[alert_type]
        return time_since_last < self.deduplication_window

    def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[str] = None,
        acknowledged: Optional[bool] = None,
    ) -> List[Alert]:
        """
        Get filtered alerts.

        Args:
            severity: Filter by severity
            alert_type: Filter by type
            acknowledged: Filter by acknowledgment status

        Returns:
            Filtered alert list
        """
        filtered = self.alerts

        if severity:
            filtered = [a for a in filtered if a.severity == severity]

        if alert_type:
            filtered = [a for a in filtered if a.alert_type == alert_type]

        if acknowledged is not None:
            filtered = [a for a in filtered if a.acknowledged == acknowledged]

        return filtered

    def get_summary(self) -> dict:
        """
        Get alert summary statistics.

        Returns:
            Summary dict
        """
        return {
            "total_alerts": len(self.alerts),
            "by_severity": {
                "critical": len([a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]),
                "high": len([a for a in self.alerts if a.severity == AlertSeverity.HIGH]),
                "medium": len([a for a in self.alerts if a.severity == AlertSeverity.MEDIUM]),
                "low": len([a for a in self.alerts if a.severity == AlertSeverity.LOW]),
            },
            "by_type": dict(Counter([a.alert_type for a in self.alerts])),
            "unacknowledged": len([a for a in self.alerts if not a.acknowledged]),
        }

    def export_alerts(self, output_path: Path):
        """
        Export alerts to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        alert_data = {
            "summary": self.get_summary(),
            "alerts": [a.to_dict() for a in self.alerts],
        }

        with open(output_path, "w") as f:
            json.dump(alert_data, f, indent=2)

        print(f"✓ Alerts saved to {output_path}")

    def reset(self):
        """Reset alert state."""
        self.alerts.clear()
        self.last_alert_time.clear()
