# SentinelAI Project Structure

## Current Implementation (Day 1-2)

```
sentinelai/
│
├── README.md                       ✅ Main project documentation
├── SETUP.md                        ✅ Installation & setup guide
├── DAY_1_2_CHECKLIST.md           ✅ Validation checklist
├── QUICK_REFERENCE.md             ✅ Quick usage reference
├── STRUCTURE.md                    ✅ This file
├── LICENSE                         ✅ MIT License
├── .gitignore                      ✅ Git ignore rules
├── .env.example                    ✅ Environment template
│
├── backend/                        # Python backend (FastAPI)
│   ├── __init__.py                ✅ Package init
│   ├── config.py                  ✅ Configuration management
│   ├── requirements.txt           ✅ Python dependencies
│   │
│   ├── core/                       # Core processing modules ✅
│   │   ├── __init__.py            ✅ Module exports
│   │   ├── detector.py            ✅ YOLOv8 person detector
│   │   ├── tracker.py             ✅ ByteTrack multi-object tracker
│   │   ├── actions.py             ✅ Rule-based action classifier
│   │   ├── events.py              ✅ Event logging & filtering
│   │   ├── video_io.py            ✅ Video reading & writing
│   │   └── pipeline.py            ✅ Main processing orchestrator
│   │
│   ├── utils/                      # Utility modules ✅
│   │   ├── __init__.py            ✅
│   │   ├── performance.py         ✅ FPS & latency monitoring
│   │   └── visualization.py       ✅ Drawing annotations
│   │
│   ├── scripts/                    # Test & utility scripts ✅
│   │   ├── __init__.py            ✅
│   │   └── test_pipeline.py       ✅ Day 1-2 test script
│   │
│   ├── api/                        # REST API (Week 1) 🚧
│   │   ├── __init__.py            ✅
│   │   ├── routes.py              🚧 API endpoints
│   │   ├── models.py              🚧 Pydantic schemas
│   │   └── deps.py                🚧 Dependencies
│   │
│   ├── storage/                    # Database & file storage (Week 1) 🚧
│   │   ├── __init__.py            ✅
│   │   ├── database.py            🚧 SQLite job management
│   │   └── file_manager.py        🚧 File operations
│   │
│   ├── workers/                    # Background processing (Week 1) 🚧
│   │   ├── __init__.py            ✅
│   │   └── processor.py           🚧 Async job worker
│   │
│   └── models/                     # ML model weights
│       ├── .gitkeep               ✅
│       ├── yolov8n.pt             📥 Auto-downloaded on first run
│       └── action_classifier.pth  🚧 Week 4+
│
├── frontend/                       # React frontend (Week 2) 🚧
│   ├── package.json               🚧
│   ├── src/
│   │   ├── App.jsx                🚧
│   │   ├── components/            🚧
│   │   ├── api/                   🚧
│   │   └── styles/                🚧
│   └── public/                    🚧
│
├── data/                           # Data storage
│   ├── uploads/                   ✅ Incoming videos
│   │   └── .gitkeep              ✅
│   ├── processed/                 ✅ Annotated outputs
│   │   └── .gitkeep              ✅
│   ├── events/                    ✅ JSON event logs
│   │   └── .gitkeep              ✅
│   └── sample_videos/             ✅ Test datasets
│       └── .gitkeep              ✅
│
├── notebooks/                      # Jupyter notebooks (Week 3+) 🚧
│   ├── model_evaluation.ipynb     🚧 Benchmark models
│   └── action_model_training.ipynb 🚧 Train action classifier
│
├── tests/                          # Unit tests (Week 2) 🚧
│   ├── test_detector.py           🚧
│   ├── test_tracker.py            🚧
│   ├── test_actions.py            🚧
│   └── test_api.py                🚧
│
├── docker/                         # Docker deployment (Week 2+) 🚧
│   ├── Dockerfile.backend         🚧
│   ├── Dockerfile.frontend        🚧
│   └── docker-compose.yml         🚧
│
└── docs/                           # Documentation assets 🚧
    └── screenshots/               🚧 UI screenshots

Legend:
✅ = Implemented (Day 1-2)
🚧 = Planned (Future weeks)
📥 = Auto-downloaded
```

---

## Module Dependency Graph

```
┌─────────────────────────────────────────┐
│          Scripts & Tests                │
│  ┌─────────────────────────────────┐   │
│  │  test_pipeline.py               │   │
│  └────────────┬────────────────────┘   │
└───────────────┼─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│          Core Pipeline                  │
│  ┌─────────────────────────────────┐   │
│  │  pipeline.py                    │   │
│  │  - orchestrates all components  │   │
│  └──┬───────┬──────┬──────┬────────┘   │
└─────┼───────┼──────┼──────┼─────────────┘
      │       │      │      │
      ▼       ▼      ▼      ▼
┌─────────┐ ┌──────┐ ┌──────┐ ┌────────┐
│detector │ │tracker│ │actions│ │events  │
│         │ │       │ │       │ │        │
│YOLOv8   │ │Byte   │ │Rule   │ │Logger  │
│wrapper  │ │Track  │ │Based  │ │Filter  │
└─────────┘ └──────┘ └──────┘ └────────┘
      │         │        │         │
      └─────────┴────────┴─────────┘
                │
                ▼
         ┌────────────┐
         │  video_io  │
         │  VideoReader│
         │  VideoWriter│
         └────────────┘

Utilities (used by all):
├── performance.py (monitoring)
├── visualization.py (drawing)
└── config.py (settings)
```

---

## Data Flow

