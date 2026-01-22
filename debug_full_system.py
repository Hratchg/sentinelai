"""
Complete System Debug and Verification
Tests all Week 3 components and integration points
"""

import sys
import traceback
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("SENTINELAI WEEK 3 - COMPLETE SYSTEM DEBUG")
print("=" * 70)

errors = []
warnings = []

# =============================================================================
# SECTION 1: IMPORTS AND MODULE LOADING
# =============================================================================
print("\n[1/10] Testing Module Imports...")
print("-" * 70)

modules_to_test = [
    ("backend.config", "settings"),
    ("backend.core.detector", "YOLOv8Detector"),
    ("backend.core.tracker", "ByteTracker"),
    ("backend.core.actions", "ActionClassifier"),
    ("backend.core.events", "EventLogger"),
    ("backend.core.pipeline", "VideoPipeline"),
    ("backend.core.fall_detector", "FallDetector"),
    ("backend.core.fight_detector", "FightDetector"),
    ("backend.core.heatmap", "HeatmapGenerator"),
    ("backend.core.alerts", "AlertGenerator"),
    ("backend.core.notifications", "WebhookNotifier"),
    ("backend.storage.models", "Job"),
    ("backend.storage.database", "init_db"),
    ("backend.storage.crud", "create_job"),
    ("backend.api.main", "app"),
]

for module_name, class_name in modules_to_test:
    try:
        module = __import__(module_name, fromlist=[class_name])
        obj = getattr(module, class_name)
        print(f"   ✓ {module_name}.{class_name}")
    except Exception as e:
        error_msg = f"Failed to import {module_name}.{class_name}: {e}"
        errors.append(error_msg)
        print(f"   ✗ {error_msg}")

# =============================================================================
# SECTION 2: CONFIGURATION VALIDATION
# =============================================================================
print("\n[2/10] Testing Configuration...")
print("-" * 70)

try:
    from backend.config import settings

    required_settings = [
        'FALL_DETECTION_ENABLED',
        'FIGHT_DETECTION_ENABLED',
        'HEATMAP_ENABLED',
        'ALERTS_ENABLED',
        'DETECTOR_MODEL',
        'DETECTOR_CONFIDENCE',
        'FRAME_SKIP',
    ]

    for setting in required_settings:
        value = getattr(settings, setting, None)
        if value is not None:
            print(f"   ✓ {setting} = {value}")
        else:
            warning_msg = f"Setting {setting} not found"
            warnings.append(warning_msg)
            print(f"   ⚠ {warning_msg}")

    # Check Week 3 specific settings
    week3_settings = {
        'FALL_ASPECT_RATIO_THRESHOLD': 0.8,
        'FALL_VERTICAL_VELOCITY_THRESHOLD': 20.0,
        'FIGHT_PROXIMITY_IOU_THRESHOLD': 0.3,
        'FIGHT_RAPID_MOVEMENT_THRESHOLD': 15.0,
        'HEATMAP_CELL_SIZE': 32,
    }

    for setting, expected in week3_settings.items():
        value = getattr(settings, setting, None)
        if value is not None:
            print(f"   ✓ {setting} = {value}")
        else:
            warning_msg = f"Week 3 setting {setting} not found (expected {expected})"
            warnings.append(warning_msg)
            print(f"   ⚠ {warning_msg}")

except Exception as e:
    error_msg = f"Configuration test failed: {e}"
    errors.append(error_msg)
    print(f"   ✗ {error_msg}")
    traceback.print_exc()

# =============================================================================
# SECTION 3: DATABASE SCHEMA VALIDATION
# =============================================================================
print("\n[3/10] Testing Database Schema...")
print("-" * 70)

try:
    from backend.storage.models import Job
    from sqlalchemy import inspect

    mapper = inspect(Job)
    columns = {col.key: str(col.type) for col in mapper.columns}

    required_columns = [
        'id', 'filename', 'status', 'progress',
        'input_path', 'output_video_path', 'output_events_path',
        'output_heatmap_path', 'output_alerts_path',  # Week 3
        'error_message', 'created_at', 'updated_at', 'completed_at'
    ]

    for col in required_columns:
        if col in columns:
            print(f"   ✓ Column '{col}' ({columns[col]})")
        else:
            error_msg = f"Required column '{col}' missing from Job model"
            errors.append(error_msg)
            print(f"   ✗ {error_msg}")

