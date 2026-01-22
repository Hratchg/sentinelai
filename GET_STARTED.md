# 🚀 Get Started with SentinelAI

Welcome! This guide will get you up and running in **under 10 minutes**.

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
cd sentinelai/backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

**Time**: ~5 minutes (downloads PyTorch + dependencies)

### Step 2: Validate Setup

```bash
cd ..
python validate_setup.py
```

This checks:
- Python version
- All dependencies
- GPU availability (optional)
- Core modules

**Expected output**: All checks ✓ passed

### Step 3: Add Test Video & Run

```bash
# Download a test video (10-30 seconds, people walking)
# Save to: data/sample_videos/test.mp4

# Run the pipeline
cd backend
python scripts/test_pipeline.py
```

**Output**:
- Annotated video: `data/processed/test_output.mp4`
- Events log: `data/events/test_events.json`

---

## 📺 What You'll See

### Input Video
Your test video (e.g., people walking in a hallway)

### Output Video
Same video with:
- ✅ Bounding boxes around people
- ✅ Track IDs (1, 2, 3...)
- ✅ Action labels (walking, standing, running, loitering)
- ✅ FPS counter

### Events JSON
```json
{
  "total_events": 87,
  "events": [
    {
      "frame_number": 234,
      "track_id": 3,
      "action": "walking",
      "confidence": 0.91,
      "bbox": [120, 340, 180, 520]
    }
  ]
}
```

---

## 🎯 Expected Performance

| Your Hardware | Expected FPS | Processing Time (30s video) |
|---------------|-------------|----------------------------|
| CPU (i5/i7) | 8-12 FPS | ~5-7 seconds |
| GPU (GTX 1060) | 30-40 FPS | ~2 seconds |
| GPU (RTX 3060+) | 60-100 FPS | ~1 second |

---

## 🔧 Configuration (Optional)

Edit `backend/config.py` to tune performance:

### For Speed (lower quality)
```python
FRAME_SKIP = 3              # Skip more frames
DETECTOR_CONFIDENCE = 0.35  # Fewer detections
```

### For Quality (lower speed)
```python
FRAME_SKIP = 1              # Process all frames
DETECTOR_CONFIDENCE = 0.20  # More detections
```

---

## 📚 What You Built (Day 1-2)

### Detection
- Person detection with YOLOv8
- GPU acceleration (if available)
- Confidence filtering

### Tracking
- Multi-person tracking across frames
- Persistent track IDs
- Velocity computation

### Actions
- **Standing**: Stationary, not loitering
- **Walking**: Moderate velocity
- **Running**: High velocity
- **Loitering**: Stationary for 3+ seconds

### Output
- Annotated video
- Structured event log (JSON)
- Performance metrics

---

## 🎓 Next Steps

### Explore the Code
- [core/pipeline.py](backend/core/pipeline.py) - Main orchestrator
- [core/detector.py](backend/core/detector.py) - YOLO wrapper
- [core/tracker.py](backend/core/tracker.py) - ByteTrack wrapper
- [core/actions.py](backend/core/actions.py) - Action classifier

### Try Different Videos
- Crowded scenes
- Different lighting conditions
- Indoor vs outdoor
- Different camera angles

### Tune Thresholds
Adjust action detection in `config.py`:
- `VELOCITY_WALKING_THRESHOLD` - Walking speed
- `VELOCITY_RUNNING_THRESHOLD` - Running speed
- `LOITERING_THRESHOLD` - Loitering time

### Week 1 Preview: REST API
Next, you'll build:
- FastAPI backend
- Upload endpoint
- Job management
- Results API

---

## 🐛 Troubleshooting

### "CUDA not available"
✅ **Normal** - Will use CPU. For GPU:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### "boxmot not found"
```bash
pip install boxmot==10.0.47
```

### "Video codec error"
Install ffmpeg:
- **Windows**: Download from https://ffmpeg.org/
- **Linux**: `sudo apt install ffmpeg`
- **Mac**: `brew install ffmpeg`

### Low FPS on CPU
Increase frame skip:
```python
FRAME_SKIP = 3  # in config.py
```

---

## 📖 Documentation

- [SETUP.md](SETUP.md) - Detailed setup guide
- [DAY_1_2_CHECKLIST.md](DAY_1_2_CHECKLIST.md) - Validation checklist
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Code examples
- [STRUCTURE.md](STRUCTURE.md) - Project architecture

---

## 💡 Example Usage

### Process a Video Programmatically

```python
from pathlib import Path
from backend.core import VideoPipeline

pipeline = VideoPipeline()

results = pipeline.process_video(
    input_path=Path("input.mp4"),
    output_path=Path("output.mp4"),
    events_path=Path("events.json")
)

print(f"Processed {results['performance']['overall']['total_frames']} frames")
print(f"Found {results['event_summary']['unique_tracks']} people")
print(f"Average FPS: {results['performance']['overall']['fps']:.2f}")
```

### Filter Events by Action

```python
import json

with open("data/events/test_events.json") as f:
    data = json.load(f)

# Find all running events
running = [e for e in data["events"] if e["action"] == "running"]
print(f"Found {len(running)} running events")

# Find loitering
loitering = [e for e in data["events"] if e["action"] == "loitering"]
for event in loitering:
    print(f"Track {event['track_id']} loitered at {event['time_seconds']:.1f}s")
```

---

## 🎉 Success Checklist

- [x] Dependencies installed
- [x] Validation passed
- [x] Test video processed
- [x] Output video has annotations
- [x] Events JSON created
- [x] Reasonable FPS achieved

**You're ready to build the full system!**

---

## 🤝 Need Help?

1. Check [SETUP.md](SETUP.md) troubleshooting section
2. Review validation output: `python validate_setup.py`
3. Check console for error messages
4. Verify test video format (MP4, AVI, MOV)

---

## 🎯 Week 1 Preview

Next milestone: **FastAPI Backend**

You'll add:
- REST API with 4 endpoints
- SQLite job management
- Background processing
- Simple React frontend

**Estimated time**: 1 week

See [README.md](README.md) for full roadmap.

---

**Built with ❤️ for Computer Vision**

Ready to deploy smart surveillance AI!