```
Input Video (MP4)
    │
    ▼
┌───────────────┐
│ VideoReader   │ Read frames (with skip)
└───────┬───────┘
        │
        ▼ frame (numpy array)
┌───────────────┐
│ YOLOv8Detector│ Detect persons
└───────┬───────┘
        │
        ▼ detections [x1,y1,x2,y2,conf]
┌───────────────┐
│ ByteTracker   │ Track across frames
└───────┬───────┘
        │
        ▼ tracks {id, bbox, state}
┌───────────────┐
│ActionClassifier│ Classify actions
└───────┬───────┘
        │
        ▼ tracks + actions
┌───────────────┐
│ EventLogger   │ Generate events
└───────┬───────┘
        │
        ├─────────────────┐
        │                 │
        ▼                 ▼
┌───────────────┐  ┌─────────────┐
│ VideoWriter   │  │ JSON Export │
│ (annotated)   │  │ (events)    │
└───────────────┘  └─────────────┘
        │                 │
        ▼                 ▼
   output.mp4        events.json
```

---

## Configuration Flow

```
Environment Variables (.env)
            │
            ▼
┌───────────────────────┐
│     config.py         │
│  - Settings class     │
│  - Pydantic validation│
└───────┬───────────────┘
        │
        ├─────────┬─────────┬─────────┬────────┐
        │         │         │         │        │
        ▼         ▼         ▼         ▼        ▼
    detector  tracker  actions  video_io  pipeline
```

---

## File Size Estimates

| Component | Files | Lines | Size |
|-----------|-------|-------|------|
| Core modules | 6 | ~1800 | 60 KB |
| Utilities | 2 | ~600 | 20 KB |
| Config | 1 | ~200 | 8 KB |
| Scripts | 1 | ~100 | 4 KB |
| **Total Code** | **10** | **~2700** | **~92 KB** |
| | | | |
| Documentation | 5 | ~1500 | 50 KB |
| **Total Project** | **15** | **~4200** | **~142 KB** |

**Model weights** (not in git):
- yolov8n.pt: ~6 MB (auto-downloaded)

---

## API Surface (Public Interface)

### Main Entry Point
```python
from backend.core import VideoPipeline

pipeline = VideoPipeline()
results = pipeline.process_video(input_path, output_path)
```

### Individual Components
```python
from backend.core import YOLOv8Detector, ByteTracker, ActionClassifier

detector = YOLOv8Detector()
tracker = ByteTracker()
classifier = ActionClassifier()

# Use separately
detections = detector.detect(frame)
tracks = tracker.update(detections, frame_id)
action, conf = classifier.classify(track)
```

### Utilities
```python
from backend.utils import PerformanceMonitor, draw_annotations

perf = PerformanceMonitor()
with perf.measure('operation'):
    # ... code ...

annotated = draw_annotations(frame, tracks)
```

---

## Key Design Decisions

### 1. Modular Architecture
- **Why**: Easy to swap detector/tracker/action models
- **Benefit**: Can upgrade from rule-based → ML actions without rewriting pipeline

### 2. Configuration Centralization
- **Why**: Single source of truth for all settings
- **Benefit**: Easy to tune performance vs accuracy

### 3. Performance Monitoring Built-in
- **Why**: CV systems need profiling for optimization
- **Benefit**: Know exactly where bottlenecks are

### 4. Event-based Logging
- **Why**: Only log action changes (not every frame)
- **Benefit**: Manageable event logs even for long videos

### 5. Type Hints & Docstrings
- **Why**: Portfolio project needs production quality
- **Benefit**: IDE autocomplete, easier maintenance

---

## Future Extensions (Hooks for Week 2+)

### API Layer (Week 1)
```
backend/api/routes.py
├── POST   /api/v1/upload
├── GET    /api/v1/jobs/{id}
├── GET    /api/v1/results/{id}/video
└── GET    /api/v1/results/{id}/events
```

### Database Schema (Week 1)
```sql
jobs
├── id (PK)
├── status (queued/processing/completed/failed)
├── input_video_path
├── output_video_path
├── events_path
├── created_at
└── completed_at
```

### ML Action Model (Week 4+)
```
backend/core/actions.py
├── ActionClassifier (rule-based) ✅
└── MLActionClassifier (X3D)      🚧
    ├── clip_extraction
    ├── model_inference
    └── action_mapping
```

---

## Testing Strategy

### Unit Tests (Week 2)
- `test_detector.py`: Detection accuracy, FPS
- `test_tracker.py`: Track persistence, ID switches
- `test_actions.py`: Action classification correctness
- `test_events.py`: Event filtering, JSON export

### Integration Tests (Week 2)
- `test_pipeline.py`: End-to-end processing
- `test_api.py`: REST endpoints

### Performance Tests (Week 3)
- Benchmark on MOT17 dataset
- FPS measurements across hardware
- Memory usage profiling

---

## Documentation Status

| Document | Status | Purpose |
|----------|--------|---------|
| README.md | ✅ | Project overview |
| SETUP.md | ✅ | Installation guide |
| DAY_1_2_CHECKLIST.md | ✅ | Validation steps |
| QUICK_REFERENCE.md | ✅ | Usage examples |
| STRUCTURE.md | ✅ | This file |
| PERFORMANCE.md | 🚧 | Benchmarks (Week 3) |
| DEPLOYMENT.md | 🚧 | Docker guide (Week 2) |
| API.md | 🚧 | API docs (Week 1) |

---

**Last Updated**: Day 1-2 completion
**Next Milestone**: Week 1 - FastAPI backend