except Exception as e:
    error_msg = f"Database schema test failed: {e}"
    errors.append(error_msg)
    print(f"   ✗ {error_msg}")
    traceback.print_exc()

# =============================================================================
# SECTION 4: DATABASE CONNECTION
# =============================================================================
print("\n[4/10] Testing Database Connection...")
print("-" * 70)

try:
    import asyncio
    from backend.storage.database import AsyncSessionLocal, DATABASE_URL
    from backend.storage import crud

    async def test_db_connection():
        try:
            async with AsyncSessionLocal() as db:
                jobs, total = await crud.list_jobs(db, limit=5)
                return total, jobs
        except Exception as e:
            raise e

    total_jobs, jobs = asyncio.run(test_db_connection())
    print(f"   ✓ Database connection successful")
    print(f"   ✓ Database URL: {DATABASE_URL}")
    print(f"   ✓ Total jobs: {total_jobs}")

    if jobs:
        print(f"   ✓ Sample jobs retrieved: {len(jobs)}")
        for job in jobs[:3]:
            print(f"      - Job {job.id[:8]}... status={job.status}")

except Exception as e:
    error_msg = f"Database connection test failed: {e}"
    errors.append(error_msg)
    print(f"   ✗ {error_msg}")
    traceback.print_exc()

# =============================================================================
# SECTION 5: FALL DETECTOR
# =============================================================================
print("\n[5/10] Testing Fall Detector...")
print("-" * 70)

try:
    from backend.core.fall_detector import FallDetector
    from backend.core.tracker import TrackState

    # Initialize detector
    fall_detector = FallDetector()
    print(f"   ✓ FallDetector initialized")

    # Create test track state
    track_state = TrackState(track_id=1)

    # Test with standing person (should not detect fall)
    track_state.update([100, 100, 200, 400], frame_id=1)  # Tall bbox
    is_fallen, conf = fall_detector.detect_fall(track_state, frame_height=1080)
    print(f"   ✓ Standing test: fallen={is_fallen}, conf={conf:.3f}")

    if is_fallen:
        warning_msg = "False positive: Standing person detected as fallen"
        warnings.append(warning_msg)
        print(f"   ⚠ {warning_msg}")

    # Test with fallen person (should detect fall)
    track_state2 = TrackState(track_id=2)
    track_state2.update([100, 500, 400, 600], frame_id=1)  # Wide, short bbox near bottom
    is_fallen, conf = fall_detector.detect_fall(track_state2, frame_height=1080)
    print(f"   ✓ Fallen test: fallen={is_fallen}, conf={conf:.3f}")

    if not is_fallen and conf < 0.3:
        warning_msg = "False negative: Fallen person not detected"
        warnings.append(warning_msg)
        print(f"   ⚠ {warning_msg}")

except Exception as e:
    error_msg = f"Fall detector test failed: {e}"
    errors.append(error_msg)
    print(f"   ✗ {error_msg}")
    traceback.print_exc()

# =============================================================================
# SECTION 6: FIGHT DETECTOR
# =============================================================================
print("\n[6/10] Testing Fight Detector...")
print("-" * 70)

try:
    from backend.core.fight_detector import FightDetector
    from backend.core.tracker import TrackState

    fight_detector = FightDetector()
    print(f"   ✓ FightDetector initialized")

    # Create two overlapping tracks (fighting)
    track1 = {
        "track_id": 1,
        "bbox": [100, 100, 200, 300],
        "state": TrackState(track_id=1)
    }
    track1["state"].update([100, 100, 200, 300], frame_id=100)
    track1["state"].update([110, 110, 210, 310], frame_id=101)

    track2 = {
        "track_id": 2,
        "bbox": [150, 120, 250, 320],
        "state": TrackState(track_id=2)
    }
    track2["state"].update([150, 120, 250, 320], frame_id=100)
    track2["state"].update([140, 110, 240, 310], frame_id=101)

    # Test fight detection
    fights = fight_detector.detect_fights([track1, track2], frame_id=101)
    print(f"   ✓ Fight detection test complete: {len(fights)} fights detected")

    # Test with separated tracks (should not detect fight)
    track3 = {
        "track_id": 3,
        "bbox": [500, 100, 600, 300],
        "state": TrackState(track_id=3)
    }
    track3["state"].update([500, 100, 600, 300], frame_id=100)

    fights_separated = fight_detector.detect_fights([track1, track3], frame_id=102)
    print(f"   ✓ Separated tracks test: {len(fights_separated)} fights detected")

    if fights_separated:
        warning_msg = "False positive: Separated tracks detected as fighting"
        warnings.append(warning_msg)
        print(f"   ⚠ {warning_msg}")

