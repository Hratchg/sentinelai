"""
Start SentinelAI Backend Server
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Starting SentinelAI Backend Server")
    print("=" * 60)
    print(f"Project Root: {project_root}")
    print(f"Python Path: {sys.path[0]}")
    print()

    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
