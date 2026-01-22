# Video Upload Troubleshooting

## Error: "Unsupported 'img_numpy' input format '<class 'NoneType'>'"

This error means the video file cannot be read properly by OpenCV.

---

## Quick Fix Steps

### Step 1: Test Your Video File

Run the diagnostic script:

```bash
.\backend\venv\Scripts\python.exe test_video_file.py "path\to\your\video.mp4"
```

Example:
```bash
.\backend\venv\Scripts\python.exe test_video_file.py "data\uploads\test_video.mp4"
```

This will tell you if the video file is readable.

---

### Step 2: Common Causes & Solutions

#### Cause 1: Unsupported Video Codec ⚠️ MOST COMMON

**Problem:** Your video uses a codec that OpenCV doesn't support on your system.

**Solution:** Re-encode the video to H.264 MP4 format:

```bash
# Install ffmpeg if you don't have it: https://ffmpeg.org/download.html

# Re-encode video
ffmpeg -i input_video.mp4 -c:v libx264 -c:a aac -preset fast output_video.mp4
```

**Supported formats:**
- ✅ MP4 with H.264 codec (best compatibility)
- ✅ AVI with MJPEG codec
- ⚠️ MOV (depends on codec inside)
- ⚠️ MKV (depends on codec inside)
- ❌ HEVC/H.265 (often not supported by OpenCV)
- ❌ VP9/WebM (limited support)

#### Cause 2: Corrupted Video File

**Problem:** The video file is damaged.

**Solution:**
1. Try playing the video in VLC media player
2. If VLC can't play it, the file is likely corrupted
3. Try re-downloading or using a different video

#### Cause 3: File Path Issues

**Problem:** Special characters or spaces in filename.

**Solution:**
- Rename file to simple name: `test_video.mp4`
- Avoid spaces, use underscores: `my_video.mp4` instead of `my video.mp4`
- Upload directly through the web interface instead of copying to uploads folder

---

## Testing After Fix

### Method 1: Use the Diagnostic Script

```bash
.\backend\venv\Scripts\python.exe test_video_file.py "your_fixed_video.mp4"
```

Should show:
```
✅ Video opened successfully!
✅ Video file is OK and should work with SentinelAI!
```

### Method 2: Upload via Frontend

1. Open http://localhost:5173
2. Click upload button
3. Select your video
4. Watch the processing status

---

## Getting a Test Video

If you don't have a suitable video, you can:

### Option 1: Download a sample surveillance video

Free sample videos:
- https://sample-videos.com/
- https://www.pexels.com/search/videos/surveillance/
- https://pixabay.com/videos/search/cctv/

### Option 2: Create a test video with your webcam

```bash
# Record 10 seconds from webcam
ffmpeg -f dshow -i video="Integrated Camera" -t 10 -c:v libx264 test_video.mp4
```

### Option 3: Generate a test video

```python
# Run this to create a simple test video
.\backend\venv\Scripts\python.exe -c "
import cv2
import numpy as np

# Create a 5-second test video (30 fps)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test_video.mp4', fourcc, 30.0, (640, 480))

for i in range(150):  # 5 seconds at 30 fps
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    out.write(frame)

out.release()
print('Test video created: test_video.mp4')
"
```

---

## Recommended Video Specifications

For best results with SentinelAI:

**Format:**
- Container: MP4
- Video codec: H.264 (libx264)
- Audio codec: AAC (or no audio)

**Resolution:**
- Minimum: 640x480
- Recommended: 1280x720 (720p) or 1920x1080 (1080p)
- Maximum: 3840x2160 (4K)

**Frame Rate:**
- Minimum: 15 FPS
- Recommended: 30 FPS
- Maximum: 60 FPS

**Duration:**
- Recommended: 10 seconds to 5 minutes for testing
- Maximum: Limited by file size (100MB)

**File Size:**
- Maximum: 100MB per upload

**Content:**
- Must contain people (for detection)
- Surveillance/security footage works best
- Clear lighting conditions
- Stable camera angle preferred

---

## Backend Improvements (Already Applied)

The following improvements have been added to handle video issues gracefully:

1. **Frame Validation** (pipeline.py)
   - Checks if frame is None before processing
   - Skips invalid frames instead of crashing
   - Logs warnings for debugging

2. **Error Messages**
   - Clear error messages when video can't be opened
   - Diagnostic information in logs

---

## Still Having Issues?

### Check Backend Logs

Look at the terminal where you started the backend server. You should see:

```
✓ Video loaded: 1920x1080 @ 30.0 fps, 450 frames (15.0s)
Processing: your_video.mp4
```

If you see errors like:
- `Failed to open video: ...` - Video file is corrupted or codec unsupported
- `Invalid frame at frame_id X` - Some frames are corrupted

### Get More Details

Run the full system test:

```bash
.\backend\venv\Scripts\python.exe debug_full_system.py
```

This will check all components are working.

---

## Quick Reference Commands

**Test video file:**
```bash
.\backend\venv\Scripts\python.exe test_video_file.py "video.mp4"
```

**Convert video to compatible format:**
```bash
ffmpeg -i input.mp4 -c:v libx264 -c:a aac -preset fast output.mp4
```

**Check video info:**
```bash
ffmpeg -i video.mp4
```

**Restart backend:**
```bash
# Ctrl+C to stop, then:
.\backend\venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Summary

**Most Common Solution:** Re-encode your video to H.264 MP4 format using ffmpeg.

**Quick Test:** Use `test_video_file.py` to check if your video is compatible.

**Best Format:** MP4 with H.264 codec, 720p or 1080p, 30 FPS.
