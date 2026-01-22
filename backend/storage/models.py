"""
SQLAlchemy Database Models
Multi-tenant architecture with user authentication
"""

from sqlalchemy import Column, String, Float, Text, DateTime, Index, Integer, Boolean, LargeBinary, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.storage.database import Base
import uuid


def generate_uuid():
    """Generate a unique UUID string"""
    return str(uuid.uuid4())


class User(Base):
    """
    User model for authentication and multi-tenancy.

    Each user has their own isolated SentinelAI instance with:
    - Separate person database (faces/IDs)
    - Private events and video clips
    - Individual system preferences

    Attributes:
        id: Unique user identifier (UUID)
        username: Unique username for login
        email: User email address
        hashed_password: Bcrypt hashed password
        full_name: User's full name (optional)
        is_active: Account active status
        is_superuser: Admin privileges
        created_at: Account creation timestamp
        last_login_at: Last login timestamp
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships (one-to-many)
    persons = relationship("Person", back_populates="user", cascade="all, delete-orphan")
    events = relationship("PersonEvent", back_populates="user", cascade="all, delete-orphan")
    event_clips = relationship("EventClip", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

    def to_dict(self):
        """Convert model to dictionary (excluding password)"""
        return {
            "user_id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login_at": self.last_login_at
        }


class Job(Base):
    """
    Job model for tracking video processing tasks.

    User-scoped: Each job belongs to a specific user.

    Attributes:
        id: Unique job identifier (UUID)
        user_id: Foreign key to User (owner)
        filename: Original video filename
        status: Current job status (queued, processing, completed, failed)
        progress: Processing progress percentage (0-100)
        input_path: Path to uploaded video file
        output_video_path: Path to processed video with annotations
        output_events_path: Path to events JSON file
        output_heatmap_path: Path to heatmap PNG file (Week 3)
        output_alerts_path: Path to alerts JSON file (Week 3)
        error_message: Error message if job failed
        created_at: Job creation timestamp
        updated_at: Last update timestamp
        completed_at: Job completion timestamp
    """
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="queued", index=True)
    progress = Column(Float, nullable=False, default=0.0)

    # File paths
    input_path = Column(String(512), nullable=True)
    output_video_path = Column(String(512), nullable=True)
    output_events_path = Column(String(512), nullable=True)
    output_heatmap_path = Column(String(512), nullable=True)  # Week 3
    output_alerts_path = Column(String(512), nullable=True)  # Week 3

    # Error handling
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    user = relationship("User", back_populates="jobs")

    def __repr__(self):
        return f"<Job(id={self.id}, user={self.user_id}, filename={self.filename}, status={self.status}, progress={self.progress}%)>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "job_id": self.id,
            "filename": self.filename,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message
        }


# Create indexes for better query performance
Index("idx_job_status", Job.status)
Index("idx_job_created_at", Job.created_at)


class Person(Base):
    """
    Person model for face recognition and identity tracking.

    User-scoped: Each person record belongs to a specific user.
    Person IDs and faces are isolated between users.

    Attributes:
        id: Unique person identifier (UUID)
        user_id: Foreign key to User (owner)
        name: Extracted name from audio (if available)
        display_name: User-friendly name to display
        face_embedding: Binary face embedding vector (512-d for Facenet)
        first_seen_at: First appearance timestamp
        last_seen_at: Last seen timestamp
        total_appearances: Count of total detections
        archived: Whether person is archived (inactive)
        archived_at: Archive timestamp
        name_source: How name was obtained ('audio', 'manual', 'auto-generated')
    """
    __tablename__ = "persons"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    face_embedding = Column(LargeBinary, nullable=True)  # Stores numpy array as bytes
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    total_appearances = Column(Integer, default=0, nullable=False)
    archived = Column(Boolean, default=False, nullable=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    name_source = Column(String(20), nullable=True)  # 'audio' | 'manual' | 'auto-generated'

    # Relationships
    user = relationship("User", back_populates="persons")
    events = relationship("PersonEvent", back_populates="person", cascade="all, delete-orphan")
    event_clips = relationship("EventClip", back_populates="person", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Person(id={self.id}, display_name={self.display_name}, appearances={self.total_appearances})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "person_id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "first_seen_at": self.first_seen_at,
            "last_seen_at": self.last_seen_at,
            "total_appearances": self.total_appearances,
            "archived": self.archived,
            "name_source": self.name_source
        }


class PersonEvent(Base):
    """
    Event log for person actions and detections.

    User-scoped: Events belong to user through person relationship.

    Attributes:
        id: Unique event identifier
        user_id: Foreign key to User (owner) - for efficient querying
        person_id: Foreign key to Person
        camera_id: Camera source ID
        event_type: Type of event (person_appeared, gesture_detected, voice_detected, etc.)
        action: Action label (walking, waving, standing, etc.)
        confidence: Detection confidence score
        frame_number: Frame index in video/stream
        bbox: Bounding box coordinates [x1, y1, x2, y2] as JSON string
        metadata: Additional event data as JSON
        created_at: Event timestamp
    """
    __tablename__ = "person_events"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    person_id = Column(String(36), ForeignKey('persons.id'), nullable=False, index=True)
    camera_id = Column(Integer, nullable=False, default=0)
    event_type = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    frame_number = Column(Integer, nullable=True)
    bbox = Column(Text, nullable=True)  # JSON: [x1, y1, x2, y2]
    event_metadata = Column(Text, nullable=True)  # JSON metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="events")
    person = relationship("Person", back_populates="events")

    def __repr__(self):
        return f"<PersonEvent(id={self.id}, person={self.person_id}, type={self.event_type}, action={self.action})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "event_id": self.id,
            "person_id": self.person_id,
            "camera_id": self.camera_id,
            "event_type": self.event_type,
            "action": self.action,
            "confidence": self.confidence,
            "frame_number": self.frame_number,
            "bbox": self.bbox,
            "metadata": self.event_metadata,
            "created_at": self.created_at
        }


class GestureTemplate(Base):
    """
    Learned gesture templates for recognition.

    GLOBAL SHARED: Gestures are shared across all users.
    When any user teaches a gesture, it benefits the entire system.
    This allows the AI to continuously learn and improve gesture recognition.

    Attributes:
        id: Unique template identifier
        label: Gesture name/label (e.g., 'wave', 'peace_sign')
        pose_sequence: Binary pose sequence data (MediaPipe landmarks)
        num_frames: Number of frames in sequence
        created_by_user_id: User ID who first created this gesture (optional)
        created_at: Template creation timestamp
        last_detected_at: Last time this gesture was detected
        detection_count: Total number of times detected across all users
        is_verified: Whether this gesture has been verified by multiple users
    """
    __tablename__ = "gesture_templates"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    label = Column(String(100), nullable=False, unique=True, index=True)
    pose_sequence = Column(LargeBinary, nullable=False)  # Stores numpy array as bytes
    num_frames = Column(Integer, nullable=False)
    created_by_user_id = Column(String(36), ForeignKey('users.id'), nullable=True)  # User who first taught it
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_detected_at = Column(DateTime(timezone=True), nullable=True)
    detection_count = Column(Integer, default=0, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)  # Multiple users confirmed

    def __repr__(self):
        return f"<GestureTemplate(id={self.id}, label={self.label}, detections={self.detection_count})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "gesture_id": self.id,
            "label": self.label,
            "num_frames": self.num_frames,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "detection_count": self.detection_count
        }


class EventClip(Base):
    """
    Video clips for important events.

    User-scoped: Each clip is private to the user who recorded it.
    Clips are stored in user-specific directories for security.

    Attributes:
        id: Unique clip identifier
        user_id: Foreign key to User (owner)
        person_id: Foreign key to Person
        camera_id: Camera source ID
        event_type: Event type (person_appeared, gesture_detected, voice_detected)
        clip_path: Path to video clip file (user-scoped path)
        duration_seconds: Clip duration in seconds
        file_size_bytes: File size in bytes
        thumbnail_path: Path to thumbnail image (optional)
        created_at: Clip creation timestamp
    """
    __tablename__ = "event_clips"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    person_id = Column(String(36), ForeignKey('persons.id'), nullable=False, index=True)
    camera_id = Column(Integer, nullable=False, default=0)
    event_type = Column(String(50), nullable=False, index=True)
    clip_path = Column(String(512), nullable=False)
    duration_seconds = Column(Float, nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    thumbnail_path = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="event_clips")
    person = relationship("Person", back_populates="event_clips")

    def __repr__(self):
        return f"<EventClip(id={self.id}, person={self.person_id}, type={self.event_type}, duration={self.duration_seconds}s)>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "clip_id": self.id,
            "person_id": self.person_id,
            "camera_id": self.camera_id,
            "event_type": self.event_type,
            "clip_path": self.clip_path,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "thumbnail_path": self.thumbnail_path,
            "created_at": self.created_at
        }


# Additional indexes for optimized querying
Index("idx_user_username", User.username)
Index("idx_user_email", User.email)
Index("idx_job_user", Job.user_id)
Index("idx_person_user", Person.user_id)
Index("idx_person_last_seen", Person.last_seen_at)
Index("idx_person_archived", Person.archived)
Index("idx_person_event_user", PersonEvent.user_id)
Index("idx_person_event_created", PersonEvent.created_at)
Index("idx_person_event_type", PersonEvent.event_type)
Index("idx_event_clip_user", EventClip.user_id)
Index("idx_event_clip_created", EventClip.created_at)
Index("idx_event_clip_type", EventClip.event_type)
