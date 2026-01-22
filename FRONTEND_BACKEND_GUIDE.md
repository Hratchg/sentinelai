# Frontend-Backend Connection Guide

## Overview

Your SentinelAI system consists of two components that work together:

1. **Backend API** (FastAPI) - Processes videos, runs AI detection
2. **Frontend Dashboard** (React + Vite) - User interface for uploading/viewing results

---

## Current Status ✅

### Backend Server
- **Status:** Running
- **URL:** http://localhost:8000
- **API Base:** http://localhost:8000/api/v1
- **Documentation:** http://localhost:8000/api/docs

### Frontend Dashboard
- **Status:** Running
- **URL:** http://localhost:5173
- **Connects to:** http://localhost:8000/api/v1

---

## How They Work Together

```
┌─────────────────────┐
│   User's Browser    │
│  localhost:5173     │
│   (React Frontend)  │
└──────────┬──────────┘
           │
           │ HTTP Requests (axios)
           │ POST /upload
           │ GET /jobs/{id}
           │ GET /results/{id}/video
           │ GET /results/{id}/heatmap
           │ GET /results/{id}/alerts
           ▼
┌─────────────────────┐
│   Backend Server    │
│  localhost:8000     │
│   (FastAPI API)     │
└──────────┬──────────┘
           │
           │ Processes videos
           │ Runs AI detection
           │ Stores results
           ▼
┌─────────────────────┐
│   File System       │
│  data/videos/       │
│  data/heatmaps/     │
│  data/alerts/       │
└─────────────────────┘
```

---

## Connection Configuration

### Frontend → Backend
**File:** `frontend/src/services/api.ts`

```typescript
// Line 8: API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
```

The frontend automatically connects to your backend at `http://localhost:8000/api/v1`.

### CORS (Cross-Origin Resource Sharing)
**File:** `backend/api/main.py` (Lines 53-59)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows frontend at localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This allows the frontend (port 5173) to make requests to the backend (port 8000).

---

## Available Features

### Week 1-2 Features (Already in Frontend)
- ✅ Video upload
- ✅ Job status monitoring
- ✅ Event timeline
- ✅ Processed video playback

### Week 3 Features (Backend Ready, Frontend Needs Update)
- ⏳ Heatmap visualization (API ready at `/results/{id}/heatmap`)
- ⏳ Alert notifications (API ready at `/results/{id}/alerts`)
- ⏳ Fall detection display
- ⏳ Fight detection display

---

## Testing the Connection

### 1. Open Frontend
Open your browser to: **http://localhost:5173**

You should see the SentinelAI dashboard.

### 2. Upload a Video
1. Click "Upload Video" or similar button
2. Select a video file (MP4, AVI, MOV, or MKV)
3. The frontend will send a POST request to `http://localhost:8000/api/v1/upload`

### 3. Monitor Processing
The frontend polls the backend API every few seconds:
```
GET http://localhost:8000/api/v1/jobs/{job_id}
```

### 4. View Results
When complete, the frontend fetches:
- **Processed video:** `GET /results/{job_id}/video`
- **Events JSON:** `GET /results/{job_id}/events`
- **Heatmap (Week 3):** `GET /results/{job_id}/heatmap`
- **Alerts (Week 3):** `GET /results/{job_id}/alerts`

---

## API Endpoints Used by Frontend

### Upload
```typescript
POST /api/v1/upload
Content-Type: multipart/form-data

Returns: { job_id: string, filename: string, status: string }
```

### Job Status
```typescript
GET /api/v1/jobs/{job_id}

Returns: {
  id: string,
  filename: string,
  status: "queued" | "processing" | "completed" | "failed",
  progress: number,
  created_at: string,
  completed_at: string | null
}
```

### List Jobs
```typescript
GET /api/v1/jobs?skip=0&limit=20&status=completed

Returns: {
  jobs: Job[],
  total: number,
  skip: number,
  limit: number
}
```

### Download Video
```typescript
GET /api/v1/results/{job_id}/video

Returns: video file (MP4)
```

### Get Events
```typescript
GET /api/v1/results/{job_id}/events

Returns: {
  events: [
    {
      event_type: "action_change",
      action: "walking" | "running" | "standing" | "loitering" | "fallen",
      track_id: number,
      timestamp: number,
      frame_number: number,
      confidence: number
    }
  ],
  summary: {
    total_events: number,
    actions_detected: string[],
    unique_people: number
  }
}
```

### Get Heatmap (Week 3) 🆕
```typescript
GET /api/v1/results/{job_id}/heatmap

Returns: PNG image file
```

### Get Alerts (Week 3) 🆕
```typescript
GET /api/v1/results/{job_id}/alerts

Returns: {
  summary: {
    total_alerts: number,
    by_severity: {
      critical: number,
      high: number,
      medium: number,
      low: number
    },
    by_type: {
      fall_detected: number,
      fight_detected: number,
      prolonged_loitering: number,
      crowd_detected: number
    }
  },
  alerts: [
    {
      id: string,
      alert_type: string,
      severity: "critical" | "high" | "medium" | "low",
      message: string,
      timestamp: string,
      frame_id: number,
      track_ids: number[]
    }
  ]
}
```

---

## Network Flow Example

When you upload a video:

1. **Frontend sends file:**
   ```
   Browser → POST http://localhost:8000/api/v1/upload
   ```

2. **Backend creates job:**
   ```
   Backend → Saves to data/uploads/
   Backend → Creates database record
   Backend → Returns job_id
   ```

3. **Frontend polls status:**
   ```
   Browser → GET http://localhost:8000/api/v1/jobs/{job_id}
   (Every 2 seconds until status = "completed")
   ```

