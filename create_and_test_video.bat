@echo off
echo ========================================
echo SentinelAI - Create Test Video
echo ========================================
echo.

echo Step 1: Creating test video...
.\backend\venv\Scripts\python.exe create_test_video.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Failed to create test video
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 2: Testing video file...
.\backend\venv\Scripts\python.exe test_video_file.py test_video.mp4

echo.
echo ========================================
echo Done!
echo ========================================
echo.
echo You can now upload test_video.mp4 via the frontend:
echo http://localhost:5173
echo.
pause
