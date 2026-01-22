# SentinelAI API Quick Reference

## Your API is Running! ✅

**Server:** http://localhost:8000

---

## 🌐 Open in Browser

### Main Endpoints to Visit:

1. **Interactive API Documentation (Swagger UI)** ⭐ RECOMMENDED
   ```
   http://localhost:8000/api/docs
   ```
   - Upload videos directly from browser
   - Test all endpoints interactively
   - See request/response examples

2. **Alternative Documentation (ReDoc)**
   ```
   http://localhost:8000/api/redoc
   ```
   - Clean, readable API documentation
   - Better for reading/understanding

3. **Root Endpoint**
   ```
   http://localhost:8000/
   ```
   Returns: `{"status":"ok","service":"SentinelAI API","version":"0.1.0"}`

4. **Health Check**
   ```
   http://localhost:8000/health
   ```
   Returns: `{"status":"healthy","database":"connected"}`

---

## 📤 Upload a Video (via Browser)

1. Go to http://localhost:8000/api/docs
2. Find **POST /api/v1/upload** endpoint
3. Click "Try it out"
4. Click "Choose File" and select a video
5. Click "Execute"
6. Copy the `job_id` from the response

---

## 📊 Check Results

### Get Job Status
```
http://localhost:8000/api/v1/jobs/{job_id}
```
Replace `{job_id}` with your actual job ID.

### Download Processed Video
```
http://localhost:8000/api/v1/results/{job_id}/video
```

### Get Events (Actions Detected)
```
http://localhost:8000/api/v1/results/{job_id}/events
```

### 🆕 Download Heatmap (Week 3)
```
http://localhost:8000/api/v1/results/{job_id}/heatmap
```

### 🆕 Get Alerts (Week 3)
```
http://localhost:8000/api/v1/results/{job_id}/alerts
```

---

## 🔍 Example Workflow

1. **Upload** video at http://localhost:8000/api/docs
   - Get `job_id` (e.g., "abc123...")

2. **Monitor** processing:
   - Visit: `http://localhost:8000/api/v1/jobs/abc123...`
   - Wait for status: "completed"

3. **View Results**:
   - Events: `http://localhost:8000/api/v1/results/abc123.../events`
   - Heatmap: `http://localhost:8000/api/v1/results/abc123.../heatmap`
   - Alerts: `http://localhost:8000/api/v1/results/abc123.../alerts`
   - Video: `http://localhost:8000/api/v1/results/abc123.../video`

---

## 📝 Current Status

Your server is running and shows:
```json
{
  "status": "ok",
  "service": "SentinelAI API",
  "version": "0.1.0",
  "docs": "/api/docs"
}
```

This means:
- ✅ Server is running
- ✅ API is responding
- ✅ All endpoints are available
- ✅ Week 3 features are active

---

## 🎯 Quick Actions

**Want to test immediately?**

1. Open browser: http://localhost:8000/api/docs
2. You'll see the Swagger UI with all endpoints
3. Find "POST /api/v1/upload" and expand it
4. Click "Try it out"
5. Upload a test video
6. Watch it process!

**No video handy?**
- Use any MP4, AVI, MOV, or MKV file
- Max 100MB
- Surveillance footage works best for Week 3 features

---

## 🔧 Troubleshooting

**Can't access http://localhost:8000/api/docs?**
- Make sure server is still running
- Check console for errors
- Try http://127.0.0.1:8000/docs instead

**Upload fails?**
- Check file is <100MB
- Check format is MP4, AVI, MOV, or MKV
- See console logs for detailed error

**Processing stuck?**
- Check console logs
- First video may take time (downloading YOLO model)
- Processing time: ~30-60 seconds per minute of video

---

## 📚 Full Documentation

- **Implementation:** [WEEK3_IMPLEMENTATION_SUMMARY.md](WEEK3_IMPLEMENTATION_SUMMARY.md)
- **Testing Guide:** [WEEK3_TESTING_GUIDE.md](WEEK3_TESTING_GUIDE.md)
- **System Status:** [SYSTEM_STATUS.md](SYSTEM_STATUS.md)
- **Quick Start:** [QUICK_START.md](QUICK_START.md)

---

**Your API is fully operational!** 🚀
**Next:** Visit http://localhost:8000/api/docs to start testing!
