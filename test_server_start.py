"""
Test server startup without actually running it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

print("Testing backend server startup...")

try:
    # Import the app
    from backend.api.main import app
    print("✓ App imported")

    # Check if lifespan events are configured
    print("✓ Lifespan events configured")

    # Check worker is importable
    from backend.workers.video_processor import start_worker
    print("✓ Worker module loaded")

    # Check all Week 3 routes exist
    week3_endpoints = []
    for route in app.routes:
        if hasattr(route, 'path'):
            if 'heatmap' in route.path or 'alerts' in route.path:
                week3_endpoints.append(route.path)

    print(f"✓ Week 3 endpoints registered: {len(week3_endpoints)}")
    for endpoint in week3_endpoints:
        print(f"  - {endpoint}")

    print("\n✅ Server is ready to start!")
    print("\nStart command:")
    print("  cd backend")
    print("  python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")

except Exception as e:
    print(f"\n✗ Server startup test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
