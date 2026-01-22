# Getting Started with SentinelAI

Welcome! This guide will help you set up and use SentinelAI for the first time.

---

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.9+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/) (for frontend)
- **(Optional) NVIDIA GPU** with CUDA 11.8+ for faster processing

### Check Your Setup

```bash
# Check Python version
python --version  # Should be 3.9 or higher

# Check Node.js version
node --version    # Should be 18.0 or higher

# Check npm version
npm --version
```

---

## 🚀 First-Time Setup

**IMPORTANT**: You must complete this setup BEFORE running the application!

### Step 1: Install Backend Dependencies

```bash
# From project root, navigate to backend
cd backend

# Install Python packages (this may take 5-10 minutes)
pip install -r requirements.txt
```

**Note**: PyTorch installation can be large (~2GB). If you have a GPU, PyTorch will automatically use it.

### Step 2: Install Frontend Dependencies

```bash
# From project root, navigate to frontend
cd frontend

# Install Node packages (this may take 2-3 minutes)
npm install
```

**Wait for installation to complete!** You should see "added XXX packages" when done.

This installs React, TailwindCSS, Vite, and other frontend dependencies.

### ✅ Verify Installation

After both steps complete, verify:

```bash
# Check backend
cd backend
python -c "import fastapi; print('Backend OK')"

# Check frontend
cd frontend
npm list vite --depth=0
```

If both show success, you're ready to run the application!

---

## 🎬 Running the Application

You need **two terminal windows** running simultaneously:

### Option A: Automatic Startup (Windows)

**Easiest method** - Double-click `start.bat` in the project root, or run:

```bash
start.bat
```

This automatically opens two command windows:
- **Backend API Server** on http://localhost:8000
- **Frontend Dashboard** on http://localhost:5173

### Option B: Manual Startup

#### Terminal 1: Start Backend API

```bash
# From project root
python start_api.py
```

You should see:
```
============================================================
  SentinelAI API Server
============================================================
  Host: 0.0.0.0
  Port: 8000

  API Docs: http://0.0.0.0:8000/api/docs
  Health: http://0.0.0.0:8000/health
  Base URL: http://0.0.0.0:8000/api/v1
============================================================
```

#### Terminal 2: Start Frontend Dashboard

```bash
# From project root
cd frontend
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.x:5173/
```

---

## 🖥️ Using the Application

### 1. Open the Dashboard

Open your web browser and go to:
```
http://localhost:5173
```

You should see the SentinelAI home page.

### 2. Upload a Video

#### Step-by-Step:

1. **Click "Upload"** in the navigation bar
2. **Drag and drop** a video file, or **click to browse**
3. **Supported formats**: MP4, AVI, MOV, MKV
4. **Max file size**: 100 MB
5. **Click "Upload and Process"**

You'll be automatically redirected to the Results page!

### 3. Monitor Processing

The application will process your video in the background:

- **Progress bar** shows 0-100% completion
- **Status updates** every 2 seconds
- **Typical processing time**:
  - 30-second video on GPU: ~30 seconds
  - 30-second video on CPU: ~2-3 minutes

You can also click **"Jobs"** in the navigation to see all your jobs.

### 4. View Results

Once processing completes (status shows "Completed"):

#### **Processed Video**
- Watch the video with annotations in the built-in player
- Bounding boxes around detected people
- Track IDs for each person
- Action labels (standing, walking, running, loitering)
- Click **"Download"** to save the video

#### **Video Metadata**
- Duration
- Total events detected
- Number of unique people tracked

#### **Action Summary**
- Count of each action type
- Color-coded badges

#### **Events Timeline**
- Scrollable list of all detected events
- Timestamps for each event
- Track IDs
- Action types
- Confidence scores

### 5. Download Results

Click the **"Download"** button to save:
- Annotated video (same format as input)
- Events JSON (via API endpoint)

---

## 📹 Finding Sample Videos

### Option 1: Use Your Own Videos

Any surveillance-style video works! Best results with:
- Clear view of people
- Good lighting
- MP4, AVI, or MOV format
- Under 100 MB

### Option 2: Download Sample Videos

See `/data/sample_videos/README.md` for links to:
- Free surveillance footage
- Test videos
- Public domain videos

### Option 3: Create a Test Video

Record a short video (10-30 seconds) with your webcam or phone camera showing:
- People walking
- People standing
- Movement patterns

---

## 🎯 Quick Test Workflow

Here's a complete test from start to finish:

```bash
# 1. Start both servers
start.bat

# 2. Open browser
# Go to: http://localhost:5173

# 3. Upload a video
# - Click "Upload"
# - Drag & drop your video
# - Click "Upload and Process"

# 4. Wait for processing
# - Watch progress bar
# - Status updates automatically

# 5. View results
# - Watch annotated video
# - Explore events timeline
# - Download processed video
```

**Expected time**: 2-5 minutes for a 30-second video

---

## 🔍 Understanding the Results

### Action Types

| Action | Description | Behavior |
|--------|-------------|----------|
| **Standing** | Person is stationary | Low velocity (< 3 px/frame) |
| **Walking** | Normal walking pace | Moderate velocity (3-12 px/frame) |
| **Running** | Fast movement | High velocity (> 12 px/frame) |
| **Loitering** | Stationary for 3+ seconds | Prolonged standing in one location |

### Track IDs

