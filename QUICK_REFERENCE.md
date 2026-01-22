# SentinelAI Quick Reference

## 🚀 Quick Start

```bash
# Setup
cd sentinelai/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run test
python scripts/test_pipeline.py
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/config.py` | All configuration settings |
| `backend/core/pipeline.py` | Main processing orchestrator |
| `backend/core/detector.py` | YOLOv8 person detector |
| `backend/core/tracker.py` | ByteTrack multi-object tracker |
| `backend/core/actions.py` | Rule-based action classifier |
| `backend/scripts/test_pipeline.py` | Test script |

---

## 🎛️ Key Configuration

Edit `backend/config.py` or create `.env`:

```python
# Performance
FRAME_SKIP = 2              # Process every Nth frame
DETECTOR_FP16 = True        # Half precision (GPU only)

# Detection
DETECTOR_CONFIDENCE = 0.25  # Min detection score
DETECTOR_IOU = 0.45         # NMS threshold

# Tracking
TRACK_BUFFER = 30           # Frames to keep lost tracks
MATCH_THRESH = 0.8          # IoU for track matching

# Actions
VELOCITY_WALKING_THRESHOLD = 3.0   # px/frame
VELOCITY_RUNNING_THRESHOLD = 12.0  # px/frame
LOITERING_THRESHOLD = 90           # frames (~3s)
```

---

## 🔧 Common Tasks

### Process a Video Programmatically

```python
from pathlib import Path
from core.pipeline import process_video_simple

results = process_video_simple(
    input_path="data/sample_videos/test.mp4",
    output_path="data/processed/output.mp4",
    events_path="data/events/events.json"
)

print(f"Processed {results['performance']['overall']['total_frames']} frames")
print(f"Found {results['event_summary']['unique_tracks']} tracks")
```

### Custom Pipeline

```python
from core import VideoPipeline, YOLOv8Detector, ByteTracker, ActionClassifier

# Create custom components
detector = YOLOv8Detector(conf_threshold=0.3)
tracker = ByteTracker(track_buffer=60)
classifier = ActionClassifier(loitering_threshold=120)

# Create pipeline
pipeline = VideoPipeline(
    detector=detector,
    tracker=tracker,
    action_classifier=classifier,
    frame_skip=1  # Process all frames
)

# Process video
results = pipeline.process_video(
    input_path=Path("input.mp4"),
    output_path=Path("output.mp4"),
    events_path=Path("events.json")
)
```

### Filter Events

```python
import json

# Load events
with open("data/events/test_events.json") as f:
    data = json.load(f)

events = data["events"]

# Filter by action
running_events = [e for e in events if e["action"] == "running"]

# Filter by track
track_3_events = [e for e in events if e["track_id"] == 3]

# Filter by time
events_10_to_20s = [e for e in events if 10 <= e["time_seconds"] <= 20]
```

---

## 🎨 Visualization Options

```python
from core.video_io import VideoReader, VideoWriter
from utils.visualization import draw_annotations, draw_fps, draw_track_history

reader = VideoReader("input.mp4")
writer = VideoWriter("output.mp4", fps=30, frame_size=(1920, 1080))

for frame_id, frame in reader:
    # ... run detection, tracking, actions ...

    # Draw annotations
    annotated = draw_annotations(
        frame,
        tracks,
        show_bbox=True,
        show_id=True,
        show_action=True,
        show_velocity=True  # Show velocity value
    )

    # Add FPS counter
    annotated = draw_fps(annotated, current_fps)

    # Draw track history trails
    for track in tracks:
        annotated = draw_track_history(annotated, track, max_points=30)

    writer.write(annotated)
```

---

## 📊 Performance Monitoring

```python
from utils.performance import PerformanceMonitor

perf = PerformanceMonitor()
perf.start_session()

for frame in frames:
    with perf.measure("detection"):
        detections = detector.detect(frame)

    with perf.measure("tracking"):
        tracks = tracker.update(detections, frame_id)

    perf.increment_frame()

perf.end_session()

# Print detailed report
perf.print_report()

# Or get dict
report = perf.report()
print(f"Average FPS: {report['overall']['fps']:.2f}")
```

---

## 🔍 Event Schema

