"""
WebSocket handler for real-time camera streaming.

Broadcasts:
- Live video frames
- Person detections
- Events in real-time
"""

from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Query, HTTPException, Depends
from typing import List, Dict
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import asyncio
import logging
import base64
import cv2
import numpy as np

from backend.auth.security import decode_token
from backend.storage.database import get_db, AsyncSessionLocal
from backend.storage.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections for live streaming with multi-tenant support.

    Features:
    - User-scoped connections (multi-tenancy)
    - Per-camera subscriptions
    - Broadcast to specific users and cameras
    """

    def __init__(self):
        """Initialize connection manager."""
        # Structure: {user_id: {camera_id: [WebSocket, ...]}}
        self.connections: Dict[str, Dict[int, List[WebSocket]]] = {}

        # Reverse mapping: websocket -> (user_id, camera_id)
        self.socket_to_user: Dict[WebSocket, tuple] = {}

    async def connect(self, websocket: WebSocket, user_id: str, camera_id: int):
        """
        Accept new WebSocket connection for authenticated user.

        Args:
            websocket: WebSocket connection
            user_id: User ID (from JWT)
            camera_id: Camera to subscribe to
        """
        await websocket.accept()

        # Initialize user connections if new
        if user_id not in self.connections:
            self.connections[user_id] = {}

        if camera_id not in self.connections[user_id]:
            self.connections[user_id][camera_id] = []

        # Add connection
        self.connections[user_id][camera_id].append(websocket)
        self.socket_to_user[websocket] = (user_id, camera_id)

        logger.info(f"User {user_id} connected to camera {camera_id} (total: {self._count_connections()})")

    def disconnect(self, websocket: WebSocket):
        """
        Remove WebSocket connection.

        Args:
            websocket: WebSocket connection
        """
        if websocket not in self.socket_to_user:
            return

        user_id, camera_id = self.socket_to_user[websocket]

        # Remove from connections
        if user_id in self.connections and camera_id in self.connections[user_id]:
            if websocket in self.connections[user_id][camera_id]:
                self.connections[user_id][camera_id].remove(websocket)

            # Clean up empty structures
            if not self.connections[user_id][camera_id]:
                del self.connections[user_id][camera_id]

            if not self.connections[user_id]:
                del self.connections[user_id]

        # Remove from reverse mapping
        del self.socket_to_user[websocket]

        logger.info(f"User {user_id} disconnected from camera {camera_id} (remaining: {self._count_connections()})")

    def _count_connections(self) -> int:
        """Count total active connections."""
        count = 0
        for user_cameras in self.connections.values():
            for camera_sockets in user_cameras.values():
                count += len(camera_sockets)
        return count

    async def broadcast_to_user_camera(self, user_id: str, camera_id: int, message: dict):
        """
        Broadcast message to specific user's camera connections.

        Args:
            user_id: User ID
            camera_id: Camera ID
            message: Message dictionary
        """
        if user_id not in self.connections:
            return

        if camera_id not in self.connections[user_id]:
            return

        dead_sockets = []
        for websocket in self.connections[user_id][camera_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to socket: {e}")
                dead_sockets.append(websocket)

        # Clean up dead connections
        for socket in dead_sockets:
            self.disconnect(socket)

    async def broadcast_to_all(self, message: dict):
        """
        Broadcast message to all connections (all users, all cameras).

        Args:
            message: Message dictionary
        """
        dead_sockets = []
        for user_cameras in self.connections.values():
            for camera_sockets in user_cameras.values():
                for websocket in camera_sockets:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"Failed to send to socket: {e}")
                        dead_sockets.append(websocket)

        # Clean up dead connections
        for socket in dead_sockets:
            self.disconnect(socket)

    def get_stats(self) -> Dict:
        """Get connection statistics."""
        stats = {
            'total_connections': self._count_connections(),
            'users': {}
        }

        for user_id, cameras in self.connections.items():
            stats['users'][user_id] = {
                'cameras': {
                    camera_id: len(sockets)
                    for camera_id, sockets in cameras.items()
                }
            }

        return stats


# Global connection manager
manager = ConnectionManager()


async def get_user_from_token(token: str, db: AsyncSession) -> User:
    """
    Extract user from JWT token for WebSocket authentication.

    Args:
        token: JWT token string
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        return user

    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


async def handle_voice_command(user: User, camera_id: int, voice_text: str, websocket: WebSocket, db: AsyncSession):
    """
    Process voice command and send response.

    Args:
        user: Authenticated user
        camera_id: Camera ID
        voice_text: Voice command text
        websocket: WebSocket connection
        db: Database session
    """
    try:
        # Import query engine
        from backend.llm.query_engine import SurveillanceQueryEngine

        # Initialize engine for this user
        engine = SurveillanceQueryEngine(user_id=user.id)

        # Get answer (works in both Phase 1 stub mode and Phase 2 full mode)
        result = await engine.answer_question(db, voice_text, include_clips=False)

        await websocket.send_json({
            "type": "voice_response",
            "question": voice_text,
            "answer": result['answer'],
            "video_clips": result.get('video_clips', []),
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Voice command error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Failed to process voice command: {str(e)}"
        })


