"""
SentinelAI Startup Script

Starts both backend and frontend services for real-time surveillance.

Usage:
    python run.py               # Start both services
    python run.py --backend     # Backend only
    python run.py --frontend    # Frontend only
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Print ASCII art header."""
    print(f"{Colors.OKCYAN}")
    print("=" * 60)
    print(r"""
  ____            _   _            _    _    ___
 / ___|  ___ _ __| |_(_)_ __   ___| |  / \  |_ _|
 \___ \ / _ \ '__| __| | '_ \ / _ \ | / _ \  | |
  ___) |  __/ |  | |_| | | | |  __/ |/ ___ \ | |
 |____/ \___|_|   \__|_|_| |_|\___|_/_/   \_\___|

    """)
    print("Real-Time Conversational Surveillance Assistant")
    print("=" * 60)
    print(f"{Colors.ENDC}")

def check_dependencies():
    """Check if required dependencies are installed."""
    print(f"{Colors.OKBLUE}Checking dependencies...{Colors.ENDC}")

    # Check Python packages
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print(f"{Colors.OKGREEN}✓ Backend dependencies found{Colors.ENDC}")
    except ImportError as e:
        print(f"{Colors.FAIL}✗ Missing backend dependency: {e}{Colors.ENDC}")
        print(f"{Colors.WARNING}Run: cd backend && pip install -r requirements.txt{Colors.ENDC}")
        return False

    # Check Node modules
    frontend_node_modules = Path("frontend/node_modules")
    if frontend_node_modules.exists():
        print(f"{Colors.OKGREEN}✓ Frontend dependencies found{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✗ Frontend dependencies not installed{Colors.ENDC}")
        print(f"{Colors.WARNING}Run: cd frontend && npm install{Colors.ENDC}")
        return False

    # Check .env file
    env_file = Path("backend/.env")
    if env_file.exists():
        print(f"{Colors.OKGREEN}✓ Environment file found{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠ No .env file found. LLM chat may not work.{Colors.ENDC}")
        print(f"{Colors.WARNING}Create backend/.env with: ANTHROPIC_API_KEY=your_key{Colors.ENDC}")

    return True

def start_backend():
    """Start FastAPI backend server."""
    print(f"\n{Colors.OKBLUE}Starting backend server...{Colors.ENDC}")

    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]

    return subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

def start_frontend():
    """Start React frontend dev server."""
    print(f"\n{Colors.OKBLUE}Starting frontend server...{Colors.ENDC}")

    # Determine npm command based on OS
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    frontend_cmd = [npm_cmd, "run", "dev"]

    return subprocess.Popen(
        frontend_cmd,
        cwd="frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

def monitor_process(proc, name, color):
    """Monitor process output."""
    for line in proc.stdout:
        print(f"{color}[{name}]{Colors.ENDC} {line}", end='')

def main():
    """Main startup routine."""
    print_header()

    # Parse arguments
    backend_only = "--backend" in sys.argv
    frontend_only = "--frontend" in sys.argv
    run_both = not backend_only and not frontend_only

    # Check dependencies
    if not check_dependencies():
        print(f"\n{Colors.FAIL}Dependency check failed. Please install missing dependencies.{Colors.ENDC}")
        sys.exit(1)

    print(f"\n{Colors.OKGREEN}All checks passed!{Colors.ENDC}")

    processes = []

    try:
        # Start backend
        if backend_only or run_both:
            backend_proc = start_backend()
            processes.append(("Backend", backend_proc, Colors.OKCYAN))
            time.sleep(2)  # Give backend time to start
            print(f"{Colors.OKGREEN}✓ Backend started on http://localhost:8000{Colors.ENDC}")
            print(f"{Colors.OKGREEN}  API docs: http://localhost:8000/api/docs{Colors.ENDC}")

        # Start frontend
        if frontend_only or run_both:
            frontend_proc = start_frontend()
            processes.append(("Frontend", frontend_proc, Colors.OKBLUE))
            time.sleep(3)  # Give frontend time to start
            print(f"{Colors.OKGREEN}✓ Frontend started on http://localhost:5173{Colors.ENDC}")

        print(f"\n{Colors.BOLD}{Colors.OKGREEN}SentinelAI is running!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Open http://localhost:5173 in your browser{Colors.ENDC}")
        print(f"\n{Colors.WARNING}Press Ctrl+C to stop all services{Colors.ENDC}\n")

        # Monitor processes
        while True:
            time.sleep(0.1)

            # Check if any process died
            for name, proc, _ in processes:
                if proc.poll() is not None:
                    print(f"\n{Colors.FAIL}{name} process exited unexpectedly{Colors.ENDC}")
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Shutting down services...{Colors.ENDC}")

        # Terminate all processes
        for name, proc, _ in processes:
            print(f"{Colors.OKBLUE}Stopping {name}...{Colors.ENDC}")
            proc.terminate()
            try:
                proc.wait(timeout=5)
                print(f"{Colors.OKGREEN}✓ {name} stopped{Colors.ENDC}")
            except subprocess.TimeoutExpired:
                print(f"{Colors.WARNING}Force killing {name}...{Colors.ENDC}")
                proc.kill()

        print(f"\n{Colors.OKGREEN}All services stopped.{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Thank you for using SentinelAI!{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
