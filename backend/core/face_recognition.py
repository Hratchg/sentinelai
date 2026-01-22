"""
Face Recognition Engine using DeepFace

This module handles:
- Face detection and embedding extraction
- Face matching across frames
- Identity management with persistent storage
"""

import numpy as np
import cv2
from typing import Optional, Tuple, Dict, List
from deepface import DeepFace
from pathlib import Path
import pickle
import logging

logger = logging.getLogger(__name__)


class FaceRecognitionEngine:
    """
    Face recognition engine using DeepFace with Facenet512 model.

    Features:
    - Extract 512-d face embeddings
    - Match faces using cosine similarity
    - Manage known identities
    - Auto-assign IDs to new people
    """

    def __init__(self, similarity_threshold: float = 0.6):
        """
        Initialize face recognition engine.

        Args:
            similarity_threshold: Cosine similarity threshold for face matching (0-1)
                Higher = stricter matching (fewer false positives)
                Lower = looser matching (fewer false negatives)
        """
        self.model_name = "Facenet512"  # 512-d embeddings, best accuracy
        self.similarity_threshold = similarity_threshold
        self.detector_backend = "opencv"  # Fast, good enough for real-time

        logger.info(f"Initialized FaceRecognitionEngine (model={self.model_name}, threshold={similarity_threshold})")

    def extract_face_embedding(
        self,
        frame: np.ndarray,
        bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[np.ndarray]:
        """
        Extract face embedding from frame.

        Args:
            frame: Video frame (H, W, 3)
            bbox: Optional bounding box (x1, y1, x2, y2) to crop face region

        Returns:
            512-d face embedding vector, or None if face not detected
        """
        try:
            # If bbox provided, crop to face region
            if bbox is not None:
                x1, y1, x2, y2 = bbox
                # Add padding around bbox
                h, w = frame.shape[:2]
                padding = 20
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(w, x2 + padding)
                y2 = min(h, y2 + padding)

                face_crop = frame[y1:y2, x1:x2]

                if face_crop.size == 0:
                    return None
            else:
                face_crop = frame

            # Extract embedding using DeepFace
            embedding_objs = DeepFace.represent(
                img_path=face_crop,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                enforce_detection=False  # Don't fail if face not detected
            )

            if not embedding_objs or len(embedding_objs) == 0:
                return None

            # Get first face embedding
            embedding = np.array(embedding_objs[0]["embedding"])
            return embedding

        except Exception as e:
            logger.warning(f"Face embedding extraction failed: {e}")
            return None

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two face embeddings.

        Args:
            embedding1: First face embedding (512-d)
            embedding2: Second face embedding (512-d)

        Returns:
            Similarity score (0-1), where 1 = identical faces
        """
        # Normalize embeddings
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)

        # Cosine similarity
        similarity = np.dot(embedding1, embedding2)

        # Convert to 0-1 range (cosine is -1 to 1)
        similarity = (similarity + 1) / 2

        return float(similarity)

    def find_matching_identity(
        self,
        query_embedding: np.ndarray,
        known_faces: Dict[str, np.ndarray]
    ) -> Optional[str]:
        """
        Find matching person identity from known faces.

        Args:
            query_embedding: Face embedding to match (512-d)
            known_faces: Dictionary of {person_id: face_embedding}

        Returns:
            person_id of best match, or None if no match above threshold
        """
        if not known_faces:
            return None

        best_match_id = None
        best_similarity = 0.0

        for person_id, known_embedding in known_faces.items():
            similarity = self.compute_similarity(query_embedding, known_embedding)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = person_id

        # Only return match if above threshold
        if best_similarity >= self.similarity_threshold:
            logger.info(f"Face matched to {best_match_id} (similarity: {best_similarity:.3f})")
            return best_match_id

        logger.info(f"No face match found (best similarity: {best_similarity:.3f} < threshold: {self.similarity_threshold})")
        return None

    def verify_faces(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> Tuple[bool, float]:
        """
        Verify if two face embeddings belong to same person.

        Args:
            embedding1: First face embedding
            embedding2: Second face embedding

        Returns:
            (is_match, similarity_score)
        """
        similarity = self.compute_similarity(embedding1, embedding2)
        is_match = similarity >= self.similarity_threshold

        return is_match, similarity

    def save_embedding_to_disk(self, embedding: np.ndarray, filepath: str):
        """
        Save face embedding to disk.

        Args:
            embedding: Face embedding to save
            filepath: Path to save file (.pkl)
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'wb') as f:
            pickle.dump(embedding, f)

        logger.info(f"Saved face embedding to {filepath}")

    def load_embedding_from_disk(self, filepath: str) -> Optional[np.ndarray]:
        """
        Load face embedding from disk.

        Args:
            filepath: Path to embedding file (.pkl)

        Returns:
            Face embedding, or None if file not found
        """
        try:
            with open(filepath, 'rb') as f:
                embedding = pickle.load(f)

            logger.info(f"Loaded face embedding from {filepath}")
            return embedding

        except FileNotFoundError:
            logger.warning(f"Embedding file not found: {filepath}")
            return None

    def serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """
        Serialize embedding to bytes for database storage.

        Args:
            embedding: Face embedding (512-d numpy array)

        Returns:
            Serialized bytes
        """
        return pickle.dumps(embedding)

    def deserialize_embedding(self, data: bytes) -> np.ndarray:
        """
        Deserialize embedding from database bytes.

        Args:
            data: Serialized embedding bytes

        Returns:
            Face embedding (512-d numpy array)
        """
        return pickle.loads(data)


# Utility functions for database operations

async def load_all_person_embeddings(db_session) -> Dict[str, np.ndarray]:
    """
    Load all known person face embeddings from database.

    Args:
        db_session: Database session

    Returns:
        Dictionary of {person_id: face_embedding}
    """
    from backend.storage.crud import get_all_persons

    face_engine = FaceRecognitionEngine()
    persons = await get_all_persons(db_session)

    known_faces = {}
    for person in persons:
        if person.face_embedding:
            embedding = face_engine.deserialize_embedding(person.face_embedding)
            known_faces[person.id] = embedding

    logger.info(f"Loaded {len(known_faces)} person face embeddings from database")
    return known_faces


async def create_person_with_face(
    db_session,
    face_embedding: np.ndarray,
    auto_id: bool = True,
    name: Optional[str] = None
) -> str:
    """
    Create new person in database with face embedding.

    Args:
        db_session: Database session
        face_embedding: Face embedding (512-d)
        auto_id: Whether to auto-generate person ID
        name: Optional person name

    Returns:
        person_id
    """
    from backend.storage.crud import create_person
    from backend.storage.models import generate_uuid
    import hashlib

    face_engine = FaceRecognitionEngine()

    # Generate person ID
    if auto_id:
        # Create short hash from embedding for consistent ID
        embedding_hash = hashlib.sha256(face_embedding.tobytes()).hexdigest()[:8].upper()
        person_id = f"Person_{embedding_hash}"
        display_name = f"Person {embedding_hash}"
    else:
        person_id = generate_uuid()
        display_name = name or f"Person {person_id[:8]}"

    # Serialize embedding
    embedding_bytes = face_engine.serialize_embedding(face_embedding)

    # Create person in database
    person = await create_person(
        db_session,
        person_id=person_id,
        name=name,
        display_name=display_name,
        face_embedding=embedding_bytes,
        name_source='auto-generated' if not name else 'manual'
    )

    logger.info(f"Created person {person_id} with face embedding")
    return person.id
