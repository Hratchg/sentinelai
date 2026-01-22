# Sample Videos for SentinelAI

This directory is for storing sample surveillance videos to test the application.

---

## 📹 Where to Find Sample Videos

### Option 1: Free Surveillance Footage

**Pexels** (Free, no attribution required):
- Search: "surveillance camera footage"
- Search: "security camera"
- Search: "people walking"
- Link: https://www.pexels.com/search/videos/surveillance/

**Pixabay** (Free, no attribution required):
- Search: "cctv footage"
- Search: "security camera"
- Link: https://pixabay.com/videos/search/surveillance/

**Videvo** (Free with attribution):
- Search: "surveillance"
- Link: https://www.videvo.net/

### Option 2: Public Datasets

**MOT Challenge**:
- Multiple Object Tracking benchmark dataset
- Link: https://motchallenge.net/

**UCF Crime Dataset** (sample clips):
- University of Central Florida crime detection dataset
- Link: https://www.crcv.ucf.edu/projects/real-world/

### Option 3: Create Your Own

Record a short video (10-30 seconds) with:
- Webcam or smartphone camera
- People walking, standing, or moving
- Clear view and good lighting
- Save as MP4 format

---

## ✅ Video Requirements

### Supported Formats
- **MP4** (recommended)
- **AVI**
- **MOV**
- **MKV**

### File Size
- **Maximum**: 100 MB
- **Recommended**: 10-50 MB for faster processing

### Video Characteristics

**Best Results**:
- Clear view of people
- Good lighting (not too dark)
- 720p or 1080p resolution
- 10-60 seconds duration
- Multiple people for tracking demo
- Movement (walking, running) for action recognition

**Avoid**:
- Very dark or overexposed footage
- Extremely low resolution (<480p)
- Very shaky/unstable camera
- Files over 100 MB

---

## 📝 Recommended Test Videos

### Beginner Test (10-15 seconds)
- 1-2 people
- Clear, well-lit scene
- Simple movements (walking)

### Intermediate Test (30 seconds)
- 3-5 people
- Multiple actions (standing, walking)
- Surveillance camera perspective

### Advanced Test (60 seconds)
- 5+ people
- Complex movements
- Tracking across full video
- Multiple simultaneous actions

---

## 🚀 How to Use Sample Videos

### 1. Download a Video

Choose a video from the sources above and download it to this directory:
```
/data/sample_videos/my_test_video.mp4
```

### 2. Upload via UI

1. Start the application (run `start.bat`)
2. Open http://localhost:5173
3. Click "Upload"
4. Drag & drop your video or click to browse
5. Select the video from this folder
6. Click "Upload and Process"

### 3. Upload via API

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@data/sample_videos/my_test_video.mp4"
```

---

## 📊 Example Results

### What to Expect

After processing, you'll see:

**Annotations**:
- Bounding boxes around each person
- Track IDs (e.g., "Track #1", "Track #2")
- Action labels (standing, walking, running, loitering)
- FPS counter

**Events**:
- Timestamp for each action change
- Track ID
- Action type
- Confidence score
- Bounding box coordinates

**Statistics**:
- Total number of events
- Number of unique people tracked
- Breakdown of actions (standing: 10, walking: 15, etc.)

---

## 💡 Tips

### For Better Results

1. **Start small**: Use 10-15 second clips first
2. **Good lighting**: Avoid very dark videos
3. **Clear view**: Front-facing view works better than top-down
4. **Real movement**: Videos with actual movement show more actions

### Processing Time

| Video Length | Hardware | Time |
|--------------|----------|------|
| 10 seconds | CPU | ~1 min |
| 10 seconds | GPU | ~5 sec |
| 30 seconds | CPU | ~3 min |
| 30 seconds | GPU | ~30 sec |

### Format Conversion

If your video isn't in a supported format, convert it with FFmpeg:

```bash
# Install FFmpeg: https://ffmpeg.org/download.html

# Convert to MP4
ffmpeg -i input.mkv -c:v libx264 -c:a aac output.mp4

# Compress large video
ffmpeg -i input.mp4 -vf scale=1280:720 -c:v libx264 -crf 23 output.mp4
```

---

## 🎬 Sample Video Checklist

Before uploading a video, check:

- [ ] Format is MP4, AVI, MOV, or MKV
- [ ] File size is under 100 MB
- [ ] Video shows people (not just objects or scenery)
- [ ] Lighting is adequate (not too dark)
- [ ] Resolution is at least 480p (720p+ recommended)
- [ ] Duration is between 10-60 seconds

---

## 📁 Organization

You can organize videos in subdirectories:

```
sample_videos/
├── indoor/
│   ├── office_walking.mp4
│   └── hallway_surveillance.mp4
├── outdoor/
│   ├── street_crowd.mp4
│   └── park_joggers.mp4
└── test/
    ├── quick_test.mp4
    └── full_test.mp4
```

---

## ⚠️ Important Notes

1. **Privacy**: Only use videos you have rights to use
2. **Public Datasets**: Follow their license requirements
3. **No Personal Videos**: Don't upload private surveillance without consent
4. **Copyright**: Respect video copyrights and usage terms

---

## 🆘 Having Issues?

### Video Upload Fails
- Check file size (<100 MB)
- Verify format (MP4, AVI, MOV, MKV)
- Try a different video

### Processing Fails
- Start with a shorter video (10 seconds)
- Check video quality (not corrupted)
- Review backend logs for errors

### No Detections
- Make sure video shows people
- Check lighting (not too dark)
- Verify video plays correctly

---

**Ready to test?** Download a sample video and try it out! 🎬

**Need help?** See [GETTING_STARTED.md](../../GETTING_STARTED.md) for full usage guide.

---

**Last Updated**: January 16, 2025