Each person detected gets a unique ID (e.g., Track #1, Track #2). This ID persists across frames so you can follow individual people through the video.

### Confidence Scores

Each detection has a confidence score (0-100%). Higher scores mean the model is more confident in its classification.

---

## 🛠️ Troubleshooting

### Backend Won't Start

**Problem**: `ModuleNotFoundError` or import errors

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

**Problem**: Port 8000 already in use

**Solution**:
```bash
# Start on a different port
python start_api.py --port 8080
```

### Frontend Won't Start

**Problem**: `'vite' is not recognized as an internal or external command`

**Solution**: Dependencies not installed! Run:
```bash
cd frontend
npm install
```
Wait for installation to complete, then try again.

**Problem**: `npm ERR!` or dependency errors

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Problem**: Port 5173 already in use

**Solution**: Vite will automatically use port 5174 or the next available port.

### Video Upload Fails

**Problem**: "Invalid file format" error

**Solution**: Make sure your video is MP4, AVI, or MOV format.

**Problem**: "File size exceeds limit"

**Solution**: Video must be under 100 MB. Compress your video or use a shorter clip.

### Processing Stuck

**Problem**: Job stuck at "Queued" or "Processing"

**Solution**:
1. Check backend terminal for errors
2. Refresh the Jobs page
3. Restart the backend server

**Problem**: Processing very slow

**Solution**:
- **GPU**: Make sure CUDA is installed and PyTorch detects your GPU
- **CPU**: Processing will be slower (3-5x slower than GPU)
- **Shorter videos**: Try a 10-second clip first

### Can't See Results

**Problem**: Video player shows black screen

**Solution**:
1. Check if job status is "Completed"
2. Try downloading the video instead
3. Check browser console for errors (F12)

### CORS Errors

**Problem**: Browser console shows CORS errors

**Solution**: Make sure both backend (8000) and frontend (5173) are running.

---

## ⚡ Performance Tips

### For Faster Processing

1. **Use a GPU**: 10-20x faster than CPU
2. **Shorter videos**: Start with 10-30 second clips
3. **Lower resolution**: 720p processes faster than 1080p
4. **Close other programs**: Free up system resources

### Expected Processing Times

| Video Length | Hardware | Approximate Time |
|--------------|----------|------------------|
| 10 seconds | CPU (i7) | ~1 minute |
| 10 seconds | GPU (GTX 1060) | ~5 seconds |
| 30 seconds | CPU (i7) | ~3 minutes |
| 30 seconds | GPU (GTX 1060) | ~30 seconds |
| 60 seconds | GPU (RTX 3060) | ~45 seconds |

---

## 📊 Understanding the Dashboard

### Home Page
- Welcome message
- Feature overview
- Project statistics
- Quick links to Upload and Jobs

### Upload Page
- Drag-and-drop upload zone
- File validation
- Upload progress
- Auto-redirect to results

### Jobs Page
- List of all jobs
- Real-time status updates (every 2 seconds)
- Filter by status
- Progress bars for active jobs
- Delete jobs button

### Results Page
- Video player with controls
- Download button
- Video metadata cards
- Action summary statistics
- Events timeline (scrollable)
- Color-coded action badges

---

## 🎓 Advanced Usage

### Using the API Directly

You can also interact with the backend API directly:

```bash
# Upload a video
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@path/to/video.mp4"

# Check job status
curl "http://localhost:8000/api/v1/jobs/{job_id}"

# Download results
curl "http://localhost:8000/api/v1/results/{job_id}/video" -o processed.mp4
curl "http://localhost:8000/api/v1/results/{job_id}/events" | jq '.'
```

### API Documentation

Visit the interactive API docs:
```
http://localhost:8000/api/docs
```

Here you can:
- See all endpoints
- Try API calls directly
- View request/response schemas

### Processing Multiple Videos

Upload multiple videos through the UI - they'll be queued and processed sequentially.

---

## 📖 Additional Resources

### Documentation

- **[API.md](API.md)** - Complete API reference
- **[TIMELINE.md](TIMELINE.md)** - Project roadmap
- **[WEEK1_QUICKSTART.md](WEEK1_QUICKSTART.md)** - Backend quick start
- **[WEEK1_SUMMARY.md](WEEK1_SUMMARY.md)** - Week 1 implementation details
- **[WEEK2_SUMMARY.md](WEEK2_SUMMARY.md)** - Week 2 implementation details
- **[frontend/README.md](frontend/README.md)** - Frontend documentation

### Architecture

- **Backend**: FastAPI + PyTorch + YOLOv8 + ByteTrack
- **Frontend**: React + TypeScript + TailwindCSS
- **Database**: SQLite (for job management)
- **Processing**: Async job queue with progress tracking

### Getting Help

1. **Check Documentation**: Start with this guide and API.md
2. **Check Logs**: Look at terminal output for error messages
3. **Health Check**: Visit http://localhost:8000/health
4. **Interactive Docs**: Try http://localhost:8000/api/docs

---

## 🎉 You're Ready!

That's it! You now know how to:
- ✅ Install dependencies
- ✅ Start the application
- ✅ Upload videos
- ✅ Monitor processing
- ✅ View results
- ✅ Download processed videos
- ✅ Troubleshoot issues

### Next Steps

1. **Try it out**: Upload your first video!
2. **Explore features**: Check out the Jobs page and API docs
3. **Read more**: See TIMELINE.md for upcoming features
4. **Experiment**: Try different types of videos

---

**Need more help?** Check the other documentation files or review the troubleshooting section above.

**Ready to start?** Run `start.bat` and open http://localhost:5173 🚀

---

**Last Updated**: January 16, 2025
**Version**: 0.1.0 (Week 1 + 2 Complete)
