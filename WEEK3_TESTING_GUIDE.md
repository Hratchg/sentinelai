# Week 3 Testing Guide

## Quick Start

### 1. Database Setup ✅
The database has been initialized with Week 3 schema. You're ready to go!

### 2. Start the Backend
```bash
# From project root with venv activated
cd backend
python -m uvicorn api.main:app --reload --port 8000
```

### 3. Start the Frontend
```bash
cd frontend
npm run dev
```

---

## Testing Scenarios

### Test 1: Fall Detection
**Objective:** Verify fall detection identifies people who have fallen

**Test Video Requirements:**
- Person lying on ground (horizontal orientation)
- Person falling down (rapid vertical movement)
- Person staying down for 5+ seconds

**Expected Outputs:**
- Events JSON shows "fallen" action with high confidence (>0.6)
- Video annotations show red bounding boxes with "⚠ FALL DETECTED" label
- Alerts JSON contains fall_detected alerts with CRITICAL severity

**API Verification:**
```bash
# Upload video
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@fall_test.mp4"

# Get job status (use job_id from upload response)
curl http://localhost:8000/api/v1/jobs/{job_id}

# Download events
curl http://localhost:8000/api/v1/results/{job_id}/events

# Download alerts
curl http://localhost:8000/api/v1/results/{job_id}/alerts

# Check for "fallen" actions and fall_detected alerts
```

---

### Test 2: Fight Detection
**Objective:** Verify fight detection identifies physical altercations

**Test Video Requirements:**
- Two or more people in close proximity (bboxes overlapping)
- Rapid movement from both participants
- Interaction sustained for 2+ seconds

**Expected Outputs:**
- Events JSON shows fight events with participant track IDs
- Video annotations show orange boxes around both participants
- Alerts JSON contains fight_detected alerts with HIGH severity

**Verification:**
```bash
# Check events for fight events
curl http://localhost:8000/api/v1/results/{job_id}/events | jq '.events[] | select(.event_type == "fight")'

# Check alerts
curl http://localhost:8000/api/v1/results/{job_id}/alerts | jq '.alerts[] | select(.alert_type == "fight_detected")'
```

---

### Test 3: Heatmap Generation
**Objective:** Verify heatmap shows activity zones

**Test Video Requirements:**
- Multiple people moving through different areas
- Some high-traffic zones, some low-traffic zones

**Expected Outputs:**
- Heatmap PNG file generated
- High-activity areas show hot colors (red/yellow)
- Low-activity areas show cool colors (blue/purple)

**Verification:**
```bash
# Download heatmap
curl http://localhost:8000/api/v1/results/{job_id}/heatmap -o heatmap.png

# Open in image viewer
# Verify hot spots correlate with actual activity in video
```

---

### Test 4: Alert System
**Objective:** Verify all alert types are generated correctly

**Test Scenarios:**

1. **Fall Alert (CRITICAL)**
   - Upload video with person falling
   - Check alerts JSON for CRITICAL severity

2. **Fight Alert (HIGH)**
   - Upload video with two people fighting
   - Check alerts JSON for HIGH severity

3. **Loitering Alert (MEDIUM)**
   - Upload video with person standing still for 30+ seconds
   - Check alerts JSON for MEDIUM severity

4. **Crowd Alert (MEDIUM)**
   - Upload video with 10+ people in frame
   - Check alerts JSON for MEDIUM severity

**Verification:**
```bash
# Get alert summary
curl http://localhost:8000/api/v1/results/{job_id}/alerts | jq '.summary'

# Expected output:
{
  "total_alerts": 5,
  "by_severity": {
    "critical": 2,
    "high": 1,
    "medium": 2,
    "low": 0
  },
  "by_type": {
    "fall_detected": 2,
    "fight_detected": 1,
    "prolonged_loitering": 1,
    "crowd_detected": 1
  },
  "unacknowledged": 5
}
```

---

### Test 5: Webhook Notifications (Optional)
**Objective:** Verify webhook notifications are sent

**Setup:**
1. Create test webhook endpoint (e.g., using webhook.site or RequestBin)
2. Set webhook URL in config:
   ```env
   ALERT_WEBHOOK_URL=https://webhook.site/your-unique-id
   ```
3. Restart backend

**Expected Behavior:**
- Webhook receives POST requests for each alert
- Payload contains alert details (type, severity, timestamp, track IDs)
- Retry logic works (check logs if webhook is down)