```json
{
  "job_id": "uuid-1234",
  "timestamp": "2026-01-16T10:23:45.123Z",
  "frame_number": 1523,
  "time_seconds": 50.77,
  "track_id": 3,
  "bbox": [120.5, 340.2, 180.8, 520.1],
  "action": "walking",
  "confidence": 0.91,
  "metadata": {
    "velocity_px_per_frame": 8.3,
    "stationary_frames": 0,
    "bbox_area": 10842,
    "track_duration_frames": 87,
    "detection_confidence": 0.87
  }
}
```

---

## 🐛 Debug Tips

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check GPU Availability

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device: {torch.cuda.get_device_name(0)}")
```

### Visualize Single Frame

```python
from core import YOLOv8Detector
import cv2

detector = YOLOv8Detector()
frame = cv2.imread("frame.jpg")
detections = detector.detect(frame)

print(f"Found {len(detections)} people")
for i, det in enumerate(detections):
    x1, y1, x2, y2, conf = det
    print(f"  Person {i}: bbox=[{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}], conf={conf:.2f}")
```

### Profile Bottlenecks

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run pipeline
pipeline.process_video(...)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

---

## ⚙️ Optimization Tips

### Increase Speed (Lower Quality)
```python
FRAME_SKIP = 3              # Skip more frames
DETECTOR_CONFIDENCE = 0.35  # Higher threshold = less detections
OUTPUT_FPS = 10             # Lower output framerate
```

### Increase Quality (Lower Speed)
```python
FRAME_SKIP = 1              # Process all frames
DETECTOR_CONFIDENCE = 0.15  # Lower threshold = more detections
DETECTOR_MODEL = "yolov8s.pt"  # Larger model
```

### Reduce Memory Usage
```python
MAX_DETECTIONS = 50         # Limit detections per frame
TRACK_BUFFER = 15           # Shorter track history
```

---

## 📝 Action Thresholds

Adjust based on video resolution and FPS:

| Resolution | Walking Thresh | Running Thresh | Loitering Frames |
|------------|---------------|----------------|------------------|
| 640x480    | 2.0           | 8.0            | 60               |
| 1280x720   | 3.0           | 12.0           | 90               |
| 1920x1080  | 4.5           | 18.0           | 90               |

For videos at different FPS:
```python
loitering_seconds = 3.0  # Want 3 seconds
video_fps = 25  # Your video FPS
LOITERING_THRESHOLD = int(loitering_seconds * video_fps / FRAME_SKIP)
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Low FPS | Increase `FRAME_SKIP`, enable FP16, use GPU |
| Wrong actions | Adjust velocity thresholds for resolution |
| Lost tracks | Increase `TRACK_BUFFER` |
| False detections | Increase `DETECTOR_CONFIDENCE` |
| Missing people | Decrease `DETECTOR_CONFIDENCE` |
| Memory error | Reduce `TRACK_BUFFER`, increase `FRAME_SKIP` |

---

## 📚 Module Import Guide

```python
# Core processing
from core import VideoPipeline
from core.detector import YOLOv8Detector
from core.tracker import ByteTracker, TrackState
from core.actions import ActionClassifier
from core.events import EventLogger
from core.video_io import VideoReader, VideoWriter

# Utilities
from utils.performance import PerformanceMonitor, FPSCounter
from utils.visualization import draw_annotations, draw_fps

# Config
from config import settings, perf_config
```

---

## 🎯 Common Patterns

### Batch Process Multiple Videos

```python
from pathlib import Path
from core.pipeline import VideoPipeline

pipeline = VideoPipeline()
input_dir = Path("data/sample_videos")

for video_path in input_dir.glob("*.mp4"):
    output_path = Path("data/processed") / f"{video_path.stem}_output.mp4"
    events_path = Path("data/events") / f"{video_path.stem}_events.json"

    print(f"Processing: {video_path.name}")
    pipeline.process_video(video_path, output_path, events_path)
```

### Extract Specific Frames

```python
from core.video_io import VideoReader
import cv2

reader = VideoReader("input.mp4", frame_skip=30)  # Every 30th frame

for frame_id, frame in reader:
    cv2.imwrite(f"frame_{frame_id:05d}.jpg", frame)
```

---

**For full documentation, see [SETUP.md](SETUP.md) and [DAY_1_2_CHECKLIST.md](DAY_1_2_CHECKLIST.md)**
