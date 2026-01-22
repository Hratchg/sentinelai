# SentinelAI - Deployment Guide

## System Overview

**SentinelAI** is a real-time conversational surveillance assistant with:
- Live camera monitoring with AI detection
- Face recognition with persistent memory
- Custom gesture learning
- LLM-powered conversational queries
- Event-based video clip storage

---

## Pre-Deployment Checklist

### 1. System Requirements

**Hardware:**
- CPU: Intel i5+ or AMD Ryzen 5+ (8 cores recommended)
- RAM: 8 GB minimum (16 GB recommended)
- Storage: 50 GB free space
- Webcam: Built-in or USB (720p minimum, 1080p recommended)
- Optional: NVIDIA GPU with CUDA support for faster processing

**Software:**
- Python 3.10 or higher
- Node.js 18+ and npm
- Git (for cloning repository)

### 2. Required API Keys

**Anthropic API Key** (required for LLM chat):
1. Go to https://console.anthropic.com/
2. Sign up / log in
3. Navigate to API Keys
4. Create new key
5. Copy key (starts with `sk-ant-...`)

---

## Installation Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/sentinelai.git
cd sentinelai
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download YOLOv8 model (first run only)
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Step 3: Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

### Step 4: Environment Configuration

Create `backend/.env`:

```bash
# LLM Configuration (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite+aiosqlite:///./sentinelai.db

# Retention Policies (optional)
PERSON_RETENTION_DAYS=180
EVENT_RETENTION_DAYS=365
CLIP_RETENTION_DAYS=30
ARCHIVED_PERSON_RETENTION_DAYS=730

# Recognition Thresholds (optional)
FACE_SIMILARITY_THRESHOLD=0.6
GESTURE_CONFIDENCE_THRESHOLD=0.7
```

---

## Running the Application

### Option 1: Quick Start (Recommended)

```bash
# From root directory
python run.py
```

This will:
1. Check dependencies
2. Start backend on http://localhost:8000
3. Start frontend on http://localhost:5173
4. Display startup status

**Open your browser to http://localhost:5173**

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Real-Time Pipeline (optional):**
```bash
cd backend
python -m backend.core.camera_stream
```

---

## Verification Steps

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. Check Frontend

Open http://localhost:5173 in browser. You should see:
- Sidebar with "SentinelAI" logo
- Three navigation options: Live Cameras, Teach Gestures, System Health
- Main dashboard with camera feed and chat interface

### 3. Test WebSocket Connection

Check browser console (F12) for:
```
WebSocket connection established to ws://localhost:8000/ws/camera/0
```

### 4. Test API Endpoints

Visit http://localhost:8000/api/docs to see interactive API documentation.

Test endpoints:
- `GET /api/v1/admin/health` - System health stats
- `GET /api/v1/gestures` - List learned gestures
- `POST /api/v1/chat` - Conversational queries

---

## Common Issues and Solutions

### Issue 1: Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Issue 2: Frontend Won't Start

**Error:** `Cannot find module 'react'`

**Solution:**
```bash
cd frontend
npm install
```

### Issue 3: Camera Not Opening

**Error:** `Camera 0 could not be opened`

**Solution:**
```bash
# Check available cameras
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Try different camera ID
# Edit backend/config.py:
# DEFAULT_CAMERA_ID = 1  # or 2, 3, etc.
```

### Issue 4: WebSocket Connection Failed

**Error:** `WebSocket connection failed`

**Solutions:**
1. Ensure backend is running on port 8000
2. Check firewall settings (allow port 8000)
3. Verify CORS settings in `backend/api/main.py`
4. Try refreshing browser (Ctrl+F5)

### Issue 5: LLM Chat Not Working

**Error:** `401 Unauthorized` or `API key invalid`

**Solutions:**
1. Verify `ANTHROPIC_API_KEY` in `backend/.env`
2. Check API key at https://console.anthropic.com/
3. Ensure sufficient API credits
4. Restart backend after updating `.env`

### Issue 6: High CPU Usage