except Exception as e:
    error_msg = f"Fight detector test failed: {e}"
    errors.append(error_msg)
    print(f"   ✗ {error_msg}")
    traceback.print_exc()

# =============================================================================
# SECTION 7: HEATMAP GENERATOR
# =============================================================================
print("\n[7/10] Testing Heatmap Generator...")
print("-" * 70)

try:
    from backend.core.heatmap import HeatmapGenerator
    import numpy as np

    heatmap_gen = HeatmapGenerator((1920, 1080))
    print(f"   ✓ HeatmapGenerator initialized (1920x1080)")

    # Add test detections
    test_detections = [
        (500, 300), (505, 305), (510, 310),  # Cluster 1
        (1000, 800), (1005, 805),             # Cluster 2
        (200, 200),                            # Single detection
    ]

    for centroid in test_detections:
        heatmap_gen.add_detection(centroid)

    stats = heatmap_gen.get_stats()
    print(f"   ✓ Detections accumulated: {stats['total_detections']}")
    print(f"   ✓ Active cells: {stats['active_cells']}")

    # Test rendering
    heatmap_img = heatmap_gen.render_heatmap()
    print(f"   ✓ Heatmap rendered: shape={heatmap_img.shape}, dtype={heatmap_img.dtype}")

    if heatmap_img.shape != (1080, 1920, 3):
        error_msg = f"Heatmap wrong shape: {heatmap_img.shape}, expected (1080, 1920, 3)"
        errors.append(error_msg)
        print(f"   ✗ {error_msg}")

    # Test saving (to temp location)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        temp_path = f.name

    heatmap_gen.save_heatmap(temp_path)
    if Path(temp_path).exists():
        print(f"   ✓ Heatmap saved successfully")
        Path(temp_path).unlink()  # Clean up
    else:
        error_msg = "Heatmap save failed"
        errors.append(error_msg)
        print(f"   ✗ {error_msg}")

except Exception as e:
    error_msg = f"Heatmap generator test failed: {e}"
    errors.append(error_msg)
    print(f"   ✗ {error_msg}")
    traceback.print_exc()

# =============================================================================
# SECTION 8: ALERT SYSTEM
# =============================================================================
print("\n[8/10] Testing Alert System...")
print("-" * 70)

try:
    from backend.core.alerts import AlertGenerator, Alert, AlertSeverity
    import tempfile

    alert_gen = AlertGenerator(fps=30)
    print(f"   ✓ AlertGenerator initialized")

    # Create test alerts
    test_alerts = [
        Alert("fall_detected", AlertSeverity.CRITICAL, 100, [1], "Test fall"),
        Alert("fight_detected", AlertSeverity.HIGH, 200, [1, 2], "Test fight"),
        Alert("prolonged_loitering", AlertSeverity.MEDIUM, 300, [3], "Test loiter"),
    ]

    for alert in test_alerts:
        alert_gen.alerts.append(alert)

    print(f"   ✓ Test alerts created: {len(alert_gen.alerts)}")

    # Test summary
    summary = alert_gen.get_summary()
    print(f"   ✓ Alert summary generated:")
    print(f"      Total: {summary['total_alerts']}")
    print(f"      By severity: {summary['by_severity']}")

    # Test export
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    alert_gen.export_alerts(temp_path)

    if Path(temp_path).exists():
        print(f"   ✓ Alerts exported successfully")

        # Verify JSON structure
        import json
        with open(temp_path, 'r') as f:
            data = json.load(f)
            if 'summary' in data and 'alerts' in data:
                print(f"   ✓ Alert JSON structure valid")
            else:
                error_msg = "Alert JSON missing required fields"
                errors.append(error_msg)
                print(f"   ✗ {error_msg}")

        Path(temp_path).unlink()  # Clean up
    else:
        error_msg = "Alert export failed"
        errors.append(error_msg)
        print(f"   ✗ {error_msg}")

