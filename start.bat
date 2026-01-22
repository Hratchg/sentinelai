@echo off
echo.
echo ============================================================
echo   Starting SentinelAI
echo ============================================================
echo.
echo [1/2] Launching Backend API Server (with venv)...
start "SentinelAI Backend" cmd /k "cd backend && venv\Scripts\activate && python ..\start_api.py"
echo     Backend starting on http://localhost:8000
echo.
timeout /t 3 /nobreak > nul
echo [2/2] Launching Frontend Dashboard...
start "SentinelAI Frontend" cmd /k "cd frontend && npm run dev"
echo     Frontend starting on http://localhost:5173
echo.
echo ============================================================
echo   SentinelAI is starting!
echo ============================================================
echo.
echo   Backend API:  http://localhost:8000/api/docs
echo   Frontend UI:  http://localhost:5173
echo.
echo   Wait a few seconds for servers to start, then open:
echo   http://localhost:5173
echo.
echo   Press any key to close this window...
echo ============================================================
pause > nul
