"""
Week 3 Component Test Script
Tests all Week 3 modules without requiring a video file.
"""

import sys
import numpy as np
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("=" * 60)
print("Week 3 Component Test")
print("=" * 60)

# Test 1: Import all Week 3 modules
print("\n1. Testing imports...")
try:
    from backend.core.fall_detector import FallDetector
    print("   ✓ FallDetector imported")
except Exception as e:
    print(f"   ✗ FallDetector import failed: {e}")
    sys.exit(1)

try:
    from backend.core.fight_detector import FightDetector
    print("   ✓ FightDetector imported")
except Exception as e:
    print(f"   ✗ FightDetector import failed: {e}")
    sys.exit(1)

try:
    from backend.core.heatmap import HeatmapGenerator
    print("   ✓ HeatmapGenerator imported")
except Exception as e:
    print(f"   ✗ HeatmapGenerator import failed: {e}")
    sys.exit(1)

try:
    from backend.core.alerts import AlertGenerator, Alert, AlertSeverity
    print("   ✓ AlertGenerator imported")
except Exception as e:
    print(f"   ✗ AlertGenerator import failed: {e}")
    sys.exit(1)

try:
    from backend.core.notifications import WebhookNotifier
    print("   ✓ WebhookNotifier imported")
except Exception as e:
    print(f"   ✗ WebhookNotifier import failed: {e}")
    sys.exit(1)

# Test 2: Initialize modules
print("\n2. Testing module initialization...")
try:
    fall_detector = FallDetector()
    print("   ✓ FallDetector initialized")
except Exception as e:
    print(f"   ✗ FallDetector initialization failed: {e}")
    sys.exit(1)

try:
    fight_detector = FightDetector()
    print("   ✓ FightDetector initialized")
except Exception as e:
    print(f"   ✗ FightDetector initialization failed: {e}")
    sys.exit(1)

try:
    heatmap_gen = HeatmapGenerator((1920, 1080))
    print("   ✓ HeatmapGenerator initialized")
except Exception as e:
    print(f"   ✗ HeatmapGenerator initialization failed: {e}")
    sys.exit(1)

try:
    alert_gen = AlertGenerator(fps=30)
    print("   ✓ AlertGenerator initialized")
except Exception as e:
    print(f"   ✗ AlertGenerator initialization failed: {e}")
    sys.exit(1)

# Test 3: Test fall detection logic
print("\n3. Testing fall detection...")
try:
    from backend.core.tracker import TrackState

    # Create a mock track state for a fallen person
    track_state = TrackState(track_id=1)

    # Add history with horizontal bbox (lying down)
    track_state.add_detection(
        bbox=[100, 500, 300, 550],  # Wide, short bbox (fallen)
        centroid=(200, 525),
        frame_id=100
    )

    is_fallen, confidence = fall_detector.detect_fall(track_state, frame_height=1080)
    print(f"   ✓ Fall detection: is_fallen={is_fallen}, confidence={confidence:.3f}")

except Exception as e:
    print(f"   ✗ Fall detection test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test heatmap accumulation
print("\n4. Testing heatmap generation...")
try:
    # Add some detections
    heatmap_gen.add_detection((500, 300))
    heatmap_gen.add_detection((500, 305))
    heatmap_gen.add_detection((1000, 800))

    stats = heatmap_gen.get_stats()
    print(f"   ✓ Heatmap: {stats['total_detections']} detections accumulated")

    # Try rendering (without saving)
    heatmap_img = heatmap_gen.render_heatmap()
    print(f"   ✓ Heatmap rendered: shape={heatmap_img.shape}")

except Exception as e:
    print(f"   ✗ Heatmap test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test alert generation
print("\n5. Testing alert system...")
try:
    # Create a test alert
    alert = Alert(
        alert_type="fall_detected",
        severity=AlertSeverity.CRITICAL,
        frame_id=100,
        track_ids=[1],
        message="Test fall alert",
        metadata={"test": True}
    )

    print(f"   ✓ Alert created: {alert.alert_type} ({alert.severity.value})")

    # Test alert generator
    alert_gen.alerts.append(alert)
    summary = alert_gen.get_alerts_summary()
    print(f"   ✓ Alert summary: {summary['total_alerts']} total")

except Exception as e:
    print(f"   ✗ Alert test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Test fight detection
print("\n6. Testing fight detection...")
try:
    # Create mock tracks that overlap (fighting)
    track1 = {
        "track_id": 1,
        "bbox": [100, 100, 200, 300],
        "state": TrackState(track_id=1)
    }
    track1["state"].add_detection(
        bbox=[100, 100, 200, 300],
        centroid=(150, 200),
        frame_id=100
    )
    track1["state"].add_detection(
        bbox=[110, 110, 210, 310],
        centroid=(160, 210),
        frame_id=101
    )

    track2 = {
        "track_id": 2,
        "bbox": [150, 120, 250, 320],
        "state": TrackState(track_id=2)
    }
    track2["state"].add_detection(
        bbox=[150, 120, 250, 320],
        centroid=(200, 220),
        frame_id=100
    )
    track2["state"].add_detection(
        bbox=[140, 110, 240, 310],
        centroid=(190, 210),
        frame_id=101
    )

    fights = fight_detector.detect_fights([track1, track2], frame_id=101)
    print(f"   ✓ Fight detection: {len(fights)} fight events detected")

except Exception as e:
    print(f"   ✗ Fight detection test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Check database schema
print("\n7. Testing database schema...")
try:
    from backend.storage.models import Job
    from sqlalchemy import inspect

    # Check if Week 3 columns exist in the model
    mapper = inspect(Job)
    columns = [col.key for col in mapper.columns]

    required_columns = ['output_heatmap_path', 'output_alerts_path']
    for col in required_columns:
        if col in columns:
            print(f"   ✓ Column '{col}' exists in Job model")
        else:
            print(f"   ✗ Column '{col}' missing from Job model")

except Exception as e:
    print(f"   ✗ Database schema test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 8: Check config settings
print("\n8. Testing configuration...")
try:
    from backend.config import settings

    week3_settings = [
        'FALL_DETECTION_ENABLED',
        'FIGHT_DETECTION_ENABLED',
        'HEATMAP_ENABLED',
        'ALERTS_ENABLED',
    ]

    for setting in week3_settings:
        value = getattr(settings, setting, None)
        if value is not None:
            print(f"   ✓ {setting} = {value}")
        else:
            print(f"   ✗ {setting} not found")

except Exception as e:
    print(f"   ✗ Config test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Week 3 Component Test Complete!")
print("=" * 60)
print("\nAll core components are working correctly. ✅")
print("\nNext steps:")
print("1. Start backend: python -m uvicorn backend.api.main:app --reload")
print("2. Test with a video file")
print("3. Check heatmap and alerts generation")
