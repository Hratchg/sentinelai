@echo off
echo ============================================================
echo Starting SentinelAI Backend Server
echo ============================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Activate virtual environment and start server
echo Activating virtual environment...
call backend\venv\Scripts\activate.bat

echo.
echo Starting backend server at http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

REM Set Python path and start uvicorn
set PYTHONPATH=%CD%
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

pause
