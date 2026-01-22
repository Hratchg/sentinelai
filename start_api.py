#!/usr/bin/env python3
"""
SentinelAI API Server Startup Script

Usage:
    python start_api.py                    # Start with default settings
    python start_api.py --port 8080        # Custom port
    python start_api.py --host 0.0.0.0     # Listen on all interfaces
    python start_api.py --reload           # Enable auto-reload for development
"""

import sys
import argparse
import uvicorn
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    parser = argparse.ArgumentParser(description="Start SentinelAI API Server")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Log level (default: info)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  SentinelAI API Server")
    print("=" * 60)
    print(f"  Host: {args.host}")
    print(f"  Port: {args.port}")
    print(f"  Reload: {args.reload}")
    print(f"  Log Level: {args.log_level}")
    print("=" * 60)
    print(f"\n  API Docs: http://{args.host}:{args.port}/api/docs")
    print(f"  Health: http://{args.host}:{args.port}/health")
    print(f"  Base URL: http://{args.host}:{args.port}/api/v1")
    print("\n" + "=" * 60 + "\n")

    # Start server
    uvicorn.run(
        "backend.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        access_log=True
    )


if __name__ == "__main__":
    main()
