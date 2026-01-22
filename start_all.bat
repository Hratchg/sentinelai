@echo off
echo ========================================
echo Starting SentinelAI Full Stack
echo ========================================
echo.

echo [1/2] Starting Backend Server...
echo.
start "SentinelAI Backend" cmd /k "cd /d %~dp0 && .\backend\venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak > nul

echo [2/2] Starting Frontend Server...
echo.
start "SentinelAI Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/api/docs
echo.
echo Press any key to close this window...
pause > nul
