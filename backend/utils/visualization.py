"""
Visualization utilities for drawing annotations on video frames.
"""

import cv2
import numpy as np


# Color palette for different actions
ACTION_COLORS = {
    "standing": (100, 100, 255),  # Light red (BGR)
    "walking": (100, 255, 100),  # Light green
    "running": (255, 100, 100),  # Light blue
    "loitering": (0, 0, 255),  # Red
    "fallen": (0, 0, 200),  # Dark red (CRITICAL)
    "fight": (0, 140, 255),  # Orange (HIGH)
    "unknown": (128, 128, 128),  # Gray
}

# Track ID colors (cycle through)
TRACK_COLORS = [
    (230, 159, 0),
    (86, 180, 233),
    (0, 158, 115),
    (240, 228, 66),
    (0, 114, 178),
    (213, 94, 0),
    (204, 121, 167),
]


def draw_annotations(
    frame: np.ndarray,
    tracks: list[dict],
    show_bbox: bool = True,
    show_id: bool = True,
    show_action: bool = True,
    show_velocity: bool = False,
    thickness: int = 2,
) -> np.ndarray:
    """
    Draw annotations on a frame.

    Args:
        frame: Input frame (H, W, 3) in BGR
        tracks: List of track dicts with bbox, track_id, action, etc.
        show_bbox: Draw bounding box
        show_id: Show track ID
        show_action: Show action label
        show_velocity: Show velocity value
        thickness: Line thickness

    Returns:
        Annotated frame
    """
    annotated = frame.copy()

    for track in tracks:
        track_id = track["track_id"]
        bbox = track["bbox"]
        action = track.get("action", "unknown")
        action_conf = track.get("action_conf", 0.0)

        # Get colors
        action_color = ACTION_COLORS.get(action, ACTION_COLORS["unknown"])
        track_color = TRACK_COLORS[track_id % len(TRACK_COLORS)]

        # Extract bbox coordinates
        x1, y1, x2, y2 = [int(c) for c in bbox]

        # Draw bounding box (thicker for critical events)
        if show_bbox:
            box_thickness = thickness * 2 if action == "fallen" else thickness
            cv2.rectangle(
                annotated, (x1, y1), (x2, y2), action_color, box_thickness
            )

        # Add warning icon for fallen persons
        if action == "fallen":
            warning_text = "⚠ FALL DETECTED"
            _draw_label(
                annotated,
                warning_text,
                (x1, y1 - 35),
                (0, 0, 200),  # Dark red
                font_scale=0.6,
                thickness=2
            )

        # Prepare label text
        labels = []
        if show_id:
            labels.append(f"ID:{track_id}")
        if show_action:
            labels.append(f"{action.upper() if action == 'fallen' else action} ({action_conf:.2f})")
        if show_velocity and "state" in track:
            velocity = track["state"].get_velocity()
            labels.append(f"{velocity:.1f} px/f")

        # Draw label background and text
        if labels:
            label_text = " | ".join(labels)
            _draw_label(annotated, label_text, (x1, y1 - 10), action_color)

    return annotated


def _draw_label(
    frame: np.ndarray,
    text: str,
    position: tuple,
    color: tuple,
    font_scale: float = 0.5,
    thickness: int = 1,
):
    """
    Draw text label with background.

    Args:
        frame: Frame to draw on
        text: Text to draw
        position: (x, y) position
        color: RGB color tuple
        font_scale: Font scale
        thickness: Text thickness
    """
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )

    x, y = position
    padding = 5

    # Draw background rectangle
    cv2.rectangle(
        frame,
        (x, y - text_height - padding),
        (x + text_width + padding, y + padding),
        color,
        -1,  # Filled
    )

    # Draw text
    cv2.putText(
        frame,
        text,
        (x + padding // 2, y),
        font,
        font_scale,
        (255, 255, 255),  # White text
        thickness,
        cv2.LINE_AA,
    )


def draw_fps(frame: np.ndarray, fps: float) -> np.ndarray:
    """
    Draw FPS counter on frame.

    Args:
        frame: Input frame
        fps: Current FPS value

    Returns:
        Frame with FPS overlay
    """
    annotated = frame.copy()

    # Draw FPS in top-left corner
    fps_text = f"FPS: {fps:.1f}"
    _draw_label(
        annotated,
        fps_text,
        (10, 30),
        (0, 0, 0),  # Black background
        font_scale=0.7,
        thickness=2,
    )

    return annotated


def draw_track_history(
    frame: np.ndarray,
    track: dict,
    max_points: int = 30,
    thickness: int = 2,
) -> np.ndarray:
    """
    Draw track trajectory history.

    Args:
        frame: Input frame
        track: Track dict with state
        max_points: Maximum points to draw
        thickness: Line thickness

    Returns:
        Frame with trajectory
    """
    if "state" not in track:
        return frame

    annotated = frame.copy()
    state = track["state"]

    # Get recent centroids from history
    history = list(state.history)[-max_points:]

    if len(history) < 2:
        return annotated

    # Extract centroids
    points = [h["centroid"] for h in history]

    # Draw lines between consecutive points
    track_color = TRACK_COLORS[track["track_id"] % len(TRACK_COLORS)]

    for i in range(1, len(points)):
        pt1 = (int(points[i - 1][0]), int(points[i - 1][1]))
        pt2 = (int(points[i][0]), int(points[i][1]))

        # Fade older points
        alpha = i / len(points)
        color = tuple(int(c * alpha) for c in track_color)

        cv2.line(annotated, pt1, pt2, color, thickness)

    return annotated


def create_legend(
    frame_shape: tuple, actions: list[str] = None
) -> np.ndarray:
    """
    Create a legend showing action colors.

    Args:
        frame_shape: (height, width) of frame
        actions: List of actions to include in legend

    Returns:
        Legend image
    """
    if actions is None:
        actions = ["standing", "walking", "running", "loitering"]

    height = 30 + len(actions) * 30
    width = 200
    legend = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Draw title
    cv2.putText(
        legend,
        "Actions:",
        (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 0),
        1,
    )

    # Draw each action
    for i, action in enumerate(actions):
        y = 40 + i * 30
        color = ACTION_COLORS.get(action, ACTION_COLORS["unknown"])

        # Draw color box
        cv2.rectangle(legend, (10, y - 15), (30, y + 5), color, -1)

        # Draw text
        cv2.putText(
            legend,
            action.capitalize(),
            (40, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 0, 0),
            1,
        )

    return legend
