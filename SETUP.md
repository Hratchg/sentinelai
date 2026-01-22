# SentinelAI Setup Guide

## Day 1-2: Foundation Setup

This guide will help you set up the basic pipeline for detection and tracking.

---

## Prerequisites

- Python 3.9 or higher
- (Optional) NVIDIA GPU with CUDA 11.8+ for better performance
- Git

---

## Installation Steps

### 1. Clone and Setup Virtual Environment

```bash
cd sentinelai
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: This will download PyTorch. If you have a GPU, ensure you install the CUDA version:

```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 3. Download YOLOv8 Model

The model will auto-download on first run, but you can pre-download:

```bash
# Run Python and download model
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

This downloads the model to your cache (~6MB).

### 4. Add a Test Video

You need a test video to process. Options:

**Option A: Download from Pexels (free)**
```bash
# Visit https://www.pexels.com/search/videos/people%20walking/
# Download a video and save to: data/sample_videos/test.mp4
```

**Option B: Use MOT17 benchmark dataset**
```bash
# Download MOT17: https://motchallenge.net/data/MOT17/
# Extract and copy any .mp4 video to data/sample_videos/test.mp4
```

**Option C: Record from webcam**
```bash
# (Will implement in Week 2)
```

### 5. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env if you want to customize settings
```

---

## Running Day 1-2 Test

### Test the Pipeline

```bash
cd backend
python scripts/test_pipeline.py
```

This will:
1. Load your test video
2. Run person detection (YOLOv8)
3. Track people across frames (ByteTrack)
4. Classify actions (standing, walking, running, loitering)
5. Generate annotated video and event log

**Expected Output**:
- Annotated video: `data/processed/test_output.mp4`
- Events JSON: `data/events/test_events.json`
- Performance report in console

### Expected Performance

| Hardware | Expected FPS |
|----------|-------------|
| CPU (i7) | 8-12 FPS |
| GPU (GTX 1060) | 25-35 FPS |
| GPU (RTX 3060) | 50-70 FPS |
| GPU (RTX 4090) | 100+ FPS |

---

## Troubleshooting

### Issue: CUDA not found

**Solution**: Install CPU version or install CUDA toolkit
```bash
# CPU-only version
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Issue: `boxmot` installation fails

**Solution**: Install build tools
```bash
# Windows: Install Visual Studio Build Tools
# Linux: sudo apt-get install build-essential
# Mac: xcode-select --install
```

### Issue: Video codec error

**Solution**: Install ffmpeg
```bash
# Windows: Download from https://ffmpeg.org/
# Linux: sudo apt-get install ffmpeg
# Mac: brew install ffmpeg
```

### Issue: Out of memory

**Solution**: Increase frame skip in config.py
```python
FRAME_SKIP = 3  # Process every 3rd frame instead of 2nd
```

---

## Next Steps

Once the basic test works:

1. **Test with different videos**: Try crowded scenes, different lighting
2. **Tune thresholds**: Adjust action detection thresholds in config.py
3. **Check output quality**: Watch the annotated video
4. **Review events**: Open the JSON file and inspect event structure

---

## Project Structure

```
sentinelai/
├── backend/
│   ├── core/           # Main processing modules ✅
│   │   ├── detector.py      # YOLOv8 wrapper
│   │   ├── tracker.py       # ByteTrack wrapper
│   │   ├── actions.py       # Action classifier
│   │   ├── events.py        # Event logger
│   │   ├── video_io.py      # Video I/O
│   │   └── pipeline.py      # Main orchestrator
│   ├── utils/          # Utilities ✅
│   │   ├── performance.py   # FPS monitoring
│   │   └── visualization.py # Drawing functions
│   ├── scripts/        # Test scripts ✅
│   │   └── test_pipeline.py
│   ├── config.py       # Configuration ✅
│   └── requirements.txt ✅
├── data/
│   ├── uploads/        # Input videos
│   ├── processed/      # Output videos
│   ├── events/         # Event logs
│   └── sample_videos/  # Test videos
└── README.md           ✅
```

**✅ = Completed in Day 1-2**

---

## Configuration Options

Key settings in [config.py](backend/config.py):

| Setting | Default | Description |
|---------|---------|-------------|
| `FRAME_SKIP` | 2 | Process every Nth frame |
| `DETECTOR_CONFIDENCE` | 0.25 | Min detection confidence |
| `VELOCITY_WALKING_THRESHOLD` | 3.0 | Walking speed (px/frame) |
| `VELOCITY_RUNNING_THRESHOLD` | 12.0 | Running speed (px/frame) |
| `LOITERING_THRESHOLD` | 90 | Frames before loitering |
| `DETECTOR_FP16` | True | Use half precision (GPU) |

---

## Resources

- **YOLOv8 Docs**: https://docs.ultralytics.com/
- **ByteTrack Paper**: https://arxiv.org/abs/2110.06864
- **OpenCV Docs**: https://docs.opencv.org/

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the console output for errors
3. Check that all dependencies installed correctly
4. Ensure your test video is in the correct format (MP4, AVI, MOV)

---

**Next milestone**: Week 1 - FastAPI backend with job management
