# SentinelAI - Real-Time Conversational Surveillance Assistant

**AI-Powered Real-Time Surveillance with Face Recognition, Gesture Learning, and Conversational Queries**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18.2](https://img.shields.io/badge/react-18.2-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is Sentinel AI?

SentinelAI is **NOT** a video upload/processing system. It's a **real-time webcam surveillance assistant** that:

- 📹 **Live Camera Monitoring**: Real-time webcam feed with AI detection
- 👤 **Face Recognition**: Remembers people automatically via face embeddings
- 🗣️ **Audio Name Extraction**: Learns names when people introduce themselves ("Hi, I'm John")
- 🤚 **Custom Gesture Learning**: Teach unlimited gestures on the fly
- 💬 **LLM-Powered Chat**: Ask natural language questions about surveillance data (powered by Claude 3.5 Sonnet)
- 📼 **Event-Based Recording**: Stores short video clips (5-10 seconds) only for important events

### Example Interactions

```
User: "Who is that person on camera 1?"
AI: "That's John Smith. I last saw him 2 hours ago at the entrance."

User: "What is John doing right now?"
AI: "John is waving at the camera. He's been standing for 30 seconds."

User: "When did John last visit?"
AI: "John visited yesterday at 3:42 PM and stayed for 15 minutes."
    [Shows 7-second video clip of John waving]

User: "Teach this gesture as 'peace sign'"
AI: "Gesture recorded and saved as 'peace sign'. I'll recognize it in the future."
```

---

## Quick Start

### 1. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2. Set Environment Variables

Create `backend/.env`:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

Get your API key at: https://console.anthropic.com/

### 3. Run the Application

```bash
# From root directory
python run.py
```

This will start:
- Backend API on http://localhost:8000
- Frontend on http://localhost:5173

### 4. Access Dashboard

Open http://localhost:5173 in your browser.

---

## Features

### 1. Live Camera Monitoring
- Real-time WebSocket streaming
- YOLOv8 person detection
- Bounding box overlays with person IDs
- Event feed display
- FPS counter

### 2. Face Recognition
- DeepFace-based embeddings
- Automatic face matching
- Persistent person database
- Last seen timestamps

### 3. Audio Name Extraction
- Whisper speech recognition
- spaCy NLP for name extraction
- Auto-association with faces

### 4. Gesture Learning
- MediaPipe Pose tracking
- Dynamic Time Warping matching
- Unlimited custom gestures
- Real-time detection

### 5. LLM Conversational Interface
- Claude 3.5 Sonnet powered
- Natural language queries
- Video clip evidence
- Context-aware responses

### 6. Event-Based Video Storage
- Smart 5-10 second clips
- 30-day retention (configurable)
- H.264 compression
- Only important events

### 7. System Health Monitoring
- Database size tracking
- Storage usage visualization
- Manual cleanup trigger
- Retention policies

---

## Usage Guide

### Live Camera View

1. Navigate to **Live Cameras** (default)
2. WebSocket auto-connects
3. See real-time detections
4. View event feed

### Chat with AI

1. Use chat interface on right
2. Ask questions like:
   - "Who is on camera?"
   - "What is Person_123 doing?"
   - "When did I last see John?"

### Teach Gestures

1. Go to **Teach Gestures**
2. Enter gesture name
3. Click "Start Recording"
4. Perform gesture for 1 second
5. System saves and recognizes it

### Monitor System Health

1. Go to **System Health**
2. View stats and storage
3. Trigger manual cleanup
4. Check retention policies

---

## Configuration

### Retention Policies

Edit `backend/config.py`:

```python
PERSON_RETENTION_DAYS = 180      # Archive after 6 months
EVENT_RETENTION_DAYS = 365       # Delete after 1 year
CLIP_RETENTION_DAYS = 30         # Delete after 30 days
ARCHIVED_PERSON_RETENTION_DAYS = 730  # Delete after 2 years
```

### Recognition Thresholds

```python
FACE_SIMILARITY_THRESHOLD = 0.6  # Face matching (0.0-1.0)
GESTURE_CONFIDENCE_THRESHOLD = 0.7  # Gesture matching (0.0-1.0)
```

---

## API Endpoints

### Real-Time Surveillance

- `WS /ws/camera/{id}` - Live camera stream
- `POST /api/v1/chat` - Conversational queries
- `POST /api/v1/gestures/teach` - Teach gesture
- `GET /api/v1/gestures` - List gestures

### System Administration

- `GET /api/v1/admin/health` - System stats
- `POST /api/v1/admin/cleanup` - Manual cleanup
- `GET /api/v1/admin/storage/breakdown` - Storage details

Full docs: http://localhost:8000/api/docs

---

## Storage Requirements

**Typical use (1 camera, 8 hours/day):**

| Component | Storage | Notes |
|-----------|---------|-------|
| Database | 153 MB/year | Persons + events |
| Clips (30 days) | 5.4 GB | 90 clips/day × 2 MB |
| **Total** | **~6 GB** | Very reasonable! |

**Adjust retention**: `CLIP_RETENTION_DAYS = 7` → 1.2 GB

---

## Troubleshooting

### Camera Not Opening

```bash
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

Try different camera ID in config.

### WebSocket Connection Failed

1. Ensure backend running on port 8000
2. Check CORS settings
3. Verify firewall

### LLM Chat Errors

1. Verify `ANTHROPIC_API_KEY` in `.env`
2. Check API key validity
3. Ensure sufficient credits

### High CPU Usage

Edit `backend/config.py`:

```python
FRAME_SKIP = 3  # Process every 3rd frame
OUTPUT_FPS = 10  # Lower FPS
```

---

## Project Structure

```
sentinelai/
├── backend/
│   ├── api/
│   │   ├── main.py          # FastAPI app
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   ├── gestures.py
│   │   │   └── admin.py
│   │   └── websocket.py
│   ├── core/
│   │   ├── camera_stream.py
│   │   ├── realtime_pipeline.py
│   │   ├── face_recognition.py
│   │   ├── gesture_learner.py
│   │   └── audio_processor.py
│   ├── llm/
│   │   └── query_engine.py
│   └── workers/
│       └── cleanup.py
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── components/
│       │   ├── LiveCamera.tsx
│       │   └── ChatInterface.tsx
│       └── pages/
│           ├── GestureTeacher.tsx
│           └── SystemHealth.tsx
└── run.py
```

---

## License

MIT License - see LICENSE file for details

---

## Acknowledgments

- **YOLOv8** - Ultralytics
- **DeepFace** - SerengÃ¼l
- **MediaPipe** - Google
- **Claude 3.5 Sonnet** - Anthropic
- **FastAPI** - Sebastián Ramírez
- **React** - Meta

---

**Built with ❤️ for real-time AI surveillance**
