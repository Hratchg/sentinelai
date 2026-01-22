# SentinelAI: Smart Surveillance System

![Status](https://img.shields.io/badge/status-week%201%20complete-brightgreen)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Progress](https://img.shields.io/badge/progress-20%25-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

**An end-to-end AI-powered video surveillance system with person detection, multi-object tracking, and action recognition.**

🎉 **Week 1 Complete!** FastAPI backend with job queue, database, and async processing is live!

## Features

**Core CV Pipeline (Day 1-2)** ✅
- ✅ Person detection (YOLOv8n)
- ✅ Multi-object tracking (ByteTrack)
- ✅ Action recognition (standing, walking, running, loitering)
- ✅ Event logging & filtering
- ✅ Annotated video output

**Backend API (Week 1)** ✅
- ✅ FastAPI REST API with 7 endpoints
- ✅ Video upload with validation
- ✅ Background job queue & async processing
- ✅ SQLite database with job management
- ✅ Real-time progress tracking (0-100%)
- ✅ Auto-generated API docs (Swagger UI)

**Coming Soon**
- 🚧 React dashboard (Week 2)
- 🚧 Fall & fight detection (Week 3)
- 🚧 ML-based action classification with X3D (Week 4+)
- 🚧 Real-time alerts & webhooks (Week 3)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Upload Page  │  │ Jobs Monitor │  │ Analytics Dashboard│   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────┼────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Processing Pipeline (Async)                  │  │
│  │  ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌─────────┐ │  │
│  │  │ Video   │──▶│Detector │──▶│ Tracker  │──▶│ Action  │ │  │
│  │  │ Loader  │   │(YOLOv8) │   │(ByteTrack)│  │ Engine  │ │  │
│  │  └─────────┘   └─────────┘   └──────────┘   └─────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.9+
- (Optional) NVIDIA GPU with CUDA 11.8+ for faster processing

### First-Time Setup

**⚠️ IMPORTANT**: Install dependencies before running!

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

**3. Start Application**
```bash
# Option A: One command (Windows)
start.bat

# Option B: Manual (2 terminals)
python start_api.py          # Terminal 1
cd frontend && npm run dev   # Terminal 2
```

**4. Open Browser**
```
http://localhost:5173
```

📖 **Detailed Guide**: See [GETTING_STARTED.md](GETTING_STARTED.md) for complete usage instructions

---

## 🎯 How to Use

### Quick Start (Windows)
```bash
# One command to start everything
start.bat
```
Then open http://localhost:5173

### Manual Start
**Terminal 1** - Backend:
```bash
python start_api.py
```

**Terminal 2** - Frontend:
```bash
cd frontend
npm run dev
```

### Using the Application

1. **Upload a Video**
   - Go to http://localhost:5173
   - Click "Upload" → drag & drop video (MP4, AVI, MOV)
   - Max 100 MB

2. **Monitor Processing**
   - Automatically redirected to Results page
   - Progress bar shows 0-100%
   - Status updates every 2 seconds

3. **View Results**
   - Watch annotated video with bounding boxes
   - See action timeline (standing, walking, running, loitering)
   - Download processed video and events JSON

### Complete Guide
See [GETTING_STARTED.md](GETTING_STARTED.md) for:
- Detailed setup instructions
- Troubleshooting guide
- Sample video recommendations
- API usage examples

---

## Project Structure

```
sentinelai/
├── backend/              # FastAPI backend
│   ├── api/             # REST endpoints
│   ├── core/            # Processing pipeline
│   ├── models/          # ML model weights
│   ├── storage/         # Database & file management
│   └── workers/         # Background job processors
├── frontend/            # React frontend
├── data/                # Video storage
├── tests/               # Unit & integration tests
└── notebooks/           # Evaluation & training
```

## Performance

| Hardware | FPS | Latency |
|----------|-----|---------|
| CPU (i7) | 8-12 | 125ms/frame |
| GPU (T4) | 45-60 | 20ms/frame |
| GPU (RTX 4090) | 120+ | 8ms/frame |

See [PERFORMANCE.md](PERFORMANCE.md) for detailed benchmarks.

## API Documentation

**Interactive Docs**:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Health Check: http://localhost:8000/health

**Detailed Documentation**:
- [API.md](API.md) - Complete API reference with examples
- [WEEK1_QUICKSTART.md](WEEK1_QUICKSTART.md) - Quick start guide
- [TIMELINE.md](TIMELINE.md) - Development timeline and roadmap

## Development Roadmap

**Progress: 20% Complete (2 of 10 weeks)**

```
Timeline:
Foundation  ████████████ 100% ✅ (Day 1-2)
Backend API ████████████ 100% ✅ (Week 1)
Frontend    ░░░░░░░░░░░░   0% 🚧 (Week 2)
Advanced    ░░░░░░░░░░░░   0% 🔲 (Week 3)
ML Actions  ░░░░░░░░░░░░   0% 🔲 (Week 4+)
```

**Completed**:
- [x] Day 1-2: Foundation & CV pipeline
- [x] Week 1: FastAPI backend + job queue

**Next Up**:
- [ ] Week 2: React frontend dashboard
- [ ] Week 3: Fall & fight detection + alerts
- [ ] Week 4+: X3D ML-based action model

📅 **Full Timeline**: See [TIMELINE.md](TIMELINE.md) for detailed roadmap

## Tech Stack

**Backend**:
- FastAPI, PyTorch, Ultralytics (YOLOv8)
- BoxMOT (ByteTrack), OpenCV
- SQLite, Pydantic

**Frontend**:
- React 18, Vite
- Axios, TailwindCSS
- Recharts (analytics)

**Models**:
- YOLOv8n (person detection)
- ByteTrack (multi-object tracking)
- X3D-M (future: action classification)

## Contributing

This is a portfolio project, but suggestions are welcome! Open an issue or PR.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Ultralytics for YOLOv8
- BoxMOT for tracking implementations
- FastAPI for the excellent framework

---

**Built with ❤️ for computer vision and AI**
