# SentinelAI: Smart Surveillance System

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**An end-to-end AI-powered video surveillance system with real-time person detection, multi-object tracking, and intelligent action recognition.**

## What is SentinelAI?

SentinelAI is a comprehensive surveillance platform that combines computer vision and artificial intelligence to provide intelligent video monitoring. It features real-time camera streaming, person detection and tracking, voice-activated controls, and automated event detection including falls and fights. The system processes video feeds to identify and track individuals, recognize behavioral patterns, and generate alerts for suspicious activities.

Built with a modern tech stack including FastAPI for the backend and React for the frontend, SentinelAI offers both live camera monitoring and batch video processing capabilities. The platform includes features like gesture recognition, heatmap generation, face recognition, and natural language querying through voice commands.

## Key Features

- **Real-time Camera Surveillance**: Live streaming from multiple cameras with WebSocket-based frame delivery
- **Person Detection & Tracking**: YOLOv8-powered detection with ByteTrack multi-object tracking
- **Action Recognition**: Automatic detection of standing, walking, running, and loitering behaviors
- **Fall & Fight Detection**: Advanced detection of emergency situations
- **Voice Control**: "Hey Sentinel" wake word activation with natural language queries
- **Face Recognition**: Identify and track known individuals
- **Gesture Learning**: Teach and recognize custom gestures
- **Heatmap Analytics**: Visualize movement patterns and high-traffic areas
- **Alert System**: Real-time notifications for detected events
- **Video Processing**: Upload and analyze recorded video files

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Live Camera  │  │ Upload Page  │  │ Analytics Dashboard│   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API + WebSocket
┌────────────────────────────┼────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Processing Pipeline (Async)                  │  │
│  │  ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌─────────┐ │  │
│  │  │ Camera  │──▶│Detector │──▶│ Tracker  │──▶│ Action  │ │  │
│  │  │ Stream  │   │(YOLOv8) │   │(ByteTrack)│  │ Engine  │ │  │
│  │  └─────────┘   └─────────┘   └──────────┘   └─────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL (optional, SQLite by default)
- (Optional) NVIDIA GPU with CUDA 11.8+ for faster processing

### Installation

**1. Backend Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

**2. Frontend Dependencies**
```bash
cd frontend
npm install
```

**3. Environment Setup**
```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your settings (database, API keys, etc.)
```

**4. Start Application**
```bash
# Option A: One command (Windows)
start.bat

# Option B: Manual (2 terminals)
python start_api.py          # Terminal 1
cd frontend && npm run dev   # Terminal 2
```

**5. Open Browser**
```
http://localhost:5173
```

## Usage

### Live Camera Monitoring
1. Navigate to the Dashboard
2. View real-time camera feeds with person detection
3. Use voice commands: "Hey Sentinel, show me recent alerts"

### Video Upload
1. Click "Upload Video"
2. Drag and drop video file (MP4, AVI, MOV)
3. Monitor processing progress
4. View results with annotations and event timeline

### Gesture Teaching
1. Go to "Gesture Teacher"
2. Record new gesture samples
3. Train the system to recognize custom gestures

## Project Structure

```
sentinelai/
├── backend/              # FastAPI backend
│   ├── api/             # REST endpoints & WebSocket
│   ├── core/            # Processing pipeline
│   ├── auth/            # Authentication & security
│   ├── llm/             # LLM integration for queries
│   ├── storage/         # Database & file management
│   └── workers/         # Background job processors
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page views
│   │   └── services/    # API client
├── data/                # Video storage & outputs
└── docs/                # Documentation
```

## Performance

| Hardware | FPS | Latency |
|----------|-----|---------|
| CPU (i7) | 8-12 | 125ms/frame |
| GPU (T4) | 45-60 | 20ms/frame |
| GPU (RTX 4090) | 120+ | 8ms/frame |

## API Documentation

**Interactive Docs**:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Health Check: http://localhost:8000/health

## Tech Stack

**Backend**:
- FastAPI, PyTorch, Ultralytics (YOLOv8)
- BoxMOT (ByteTrack), OpenCV
- PostgreSQL/SQLite, SQLAlchemy
- Anthropic Claude API

**Frontend**:
- React 18, TypeScript, Vite
- TailwindCSS
- WebSocket for real-time streaming

**Models**:
- YOLOv8n (person detection)
- ByteTrack (multi-object tracking)
- MediaPipe (pose estimation)

## Contributing

This is a portfolio project, but suggestions are welcome! Open an issue or PR.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built for intelligent video surveillance and security**