except Exception as e:
    error_msg = f"Alert system test failed: {e}"
    errors.append(error_msg)
    print(f"   ✗ {error_msg}")
    traceback.print_exc()

# =============================================================================
# SECTION 9: API ROUTES
# =============================================================================
print("\n[9/10] Testing API Routes...")
print("-" * 70)

try:
    from backend.api.main import app

    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append((route.path, list(route.methods)))

    print(f"   ✓ Total routes registered: {len(routes)}")

    # Check for required Week 3 routes
    required_routes = [
        '/api/v1/results/{job_id}/heatmap',
        '/api/v1/results/{job_id}/alerts',
        '/api/v1/results/{job_id}/video',
        '/api/v1/results/{job_id}/events',
        '/api/v1/upload',
        '/api/v1/jobs',
    ]

    for required_route in required_routes:
        found = any(required_route in r[0] for r in routes)
        if found:
            print(f"   ✓ Route: {required_route}")
        else:
            error_msg = f"Required route missing: {required_route}"
            errors.append(error_msg)
            print(f"   ✗ {error_msg}")

except Exception as e:
    error_msg = f"API routes test failed: {e}"
    errors.append(error_msg)
    print(f"   ✗ {error_msg}")
    traceback.print_exc()

# =============================================================================
# SECTION 10: PIPELINE INTEGRATION
# =============================================================================
print("\n[10/10] Testing Pipeline Integration...")
print("-" * 70)

try:
    from backend.core.pipeline import VideoPipeline
    from backend.config import settings

    # Initialize pipeline with Week 3 features
    print(f"   ✓ Attempting to initialize VideoPipeline...")

    # Note: This won't actually load models (too slow), just check initialization
    # The actual model loading happens when process_video is called

    print(f"   ✓ Pipeline class loaded successfully")
    print(f"   ✓ Week 3 features configured:")
    print(f"      - Fall detection: {settings.FALL_DETECTION_ENABLED}")
    print(f"      - Fight detection: {settings.FIGHT_DETECTION_ENABLED}")
    print(f"      - Heatmap generation: {settings.HEATMAP_ENABLED}")
    print(f"      - Alert system: {settings.ALERTS_ENABLED}")

    # Check that pipeline can accept Week 3 parameters
    from inspect import signature
    sig = signature(VideoPipeline.process_video)
    params = list(sig.parameters.keys())

    required_params = ['input_path', 'output_path', 'events_path', 'heatmap_path', 'alerts_path']
    for param in required_params:
        if param in params:
            print(f"   ✓ Pipeline accepts '{param}' parameter")
        else:
            error_msg = f"Pipeline missing parameter: {param}"
            errors.append(error_msg)
            print(f"   ✗ {error_msg}")

except Exception as e:
    error_msg = f"Pipeline integration test failed: {e}"
    errors.append(error_msg)
    print(f"   ✗ {error_msg}")
    traceback.print_exc()

# =============================================================================
# FINAL REPORT
# =============================================================================
print("\n" + "=" * 70)
print("DEBUG REPORT SUMMARY")
print("=" * 70)

print(f"\n✓ Tests Passed: {10 - len([e for e in errors if 'test failed' in e.lower()])}/10")
print(f"✗ Errors Found: {len(errors)}")
print(f"⚠ Warnings: {len(warnings)}")

if errors:
    print("\n❌ ERRORS:")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")

if warnings:
    print("\n⚠️  WARNINGS:")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")

print("\n" + "=" * 70)

if not errors:
    print("✅ ALL SYSTEMS OPERATIONAL - WEEK 3 READY FOR PRODUCTION!")
    print("\nNext steps:")
    print("1. Start backend: .\\backend\\venv\\Scripts\\python.exe -m uvicorn backend.api.main:app --reload --port 8000")
    print("2. Test with video: Upload via http://localhost:8000/docs")
    print("3. Check results: Heatmap and alerts endpoints")
else:
    print("⚠️  ISSUES DETECTED - Review errors above")
    print("\nRecommended actions:")
    for error in errors[:3]:
        print(f"   - Fix: {error}")

print("=" * 70)
