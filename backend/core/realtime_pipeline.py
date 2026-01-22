"""
Real-time processing pipeline for live surveillance.

Orchestrates:
- Person detection (YOLOv8)
- Face recognition
- Multi-object tracking
- Gesture detection
- Audio name extraction
- Event logging
- Video clip recording
"""

import numpy as np
import cv2
import asyncio
import logging
from typing import Dict, Optional, List, Tuple
from collections import deque
import time
import json

from backend.core.detector import YOLOv8Detector
from backend.core.tracker import ByteTracker as Tracker
from backend.core.face_recognition import FaceRecognitionEngine, load_all_person_embeddings, create_person_with_face
from backend.core.gesture_learner import GestureLearner
from backend.core.audio_processor import AudioProcessor
from backend.core.clip_recorder import EventClipRecorder
from backend.storage.crud import (
    create_person_event,
    update_person_last_seen,
    update_person_name,
    create_event_clip,
    get_all_gesture_templates
)

logger = logging.getLogger(__name__)


class RealtimePipeline:
    """
    Real-time surveillance processing pipeline.

    Integrates all components for live person tracking, face recognition,
    gesture detection, and event logging.
    """

    def __init__(self, db_session):
        """
        Initialize real-time pipeline.

        Args:
            db_session: Async database session
        """
        self.db = db_session

        # Initialize components
        logger.info("Initializing pipeline components...")

        self.detector = YOLOv8Detector()
        self.tracker = Tracker()
        self.face_engine = FaceRecognitionEngine(similarity_threshold=0.6)
        self.gesture_learner = GestureLearner(sequence_length=30)
        self.audio_processor = AudioProcessor(whisper_model="base")
        self.clip_recorder = EventClipRecorder(output_dir="data/clips")

        # Load known faces from database
        self.known_faces: Dict[str, np.ndarray] = {}

        # Load gesture templates from database
        self.gesture_templates_loaded = False

        # Active tracks state
        # {track_id: {'person_id': str, 'first_seen': float, 'last_action': str}}
        self.active_tracks: Dict[int, Dict] = {}

        # Pose buffers for gesture detection
        # {track_id: deque of pose features}
        self.pose_buffers: Dict[int, deque] = {}

        # Event deduplication (prevent spam)
        # {(person_id, event_type): last_logged_time}
        self.last_event_times: Dict[Tuple[str, str], float] = {}
        self.event_dedup_window = 5.0  # seconds

        logger.info("Pipeline initialized")

    async def load_known_faces(self):
        """Load all known person face embeddings from database."""
        self.known_faces = await load_all_person_embeddings(self.db)
        logger.info(f"Loaded {len(self.known_faces)} known faces")

    async def load_gesture_templates(self):
        """Load all gesture templates from database."""
        templates = await get_all_gesture_templates(self.db)

        template_list = []
        for template in templates:
            template_list.append({
                'id': template.id,
                'label': template.label,
                'pose_sequence': template.pose_sequence
            })

        self.gesture_learner.load_templates_from_db(template_list)
        self.gesture_templates_loaded = True
        logger.info(f"Loaded {len(templates)} gesture templates")

    async def process_frame(
        self,
        camera_id: int,
        frame: np.ndarray,
        frame_idx: int
    ) -> Dict:
        """
        Process single frame from camera.

        Args:
            camera_id: Camera source ID
            frame: Video frame (H, W, 3)
            frame_idx: Frame index

        Returns:
            Processing results dictionary
        """
        results = {
            'camera_id': camera_id,
            'frame_idx': frame_idx,
            'timestamp': time.time(),
            'detections': [],
            'events': []
        }

        try:
            # 1. Add frame to clip recorder buffer
            self.clip_recorder.add_frame(frame)

            # 2. Detect people
            detections = self.detector.detect(frame)

            if len(detections) == 0:
                return results

            # 3. Track people across frames
            tracks = self.tracker.update(detections, frame_idx)

            # 4. Process each tracked person
            for track in tracks:
                track_id = track.track_id
                bbox = track.bbox  # [x1, y1, x2, y2]

                # Initialize track if new
                if track_id not in self.active_tracks:
                    await self._handle_new_track(camera_id, frame, track_id, bbox, frame_idx)

                # Update existing track
                person_id = self.active_tracks[track_id]['person_id']

                # 4a. Gesture detection
                await self._detect_gesture(camera_id, frame, track_id, person_id, bbox, frame_idx)

                # 4b. Update last seen
                await update_person_last_seen(self.db, person_id)

                # Add to results
                results['detections'].append({
                    'track_id': track_id,
                    'person_id': person_id,
                    'bbox': bbox,
                    'confidence': track.confidence if hasattr(track, 'confidence') else 0.0
                })

            # 5. Process audio for name extraction (periodic)
            if frame_idx % 90 == 0:  # Every 3 seconds @ 30 FPS
                await self._process_audio_names()

            return results

        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return results

    async def _handle_new_track(
        self,
        camera_id: int,
        frame: np.ndarray,
        track_id: int,
        bbox: List[int],
        frame_idx: int
    ):
        """
        Handle new person track.

        Args:
            camera_id: Camera ID
            frame: Video frame
            track_id: Track ID
            bbox: Bounding box
            frame_idx: Frame index
        """
        # Extract face embedding
        face_embedding = self.face_engine.extract_face_embedding(frame, tuple(bbox))

        person_id = None

        if face_embedding is not None:
            # Try to match with known faces
            person_id = self.face_engine.find_matching_identity(face_embedding, self.known_faces)

            if person_id is None:
                # New person - create in database
                person_id = await create_person_with_face(
                    self.db,
                    face_embedding,
                    auto_id=True
                )

                # Add to known faces cache
                self.known_faces[person_id] = face_embedding

                logger.info(f"New person detected: {person_id}")

                # Record clip for new person
                clip_path = self.clip_recorder.record_event_clip(
                    person_id=person_id,
                    event_type='person_appeared',
                    camera_id=camera_id
                )

                if clip_path:
                    # Save clip to database
                    import os
                    file_size = os.path.getsize(clip_path)
                    duration = len(self.clip_recorder.frame_buffer) / self.clip_recorder.fps

                    await create_event_clip(
                        self.db,
                        person_id=person_id,
                        camera_id=camera_id,
                        event_type='person_appeared',
                        clip_path=clip_path,
                        duration_seconds=duration,
                        file_size_bytes=file_size
                    )

                # Log event
                await self._log_event(
                    camera_id=camera_id,
                    person_id=person_id,
                    event_type='person_appeared',
                    action='appeared',
                    confidence=1.0,
                    frame_number=frame_idx,
                    bbox=bbox
                )
            else:
                logger.info(f"Recognized person: {person_id}")
        else:
            # Could not extract face - use generic ID
            import hashlib
            generic_id = f"Track_{hashlib.md5(str(track_id).encode()).hexdigest()[:8].upper()}"
            person_id = generic_id

        # Store track info
        self.active_tracks[track_id] = {
            'person_id': person_id,
            'first_seen': time.time(),
            'last_action': 'appeared'
        }

        # Initialize pose buffer
        self.pose_buffers[track_id] = deque(maxlen=30)

    async def _detect_gesture(
        self,
        camera_id: int,
        frame: np.ndarray,
        track_id: int,
        person_id: str,
        bbox: List[int],
        frame_idx: int
    ):
        """
        Detect gestures for tracked person.

        Args:
            camera_id: Camera ID
            frame: Video frame
            track_id: Track ID
            person_id: Person ID
            bbox: Bounding box
            frame_idx: Frame index
        """
        # Extract pose features
        pose_features = self.gesture_learner.extract_pose_features(frame, tuple(bbox))

        if pose_features is not None:
            # Add to pose buffer
            self.pose_buffers[track_id].append(pose_features)

            # Try to match gesture
            if len(self.pose_buffers[track_id]) >= 30 and self.gesture_templates_loaded:
                gesture_result = self.gesture_learner.continuous_gesture_detection(
                    self.pose_buffers[track_id],
                    confidence_threshold=0.7
                )

                if gesture_result:
                    gesture_label, confidence = gesture_result

                    # Log gesture event
                    await self._log_event(
                        camera_id=camera_id,
                        person_id=person_id,
                        event_type='gesture_detected',
                        action=gesture_label,
                        confidence=confidence,
                        frame_number=frame_idx,
                        bbox=bbox
                    )

                    # Record clip for gesture
                    clip_path = self.clip_recorder.record_event_clip(
                        person_id=person_id,
                        event_type='gesture_detected',
                        camera_id=camera_id
                    )

                    if clip_path:
                        import os
                        file_size = os.path.getsize(clip_path)
                        duration = len(self.clip_recorder.frame_buffer) / self.clip_recorder.fps

                        await create_event_clip(
                            self.db,
                            person_id=person_id,
                            camera_id=camera_id,
                            event_type='gesture_detected',
                            clip_path=clip_path,
                            duration_seconds=duration,
                            file_size_bytes=file_size
                        )

    async def _process_audio_names(self):
        """Process audio buffer for name extraction."""
        if not self.audio_processor.recording:
            return

        # Transcribe recent audio
        transcript = self.audio_processor.transcribe_audio_buffer()

        if not transcript:
            return

        # Extract name
        name = self.audio_processor.extract_person_name(transcript)

        if name:
            logger.info(f"Name detected from audio: '{name}'")

            # Try to associate with most recent active track
            if self.active_tracks:
                # Get most recently added track
                recent_track_id = max(self.active_tracks.keys())
                person_id = self.active_tracks[recent_track_id]['person_id']

                # Update person name in database
                await update_person_name(
                    self.db,
                    person_id=person_id,
                    name=name,
                    name_source='audio'
                )

                logger.info(f"Associated name '{name}' with person {person_id}")

    async def _log_event(
        self,
        camera_id: int,
        person_id: str,
        event_type: str,
        action: str,
        confidence: float,
        frame_number: int,
        bbox: List[int]
    ):
        """
        Log event to database with deduplication.

        Args:
            camera_id: Camera ID
            person_id: Person ID
            event_type: Event type
            action: Action label
            confidence: Confidence score
            frame_number: Frame index
            bbox: Bounding box
        """
        # Check deduplication
        event_key = (person_id, event_type)
        current_time = time.time()

        if event_key in self.last_event_times:
            last_time = self.last_event_times[event_key]
            if current_time - last_time < self.event_dedup_window:
                return  # Skip duplicate event

        # Log event
        await create_person_event(
            self.db,
            person_id=person_id,
            camera_id=camera_id,
            event_type=event_type,
            action=action,
            confidence=confidence,
            frame_number=frame_number,
            bbox=json.dumps(bbox),
            event_metadata=json.dumps({'timestamp': current_time})
        )

        # Update deduplication tracker
        self.last_event_times[event_key] = current_time

    def get_active_tracks_summary(self) -> Dict:
        """Get summary of currently active tracks."""
        return {
            'total_active_tracks': len(self.active_tracks),
            'tracks': [
                {
                    'track_id': tid,
                    'person_id': data['person_id'],
                    'duration_seconds': time.time() - data['first_seen']
                }
                for tid, data in self.active_tracks.items()
            ]
        }

    def cleanup_inactive_tracks(self, timeout_seconds: float = 5.0):
        """
        Remove tracks that haven't been updated recently.

        Args:
            timeout_seconds: Timeout threshold
        """
        current_time = time.time()
        inactive_tracks = [
            tid for tid, data in self.active_tracks.items()
            if current_time - data['first_seen'] > timeout_seconds
        ]

        for track_id in inactive_tracks:
            del self.active_tracks[track_id]
            if track_id in self.pose_buffers:
                del self.pose_buffers[track_id]

        if inactive_tracks:
            logger.info(f"Cleaned up {len(inactive_tracks)} inactive tracks")