@router.websocket("/ws/camera/{camera_id}")
async def camera_feed(
    websocket: WebSocket,
    camera_id: int,
    token: str = Query(...)  # JWT token from query parameter
):
    """
    WebSocket endpoint for live camera feed with authentication.

    Connection: ws://localhost:8000/ws/camera/0?token=<JWT>

    Args:
        websocket: WebSocket connection
        camera_id: Camera device ID
        token: JWT authentication token

    Message format (sent to client):
    {
        'type': 'connected' | 'frame' | 'event' | 'voice_response' | 'pong' | 'stats',
        'camera_id': int,
        'timestamp': str,
        'data': {...}
    }

    Client commands:
    - 'ping' -> Returns pong
    - 'stats' -> Returns connection statistics
    - 'voice:<text>' -> Process voice command
    """
    user = None
    db = None

    try:
        # Create database session manually for WebSocket (Depends doesn't work reliably)
        db = AsyncSessionLocal()

        # Authenticate user
        user = await get_user_from_token(token, db)

        await manager.connect(websocket, user.id, camera_id)

        # Send initial connection confirmation
        await websocket.send_json({
            'type': 'connected',
            'camera_id': camera_id,
            'user_id': user.id,
            'username': user.username,
            'message': f'Connected to camera {camera_id}'
        })

        # Get camera manager from app state
        camera_manager = getattr(websocket.app.state, 'camera_manager', None)

        # Start frame streaming task
        async def stream_frames():
            """Background task to stream frames to client."""
            frame_interval = 1.0 / 15  # 15 FPS for streaming
            frames_sent = 0
            logger.info(f"Starting frame streaming for camera {camera_id}, camera_manager exists: {camera_manager is not None}")

            if camera_manager:
                stats = camera_manager.get_stream_stats(camera_id)
                logger.info(f"Camera {camera_id} stats: {stats}")

            while True:
                try:
                    if camera_manager:
                        frame = camera_manager.get_latest_frame(camera_id)
                        if frame is not None:
                            frame_b64 = encode_frame(frame, quality=70)
                            if frame_b64:
                                await websocket.send_json({
                                    'type': 'frame',
                                    'camera_id': camera_id,
                                    'timestamp': datetime.utcnow().isoformat(),
                                    'data': {
                                        'frame': frame_b64,
                                        'tracks': [],
                                        'events': []
                                    }
                                })
                                frames_sent += 1
                                if frames_sent % 30 == 0:  # Log every 2 seconds at 15 FPS
                                    logger.info(f"Streamed {frames_sent} frames to user {user.id}")
                        elif frames_sent == 0:
                            logger.warning(f"No frame available from camera {camera_id}")
                    else:
                        if frames_sent == 0:
                            logger.warning("camera_manager is None")
                    await asyncio.sleep(frame_interval)
                except Exception as e:
                    logger.debug(f"Frame streaming stopped: {e}")
                    break

        # Start frame streaming in background
        stream_task = asyncio.create_task(stream_frames())

        # Keep connection alive and handle incoming messages
        try:
            while True:
                # Receive messages from client with timeout
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                except asyncio.TimeoutError:
                    # Send keepalive
                    await websocket.send_json({'type': 'pong'})
                    continue

                # Handle client commands
                if data == 'ping':
                    await websocket.send_json({'type': 'pong'})

                elif data == 'stats':
                    stats = manager.get_stats()
                    await websocket.send_json({
                        'type': 'stats',
                        'data': stats
                    })

                elif data.startswith('voice:'):
                    # Voice command received
                    voice_text = data.replace('voice:', '').strip()
                    await handle_voice_command(user, camera_id, voice_text, websocket, db)

        finally:
            # Cancel frame streaming task
            stream_task.cancel()
            try:
                await stream_task
            except asyncio.CancelledError:
                pass

    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        await websocket.close(code=1008, reason=e.detail)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if user:
            logger.info(f"User {user.id} disconnected from camera {camera_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

    finally:
        # Clean up database session
        if db:
            await db.close()


def encode_frame(frame: np.ndarray, quality: int = 80) -> str:
    """
    Encode frame to base64 JPEG for transmission.

    Args:
        frame: Video frame (H, W, 3)
        quality: JPEG quality (0-100)

    Returns:
        Base64 encoded JPEG string
    """
    try:
        # Encode to JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, buffer = cv2.imencode('.jpg', frame, encode_param)

        # Convert to base64
        frame_b64 = base64.b64encode(buffer).decode('utf-8')

        return frame_b64

    except Exception as e:
        logger.error(f"Frame encoding failed: {e}")
        return ""


async def broadcast_frame(
    user_id: str,
    camera_id: int,
    frame: np.ndarray,
    tracks: List[Dict],
    events: List[Dict]
):
    """
    Broadcast frame with annotations to specific user's camera connections.

    Args:
        user_id: User ID
        camera_id: Camera ID
        frame: Video frame
        tracks: List of tracked persons
        events: List of recent events
    """
    # Encode frame
    frame_b64 = encode_frame(frame, quality=80)

    if not frame_b64:
        return

    # Build message
    message = {
        'type': 'frame',
        'camera_id': camera_id,
        'timestamp': datetime.utcnow().isoformat(),
        'data': {
            'frame': frame_b64,
            'tracks': tracks,
            'events': events
        }
    }

    # Broadcast to user's camera subscribers
    await manager.broadcast_to_user_camera(user_id, camera_id, message)


async def broadcast_event(
    user_id: str,
    camera_id: int,
    event: Dict
):
    """
    Broadcast event to specific user's camera connections.

    Args:
        user_id: User ID
        camera_id: Camera ID
        event: Event dictionary
    """
    message = {
        'type': 'event',
        'camera_id': camera_id,
        'timestamp': datetime.utcnow().isoformat(),
        'data': event
    }

    await manager.broadcast_to_user_camera(user_id, camera_id, message)
