"""
SentinelAI FastAPI Application
Main entry point for the REST API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
import time
from pathlib import Path
from typing import Optional

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Essential imports
from backend.storage.database import init_db, close_db

# Auth routes (always available)
from backend.api.routes import auth

# Camera streaming (requires only opencv)
CAMERA_AVAILABLE = False
CameraStreamManager = None
websocket = None

try:
    from backend.api import websocket
    from backend.core.camera_stream import CameraStreamManager as CSM
    CameraStreamManager = CSM
    CAMERA_AVAILABLE = True
    logger.info("Camera streaming module loaded successfully")
except ImportError as e:
    logger.warning(f"Camera streaming not available: {e}")

# Optional ML-dependent routes (may require additional dependencies like mediapipe)
ML_ROUTES_AVAILABLE = False
try:
    from backend.api.routes import upload, jobs, results, chat, gestures, admin
    ML_ROUTES_AVAILABLE = True
    logger.info("ML-dependent routes loaded successfully")
except ImportError as e:
    logger.warning(f"ML-dependent routes not available: {e}")

# Global instances for camera management
camera_manager = None  # Type: Optional[CameraStreamManager]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    global camera_manager

    # Startup
    logger.info("Starting SentinelAI API server...")
    await init_db()
    logger.info("Database initialized successfully")

    # Initialize camera streams if ML dependencies available
    if ML_ROUTES_AVAILABLE:
        try:
            # Get camera IDs from environment or use default
            camera_ids_str = os.getenv("CAMERA_IDS", "0")
            camera_ids = [int(id.strip()) for id in camera_ids_str.split(",")]

            logger.info(f"Initializing camera manager for cameras: {camera_ids}")

            # Initialize camera manager (simplified - no ML pipeline for now)
            camera_manager = CameraStreamManager(camera_ids)

            # Log camera initialization status
            for cam_id in camera_ids:
                if cam_id in camera_manager.cameras:
                    logger.info(f"Camera {cam_id} initialized successfully")
                else:
                    logger.error(f"Camera {cam_id} failed to initialize")

            camera_manager.start_all_streams()

            # Store camera manager in app state for WebSocket access
            app.state.camera_manager = camera_manager

            # Verify streams are running
            import time
            time.sleep(0.5)  # Give streams time to start
            for cam_id in camera_ids:
                stats = camera_manager.get_stream_stats(cam_id)
                logger.info(f"Camera {cam_id} stream status: running={stats['running']}, has_frame={stats['has_latest_frame']}")

            logger.info(f"Camera streams started: {camera_ids}")
        except Exception as e:
            logger.error(f"Failed to initialize camera streams: {e}", exc_info=True)
            camera_manager = None
    else:
        logger.info("Camera streams disabled (ML dependencies not available)")

    yield

    # Shutdown
    logger.info("Shutting down SentinelAI API server...")

    if camera_manager:
        camera_manager.stop_all_streams()
        logger.info("Camera streams stopped")

    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="SentinelAI API",
    description="AI-powered video surveillance system with person detection, tracking, and action recognition",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check"""
    return {
        "status": "ok",
        "service": "SentinelAI API",
        "version": "0.1.0",
        "docs": "/api/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "database": "connected"
    }


@app.get("/api/debug/cameras", tags=["Debug"])
async def debug_cameras():
    """Debug endpoint to check camera status"""
    global camera_manager

    if camera_manager is None:
        return {
            "status": "error",
            "message": "Camera manager not initialized",
            "ml_routes_available": ML_ROUTES_AVAILABLE
        }

    cameras_status = {}
    for cam_id in camera_manager.camera_ids:
        stats = camera_manager.get_stream_stats(cam_id)
        cameras_status[cam_id] = stats

    return {
        "status": "ok",
        "ml_routes_available": ML_ROUTES_AVAILABLE,
        "cameras": cameras_status
    }


# Include routers
# Authentication (public routes - always available)
app.include_router(auth.router, tags=["Authentication"])

# ML-dependent routes (optional)
if ML_ROUTES_AVAILABLE:
    # Legacy routes (Week 1-3)
    app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
    app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
    app.include_router(results.router, prefix="/api/v1", tags=["Results"])

    # Week 4: Real-time surveillance routes (protected)
    app.include_router(chat.router, tags=["Chat"])
    app.include_router(gestures.router, tags=["Gestures"])
    app.include_router(admin.router, tags=["Admin"])
    app.include_router(websocket.router, tags=["WebSocket"])
    logger.info("ML-dependent routes loaded successfully")
else:
    logger.warning("ML-dependent routes disabled - only authentication available")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