**Webhook Payload Example:**
```json
{
  "alert_id": "550e8400-e29b-41d4-a716-446655440000",
  "alert_type": "fall_detected",
  "severity": "critical",
  "message": "Fall detected for person #3",
  "timestamp": "2026-01-16T17:30:45.123456",
  "track_ids": [3],
  "frame_id": 450,
  "metadata": {
    "aspect_ratio": 0.45,
    "vertical_velocity": 25.3,
    "ground_proximity": 0.95
  }
}
```

---

## Performance Testing

### Target Metrics:
- **Processing Speed:** >15 FPS on CPU
- **Fall Detection:** <1ms per track
- **Fight Detection:** <2ms per frame (when 2+ tracks)
- **Heatmap:** <0.1ms per detection
- **Alerts:** <0.5ms per frame

### Verification:
```bash
# Check performance stats in results
curl http://localhost:8000/api/v1/results/{job_id}/events | jq '.performance'

# Expected output shows component timing
{
  "overall": {
    "total_frames": 900,
    "total_time_sec": 45.2,
    "fps": 19.9
  },
  "components": {
    "detection": {"mean_ms": 35.2},
    "tracking": {"mean_ms": 8.1},
    "action_classification": {"mean_ms": 0.8},
    "fight_detection": {"mean_ms": 1.2},
    "alert_generation": {"mean_ms": 0.4},
    "visualization": {"mean_ms": 5.3},
    "video_write": {"mean_ms": 12.1}
  }
}
```

---

## Common Issues & Solutions

### Issue: Import Error for BYTETracker
**Solution:** Fixed! The correct import is `ByteTrack` (not `BYTETracker`)

### Issue: Database Migration Fails
**Solution:** Run `python -m backend.storage.init_db` for fresh setup

### Issue: Heatmap Not Generated
**Solution:** Ensure `HEATMAP_ENABLED=true` in config

### Issue: Alerts Not Generated
**Solution:** Ensure `ALERTS_ENABLED=true` in config

### Issue: Webhook Not Sending
**Solution:**
- Check `ALERT_WEBHOOK_URL` is set correctly
- Check backend logs for retry errors
- Verify webhook endpoint is accessible

---

## Test Checklist

- [ ] Database initialized with Week 3 schema
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can upload video successfully
- [ ] Video processes without errors
- [ ] Fall detection works (red boxes, "fallen" events)
- [ ] Fight detection works (fight events with participant IDs)
- [ ] Heatmap generated and downloadable
- [ ] Alerts JSON generated with correct severity
- [ ] Webhook notifications sent (if configured)
- [ ] Processing speed >15 FPS
- [ ] API endpoints return correct data

---

## Next Steps

### After Testing:
1. Document any bugs found
2. Collect performance metrics
3. Fine-tune detection thresholds if needed
4. Implement frontend components (AlertsPanel, HeatmapViewer)
5. Add end-to-end tests

### Configuration Tuning:
```env
# Adjust thresholds based on test results
FALL_ASPECT_RATIO_THRESHOLD=0.8        # Lower = more sensitive
FALL_VERTICAL_VELOCITY_THRESHOLD=20.0  # Lower = more sensitive
FIGHT_PROXIMITY_IOU_THRESHOLD=0.3      # Lower = more sensitive
FIGHT_RAPID_MOVEMENT_THRESHOLD=15.0    # Lower = more sensitive
```

---

## Sample Test Videos

### Recommended Sources:
1. **UCF Crime Dataset** - Real surveillance footage
2. **AVA Actions Dataset** - Annotated activity videos
3. **YouTube Creative Commons** - Search for:
   - "person falling cctv"
   - "fight caught on camera"
   - "crowded street surveillance"
   - "loitering security footage"

### Creating Custom Test Videos:
```bash
# Use FFmpeg to create test scenarios
# Example: Extract clip from longer video
ffmpeg -i input.mp4 -ss 00:01:30 -t 00:00:30 -c copy fall_test.mp4
```

---

## Success Criteria

✅ **Week 3 Implementation Complete When:**
1. All 5 new modules working correctly
2. Database schema includes new columns
3. API endpoints return correct data
4. Processing maintains >15 FPS
5. Fall detection accuracy >80%
6. Fight detection accuracy >70%
7. Heatmaps accurately show activity zones
8. Alerts generated with correct severity
9. No critical bugs in production code
10. Frontend can display all Week 3 features

---

**Current Status:** Backend implementation complete, ready for testing! ✅
