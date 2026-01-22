"""
Self-learning gesture recognition using MediaPipe + DTW.

Features:
- Extract pose landmarks from video frames
- Learn custom gestures from examples
- Match gestures using Dynamic Time Warping (DTW)
- Unlimited gesture vocabulary
"""

import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, Dict, List
from collections import deque
import logging
import pickle
from dtaidistance import dtw

logger = logging.getLogger(__name__)


class GestureLearner:
    """
    Self-learning gesture recognition system.

    Uses MediaPipe Pose for body landmark detection and DTW for gesture matching.

    Features:
    - Extract 33 body landmarks per frame
    - Learn gestures from recorded sequences
    - Match gestures with confidence scores
    - Persistent storage in database
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        sequence_length: int = 30
    ):
        """
        Initialize gesture learner.

        Args:
            min_detection_confidence: MediaPipe detection confidence threshold
            min_tracking_confidence: MediaPipe tracking confidence threshold
            sequence_length: Number of frames in gesture sequence
        """
        # Initialize MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # 0=lite, 1=full, 2=heavy
            enable_segmentation=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        self.sequence_length = sequence_length

        # Gesture templates: {gesture_id: {'label': str, 'sequence': np.array, 'num_frames': int}}
        self.gesture_templates: Dict[str, Dict] = {}

        logger.info(f"Initialized GestureLearner (sequence_length={sequence_length})")

    def extract_pose_features(
        self,
        frame: np.ndarray,
        bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[np.ndarray]:
        """
        Extract pose landmarks from frame.

        Args:
            frame: Video frame (H, W, 3)
            bbox: Optional bounding box to crop to person region (x1, y1, x2, y2)

        Returns:
            Pose feature vector (99-d: 33 landmarks x 3 coordinates) or None
        """
        try:
            # Crop to bounding box if provided
            if bbox is not None:
                x1, y1, x2, y2 = bbox
                h, w = frame.shape[:2]

                # Ensure bbox is within frame
                x1 = max(0, min(x1, w))
                y1 = max(0, min(y1, h))
                x2 = max(0, min(x2, w))
                y2 = max(0, min(y2, h))

                if x2 <= x1 or y2 <= y1:
                    return None

                frame_crop = frame[y1:y2, x1:x2]
            else:
                frame_crop = frame

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2RGB)

            # Process with MediaPipe
            results = self.pose.process(frame_rgb)

            if not results.pose_landmarks:
                return None

            # Extract landmarks
            landmarks = results.pose_landmarks.landmark

            # Convert to numpy array: 33 landmarks × (x, y, z) = 99 features
            pose_features = np.array([
                [lm.x, lm.y, lm.z]
                for lm in landmarks
            ]).flatten()

            return pose_features

        except Exception as e:
            logger.error(f"Pose extraction failed: {e}")
            return None

    def record_gesture_sequence(
        self,
        pose_buffer: deque
    ) -> Optional[np.ndarray]:
        """
        Create gesture sequence from pose buffer.

        Args:
            pose_buffer: Deque of recent pose features

        Returns:
            Gesture sequence array (num_frames, 99) or None
        """
        if len(pose_buffer) < self.sequence_length:
            logger.warning(f"Not enough frames in buffer ({len(pose_buffer)} < {self.sequence_length})")
            return None

        # Take last N frames
        sequence = list(pose_buffer)[-self.sequence_length:]

        # Convert to numpy array
        sequence_array = np.array(sequence)

        logger.info(f"Recorded gesture sequence: shape {sequence_array.shape}")
        return sequence_array

    def learn_gesture(
        self,
        gesture_id: str,
        label: str,
        pose_sequence: np.ndarray
    ):
        """
        Learn a new gesture from example sequence.

        Args:
            gesture_id: Unique gesture identifier
            label: Human-readable gesture name
            pose_sequence: Pose sequence array (num_frames, 99)
        """
        self.gesture_templates[gesture_id] = {
            'label': label,
            'sequence': pose_sequence,
            'num_frames': len(pose_sequence)
        }

        logger.info(f"Learned gesture '{label}' (id: {gesture_id}, frames: {len(pose_sequence)})")

    def match_gesture(
        self,
        pose_sequence: List[np.ndarray],
        confidence_threshold: float = 0.7
    ) -> Optional[Tuple[str, float]]:
        """
        Match pose sequence to learned gestures using DTW.

        Args:
            pose_sequence: List of pose feature vectors
            confidence_threshold: Minimum confidence for match (0-1)

        Returns:
            (gesture_label, confidence) or None if no match
        """
        if not self.gesture_templates:
            return None

        if len(pose_sequence) == 0:
            return None

        try:
            # Convert to numpy array
            query = np.array(pose_sequence)

            best_match = None
            best_distance = float('inf')
            best_label = None

            # Compare with all templates
            for template_id, template_data in self.gesture_templates.items():
                template_seq = template_data['sequence']
                label = template_data['label']

                # Compute DTW distance
                distance = dtw.distance(query, template_seq)

                # Normalize by sequence length
                normalized_distance = distance / max(len(query), len(template_seq))

                if normalized_distance < best_distance:
                    best_distance = normalized_distance
                    best_match = template_id
                    best_label = label

            # Convert distance to confidence (lower distance = higher confidence)
            # Use exponential decay: confidence = exp(-distance/scale)
            scale = 10.0  # Tuning parameter
            confidence = np.exp(-best_distance / scale)

            if confidence >= confidence_threshold:
                logger.info(f"Gesture matched: '{best_label}' (confidence: {confidence:.3f})")
                return (best_label, confidence)

            logger.debug(f"No gesture match (best: '{best_label}', confidence: {confidence:.3f} < {confidence_threshold})")
            return None

        except Exception as e:
            logger.error(f"Gesture matching failed: {e}")
            return None

    def continuous_gesture_detection(
        self,
        pose_buffer: deque,
        confidence_threshold: float = 0.7
    ) -> Optional[Tuple[str, float]]:
        """
        Detect gesture from continuous pose stream.

        Args:
            pose_buffer: Rolling buffer of pose features
            confidence_threshold: Minimum confidence for detection

        Returns:
            (gesture_label, confidence) or None
        """
        if len(pose_buffer) < self.sequence_length:
            return None

        # Extract recent sequence
        recent_sequence = list(pose_buffer)[-self.sequence_length:]

        # Match against templates
        return self.match_gesture(recent_sequence, confidence_threshold)

    def load_templates_from_db(self, gesture_templates: List[Dict]):
        """
        Load gesture templates from database.

        Args:
            gesture_templates: List of template dicts with 'id', 'label', 'pose_sequence'
        """
        for template in gesture_templates:
            gesture_id = template['id']
            label = template['label']
            pose_sequence_bytes = template['pose_sequence']

            # Deserialize pose sequence
            pose_sequence = pickle.loads(pose_sequence_bytes)

            self.gesture_templates[gesture_id] = {
                'label': label,
                'sequence': pose_sequence,
                'num_frames': len(pose_sequence)
            }

        logger.info(f"Loaded {len(gesture_templates)} gesture templates from database")

    def serialize_gesture_sequence(self, pose_sequence: np.ndarray) -> bytes:
        """
        Serialize gesture sequence for database storage.

        Args:
            pose_sequence: Pose sequence array

        Returns:
            Serialized bytes
        """
        return pickle.dumps(pose_sequence)

    def get_template_stats(self) -> Dict:
        """Get statistics about loaded templates."""
        return {
            'total_templates': len(self.gesture_templates),
            'templates': [
                {
                    'id': gid,
                    'label': data['label'],
                    'num_frames': data['num_frames']
                }
                for gid, data in self.gesture_templates.items()
            ]
        }

    def __del__(self):
        """Cleanup MediaPipe resources."""
        if hasattr(self, 'pose'):
            self.pose.close()


# Import cv2 here to avoid issues
import cv2