**Symptoms:** System slow, fans loud

**Solutions:**

Edit `backend/config.py`:

```python
# Reduce processing load
FRAME_SKIP = 3        # Process every 3rd frame (instead of 1)
OUTPUT_FPS = 10       # Lower output FPS (instead of 30)
DETECTOR_FP16 = False # Disable half-precision (if CPU only)
```

### Issue 7: Face Recognition Not Working

**Solutions:**
1. Ensure faces are well-lit and visible
2. Lower `FACE_SIMILARITY_THRESHOLD` for stricter matching (0.4-0.5)
3. Check DeepFace models: `~/.deepface/weights/`
4. Restart application after changes

---

## Performance Optimization

### For CPU-Only Systems

Edit `backend/config.py`:

```python
DETECTOR_DEVICE = "cpu"
DETECTOR_FP16 = False
FRAME_SKIP = 3
OUTPUT_FPS = 10
```

### For GPU Systems

```python
DETECTOR_DEVICE = "cuda"
DETECTOR_FP16 = True
FRAME_SKIP = 1
OUTPUT_FPS = 30
```

### Storage Optimization

**30-day retention (default):** ~5.4 GB
**7-day retention:** ~1.2 GB
**90-day retention:** ~16 GB

Edit `backend/config.py`:

```python
CLIP_RETENTION_DAYS = 7  # Adjust as needed
```

---

## Database Management

### Manual Cleanup

1. Go to **System Health** page
2. Click "Run Cleanup Now"
3. Confirm action

This will:
- Archive inactive persons (6 months)
- Delete old events (1 year)
- Delete old clips (30 days)
- Delete archived persons (2 years)

### Automatic Cleanup (Scheduled)

Create a cron job (Linux/macOS) or Task Scheduler (Windows):

```bash
# Run cleanup every day at 2 AM
0 2 * * * cd /path/to/sentinelai/backend && python -m backend.workers.cleanup
```

### Database Backup

```bash
# Backup SQLite database
cp sentinelai.db sentinelai.db.backup

# Backup video clips
tar -czf clips_backup.tar.gz data/clips/
```

---

## Production Deployment

### Backend (FastAPI)

```bash
# Install Gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn backend.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Frontend (React)

```bash
# Build production bundle
cd frontend
npm run build

# Serve with nginx or serve
npx serve -s dist -p 5173
```

### Using Docker (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    devices:
      - /dev/video0:/dev/video0  # Camera access

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

Run:
```bash
docker-compose up -d
```

---

## Security Considerations

### 1. API Key Protection

- **Never commit `.env` to Git**
- Use environment variables in production
- Rotate API keys regularly

### 2. Network Security

- Use HTTPS in production (Let's Encrypt)
- Configure firewall rules
- Restrict API access to trusted IPs

### 3. Database Security

- Encrypt database at rest
- Regular backups
- Sanitize user inputs

### 4. Video Storage

- Encrypt video clips
- Implement access controls
- Follow data retention regulations (GDPR, etc.)

---

## Monitoring and Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# System stats
curl http://localhost:8000/api/v1/admin/health
```

### Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs
# Check browser console (F12)
```

### Metrics to Monitor

- CPU usage
- Memory usage
- Database size
- Disk space
- API response times
- WebSocket connections

---

## Scaling

### Horizontal Scaling

- Load balance multiple backend instances
- Use Redis for shared session state
- Centralize database (PostgreSQL)

### Vertical Scaling

- Add more CPU cores
- Increase RAM
- Use faster GPU
- Add SSD storage

---

## Support

### Documentation

- `REALTIME_SURVEILLANCE.md` - User guide
- `API.md` - API reference
- `TIMELINE.md` - Development roadmap

### API Documentation

http://localhost:8000/api/docs (Swagger UI)

### Community

- GitHub Issues: Report bugs
- Discussions: Ask questions
- Pull Requests: Contribute

---

## License

MIT License - see LICENSE file for details

---

**Deployed successfully? Start monitoring with SentinelAI!** 🎥✨
