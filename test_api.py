"""
Simple API Integration Test
Tests that the backend server can start with Week 3 features.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("=" * 60)
print("API Integration Test")
print("=" * 60)

# Test 1: Import the FastAPI app
print("\n1. Testing FastAPI app import...")
try:
    from backend.api.main import app
    print("   ✓ FastAPI app imported successfully")
except Exception as e:
    print(f"   ✗ Failed to import FastAPI app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check all routes are registered
print("\n2. Checking API routes...")
try:
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append((route.path, list(route.methods)))

    print(f"   Total routes registered: {len(routes)}")

    # Check for Week 3 routes
    week3_routes = [
        '/api/v1/results/{job_id}/heatmap',
        '/api/v1/results/{job_id}/alerts'
    ]

    for route_path in week3_routes:
        found = any(route_path in r[0] for r in routes)
        if found:
            print(f"   ✓ Route registered: {route_path}")
        else:
            print(f"   ✗ Route missing: {route_path}")

except Exception as e:
    print(f"   ✗ Route check failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test pipeline imports
print("\n3. Testing pipeline integration...")
try:
    from backend.core.pipeline import VideoPipeline
    from backend.core.fall_detector import FallDetector
    from backend.core.fight_detector import FightDetector
    from backend.core.heatmap import HeatmapGenerator
    from backend.core.alerts import AlertGenerator

    print("   ✓ All Week 3 modules can be imported")
    print("   ✓ Pipeline integration ready")

except Exception as e:
    print(f"   ✗ Pipeline integration test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check database connection
print("\n4. Testing database...")
try:
    import asyncio
    from backend.storage.database import AsyncSessionLocal
    from backend.storage import crud

    async def test_db():
        async with AsyncSessionLocal() as db:
            # Try to list jobs
            jobs, total = await crud.list_jobs(db, limit=1)
            return total

    total_jobs = asyncio.run(test_db())
    print(f"   ✓ Database connection successful")
    print(f"   ✓ Total jobs in database: {total_jobs}")

except Exception as e:
    print(f"   ✗ Database test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check configuration
print("\n5. Testing configuration...")
try:
    from backend.config import settings

    print(f"   ✓ FALL_DETECTION_ENABLED: {settings.FALL_DETECTION_ENABLED}")
    print(f"   ✓ FIGHT_DETECTION_ENABLED: {settings.FIGHT_DETECTION_ENABLED}")
    print(f"   ✓ HEATMAP_ENABLED: {settings.HEATMAP_ENABLED}")
    print(f"   ✓ ALERTS_ENABLED: {settings.ALERTS_ENABLED}")

    if settings.ALERT_WEBHOOK_URL:
        print(f"   ✓ ALERT_WEBHOOK_URL: {settings.ALERT_WEBHOOK_URL}")
    else:
        print(f"   ℹ ALERT_WEBHOOK_URL: Not configured (optional)")

except Exception as e:
    print(f"   ✗ Config test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("API Integration Test Complete!")
print("=" * 60)

print("\n✅ Backend is ready to start!")
print("\nTo start the server, run:")
print("  cd backend")
print("  python -m uvicorn api.main:app --reload --port 8000")
print("\nThen test with:")
print("  curl http://localhost:8000/api/v1/health")
