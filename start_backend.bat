@echo off
echo ============================================================
echo Starting SentinelAI Backend Server
echo ============================================================
echo.

cd /d "%~dp0"
set PYTHONPATH=%CD%

echo Project Root: %CD%
echo.

backend\venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

pause