4. **Backend processes video:**
   ```
   Backend → YOLOv8 detection
   Backend → ByteTrack tracking
   Backend → Fall/Fight detection
   Backend → Heatmap generation
   Backend → Alert generation
   Backend → Saves results to data/
   ```

5. **Frontend fetches results:**
   ```
   Browser → GET http://localhost:8000/api/v1/results/{job_id}/video
   Browser → GET http://localhost:8000/api/v1/results/{job_id}/events
   Browser → GET http://localhost:8000/api/v1/results/{job_id}/heatmap
   Browser → GET http://localhost:8000/api/v1/results/{job_id}/alerts
   ```

---

## Browser DevTools Inspection

You can see the API calls in action:

1. Open your browser to http://localhost:5173
2. Press F12 to open DevTools
3. Go to the "Network" tab
4. Upload a video
5. You'll see requests to `localhost:8000/api/v1/...`

Example requests you'll see:
```
POST   http://localhost:8000/api/v1/upload          (Upload)
GET    http://localhost:8000/api/v1/jobs/abc123...  (Status check)
GET    http://localhost:8000/api/v1/jobs/abc123...  (Status check)
GET    http://localhost:8000/api/v1/jobs/abc123...  (Status check)
GET    http://localhost:8000/api/v1/results/abc123.../events
GET    http://localhost:8000/api/v1/results/abc123.../video
GET    http://localhost:8000/api/v1/results/abc123.../heatmap
GET    http://localhost:8000/api/v1/results/abc123.../alerts
```

---

## Adding Week 3 Features to Frontend

The backend API is ready for Week 3 features. To display them in the frontend, you need to:

### 1. Add Heatmap Viewer Component

**Create:** `frontend/src/components/HeatmapViewer.tsx`

```typescript
interface HeatmapViewerProps {
  jobId: string;
}

export function HeatmapViewer({ jobId }: HeatmapViewerProps) {
  const heatmapUrl = `http://localhost:8000/api/v1/results/${jobId}/heatmap`;

  return (
    <div className="heatmap-viewer">
      <h3>Activity Heatmap</h3>
      <img
        src={heatmapUrl}
        alt="Activity Heatmap"
        style={{ width: '100%', maxWidth: '800px' }}
      />
      <p className="text-muted">
        Red/yellow areas show high activity zones
      </p>
    </div>
  );
}
```

### 2. Add Alerts Panel Component

**Create:** `frontend/src/components/AlertsPanel.tsx`

```typescript
import { useQuery } from '@tanstack/react-query';
import { getAlerts } from '../services/api';

interface AlertsPanelProps {
  jobId: string;
}

export function AlertsPanel({ jobId }: AlertsPanelProps) {
  const { data: alertsData } = useQuery(
    ['alerts', jobId],
    () => getAlerts(jobId)
  );

  if (!alertsData) return <div>Loading alerts...</div>;

  const { summary, alerts } = alertsData;

  return (
    <div className="alerts-panel">
      <h3>Alerts ({summary.total_alerts})</h3>

      {/* Summary Cards */}
      <div className="alert-summary">
        <div className="alert-stat critical">
          Critical: {summary.by_severity.critical}
        </div>
        <div className="alert-stat high">
          High: {summary.by_severity.high}
        </div>
        <div className="alert-stat medium">
          Medium: {summary.by_severity.medium}
        </div>
      </div>

      {/* Alert List */}
      <div className="alert-list">
        {alerts.map(alert => (
          <div key={alert.id} className={`alert-card ${alert.severity}`}>
            <div className="alert-header">
              <span className="alert-type">{alert.alert_type}</span>
              <span className="alert-severity">{alert.severity}</span>
            </div>
            <p className="alert-message">{alert.message}</p>
            <small className="alert-timestamp">
              {new Date(alert.timestamp).toLocaleString()}
            </small>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 3. Update API Service

**Add to:** `frontend/src/services/api.ts`

```typescript
/**
 * Get heatmap URL for a job
 */
export const getHeatmapUrl = (jobId: string): string => {
  return `${API_BASE_URL}/results/${jobId}/heatmap`;
};

/**
 * Get alerts for a job
 */
export const getAlerts = async (jobId: string): Promise<any> => {
  const response = await api.get(`/results/${jobId}/alerts`);
  return response.data;
};
```

### 4. Update Results Page

**Modify:** `frontend/src/pages/ResultsPage.tsx`

Add the new components to display heatmaps and alerts alongside the existing video and events.

---

## Troubleshooting

### Frontend can't connect to backend
**Error:** `Network Error` or `ERR_CONNECTION_REFUSED`

**Solutions:**
1. Make sure backend is running at http://localhost:8000
2. Check backend console for errors
3. Verify CORS is enabled in `backend/api/main.py`

### CORS errors in browser console
**Error:** `Access to XMLHttpRequest has been blocked by CORS policy`

**Solution:** Backend already has CORS enabled for all origins (`allow_origins=["*"]`)

### 404 Not Found on API endpoints
**Error:** `404 Not Found` for `/api/v1/...` routes

**Solution:**
- Verify backend is running
- Check that routes are registered in `backend/api/main.py` (lines 84-86)
- Visit http://localhost:8000/api/docs to see all available routes

---

## Summary

**Backend (http://localhost:8000):**
- Processes videos
- Runs AI detection (YOLOv8, fall detection, fight detection)
- Generates heatmaps and alerts
- Stores results
- Provides REST API

**Frontend (http://localhost:5173):**
- User interface
- Uploads videos to backend
- Polls backend for status
- Displays results (video, events, heatmaps, alerts)

**Connection:**
- Frontend uses `axios` to make HTTP requests to backend API
- Backend allows CORS from all origins
- Data flows: User → Frontend → Backend → AI Processing → Results → Frontend → User

---

**Both servers are now running and connected!**

- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs

Open http://localhost:5173 in your browser to start using the system!
