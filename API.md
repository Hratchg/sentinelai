# SentinelAI API Documentation

**Version**: 0.1.0
**Base URL**: `http://localhost:8000/api/v1`
**Interactive Docs**: `http://localhost:8000/api/docs` (Swagger UI)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
   - [Upload Video](#upload-video)
   - [Get Job Status](#get-job-status)
   - [List Jobs](#list-jobs)
   - [Delete Job](#delete-job)
   - [Get Result Video](#get-result-video)
   - [Get Result Events](#get-result-events)
4. [Request/Response Models](#requestresponse-models)
5. [Error Handling](#error-handling)
6. [Code Examples](#code-examples)

---

## Quick Start

### 1. Start the API Server

```bash
cd backend
python -m backend.api.main

# Or use uvicorn directly
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Upload a Video

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/video.mp4"
```

### 3. Check Job Status

```bash
curl "http://localhost:8000/api/v1/jobs/{job_id}"
```

### 4. Download Results

```bash
# Get processed video
curl "http://localhost:8000/api/v1/results/{job_id}/video" -o processed_video.mp4

# Get events JSON
curl "http://localhost:8000/api/v1/results/{job_id}/events"
```

---

## Authentication

**Current Status**: No authentication required (development mode)

**Future**: JWT-based authentication will be added in Phase 5
- Bearer token authentication
- API key support
- Role-based access control (RBAC)

---

## Endpoints

### Upload Video

Upload a video file for processing.

**Endpoint**: `POST /api/v1/upload`

**Request**:
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file` (required): Video file to upload

**Supported Formats**: MP4, AVI, MOV, MKV
**Max File Size**: 100 MB

**Response** (201 Created):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "surveillance_video.mp4",
  "status": "queued",
  "message": "Video uploaded successfully and queued for processing"
}
```

**Errors**:
- `400 Bad Request`: Invalid file format or size exceeded
- `500 Internal Server Error`: Server error during upload

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@surveillance_video.mp4"
```

---

### Get Job Status

Get the current status of a processing job.

**Endpoint**: `GET /api/v1/jobs/{job_id}`

**Path Parameters**:
- `job_id` (required): Unique job identifier (UUID)

**Response** (200 OK):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "surveillance_video.mp4",
  "status": "processing",
  "progress": 45.5,
  "created_at": "2025-01-16T10:30:00Z",
  "updated_at": "2025-01-16T10:31:30Z",
  "completed_at": null,
  "error_message": null
}
```

**Status Values**:
- `queued`: Job is waiting in the queue
- `processing`: Job is currently being processed
- `completed`: Job finished successfully
- `failed`: Job failed due to an error

**Errors**:
- `404 Not Found`: Job ID not found
- `500 Internal Server Error`: Server error

**Example**:
```bash
curl "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000"
```

**Polling Pattern**:
```bash
# Poll every 2 seconds until complete
while true; do
  STATUS=$(curl -s "http://localhost:8000/api/v1/jobs/{job_id}" | jq -r '.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  sleep 2
done
```

---

### List Jobs

List all jobs with pagination and optional filtering.

**Endpoint**: `GET /api/v1/jobs`

**Query Parameters**:
- `skip` (optional): Number of jobs to skip for pagination (default: 0)
- `limit` (optional): Maximum number of jobs to return (default: 20, max: 100)
- `status` (optional): Filter by status (`queued`, `processing`, `completed`, `failed`)

**Response** (200 OK):
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "video1.mp4",
      "status": "completed",
      "progress": 100.0,
      "created_at": "2025-01-16T10:30:00Z",
      "updated_at": "2025-01-16T10:32:00Z",
      "completed_at": "2025-01-16T10:32:00Z",
      "error_message": null
    },
    {
      "job_id": "660e9511-f39c-52e5-b827-557766551111",
      "filename": "video2.mp4",
      "status": "processing",
      "progress": 67.2,
      "created_at": "2025-01-16T10:35:00Z",
      "updated_at": "2025-01-16T10:36:30Z",
      "completed_at": null,
      "error_message": null
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

**Errors**:
- `400 Bad Request`: Invalid status filter
- `500 Internal Server Error`: Server error

**Examples**:
```bash
# Get first 20 jobs
curl "http://localhost:8000/api/v1/jobs?skip=0&limit=20"

# Get all completed jobs
curl "http://localhost:8000/api/v1/jobs?status=completed"

# Get next 20 jobs (pagination)
curl "http://localhost:8000/api/v1/jobs?skip=20&limit=20"

# Get only processing jobs
curl "http://localhost:8000/api/v1/jobs?status=processing&limit=10"
```

---

### Delete Job

Delete a job and its associated files.

**Endpoint**: `DELETE /api/v1/jobs/{job_id}`

**Path Parameters**:
- `job_id` (required): Unique job identifier

**Response** (204 No Content):
No response body

**Errors**:
- `404 Not Found`: Job ID not found
- `500 Internal Server Error`: Server error

**Example**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000"
```

**Warning**: This action is irreversible. All job data and results will be permanently deleted.

---

### Get Result Video

Download the processed video with annotations.

**Endpoint**: `GET /api/v1/results/{job_id}/video`

**Path Parameters**:
- `job_id` (required): Unique job identifier

**Response** (200 OK):
- **Content-Type**: `video/mp4`
- **Body**: Binary video file with annotations

**Requirements**:
- Job status must be `completed`
- Output video file must exist

**Errors**:
- `404 Not Found`: Job not found, not ready, or video file missing
- `500 Internal Server Error`: Server error

**Example**:
```bash
# Download with original filename
curl "http://localhost:8000/api/v1/results/{job_id}/video" -o processed_video.mp4

# Stream to video player
curl "http://localhost:8000/api/v1/results/{job_id}/video" | mpv -
```

---

### Get Result Events

Get the events JSON with action detections.

**Endpoint**: `GET /api/v1/results/{job_id}/events`

**Path Parameters**:
- `job_id` (required): Unique job identifier

**Response** (200 OK):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_info": {
    "filename": "surveillance_video.mp4",
    "duration": 30.5,
    "fps": 30,
    "resolution": [1920, 1080],
    "total_frames": 915
  },
  "events": [
    {
      "frame_id": 123,
      "timestamp": 4.1,
      "track_id": 5,
      "action": "walking",
      "confidence": 0.87,
      "bbox": [320.5, 180.2, 425.8, 450.6],
      "velocity": 8.3
    },
    {
      "frame_id": 234,
      "timestamp": 7.8,
      "track_id": 5,
      "action": "standing",
      "confidence": 0.92,
      "bbox": [318.2, 179.5, 423.1, 448.9],
      "velocity": 0.8
    }
  ],
  "summary": {
    "total_events": 24,
    "unique_tracks": 3,
    "actions": {
      "walking": 15,
      "standing": 6,
      "running": 2,
      "loitering": 1
    }
  }
}
```

**Event Fields**:
- `frame_id`: Frame number where action occurred
- `timestamp`: Time in video (seconds)
- `track_id`: Unique person identifier (consistent across frames)
- `action`: Detected action (`standing`, `walking`, `running`, `loitering`)
- `confidence`: Action confidence score (0.0 - 1.0)
- `bbox`: Bounding box `[x1, y1, x2, y2]` in pixels
- `velocity`: Person velocity in pixels per frame

**Requirements**:
- Job status must be `completed`
- Events JSON file must exist

**Errors**:
- `404 Not Found`: Job not found, not ready, or events file missing
- `500 Internal Server Error`: Server error or JSON parse error

**Example**:
```bash
# Get events
curl "http://localhost:8000/api/v1/results/{job_id}/events"

# Save to file
curl "http://localhost:8000/api/v1/results/{job_id}/events" -o events.json

# Pretty print with jq
curl "http://localhost:8000/api/v1/results/{job_id}/events" | jq '.'
```

---

## Request/Response Models

### UploadResponse
```json
{
  "job_id": "string (UUID)",
  "filename": "string",
  "status": "queued | processing | completed | failed",
  "message": "string"
}
```

### JobResponse
```json
{
  "job_id": "string (UUID)",
  "filename": "string",
  "status": "queued | processing | completed | failed",
  "progress": 0.0-100.0,
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)",
  "completed_at": "datetime (ISO 8601) | null",
  "error_message": "string | null"
}
```

### EventData
```json
{
  "frame_id": "integer",
  "timestamp": "float (seconds)",
  "track_id": "integer",
  "action": "standing | walking | running | loitering",
  "confidence": 0.0-1.0,
  "bbox": [x1, y1, x2, y2],
  "velocity": "float (pixels/frame)"
}
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "ErrorType",
  "message": "Human-readable error message",
  "details": {
    "additional": "context"
  }
}
```

### Common Error Types

**ValidationError** (400):
```json
{
  "error": "ValidationError",
  "message": "Invalid file format. Only MP4, AVI, and MOV are supported.",
  "details": {
    "supported_formats": ["mp4", "avi", "mov", "mkv"]
  }
}
```

**NotFound** (404):
```json
{
  "error": "NotFound",
  "message": "Job 550e8400-e29b-41d4-a716-446655440000 not found",
  "details": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**NotReady** (404):
```json
{
  "error": "NotReady",
  "message": "Video not ready. Job status: processing",
  "details": {
    "status": "processing",
    "progress": 45.5
  }
}
```

**InternalError** (500):
```json
{
  "error": "InternalError",
  "message": "Failed to process video",
  "details": {
    "error": "Detailed error message"
  }
}
```

---

## Code Examples

### Python (requests)

```python
import requests
import time

# Upload video
with open('video.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/upload',
        files={'file': f}
    )
    job_id = response.json()['job_id']
    print(f"Job ID: {job_id}")

# Poll for completion
while True:
    response = requests.get(f'http://localhost:8000/api/v1/jobs/{job_id}')
    job = response.json()
    print(f"Status: {job['status']}, Progress: {job['progress']}%")

    if job['status'] in ['completed', 'failed']:
        break

    time.sleep(2)

# Download results if completed
if job['status'] == 'completed':
    # Get video
    video_response = requests.get(
        f'http://localhost:8000/api/v1/results/{job_id}/video'
    )
    with open('processed.mp4', 'wb') as f:
        f.write(video_response.content)

    # Get events
    events_response = requests.get(
        f'http://localhost:8000/api/v1/results/{job_id}/events'
    )
    events = events_response.json()
    print(f"Total events: {events['summary']['total_events']}")
```

### JavaScript (fetch)

```javascript
// Upload video
async function uploadVideo(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/api/v1/upload', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  return data.job_id;
}

// Poll for completion
async function pollJobStatus(jobId) {
  while (true) {
    const response = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}`);
    const job = await response.json();

    console.log(`Status: ${job.status}, Progress: ${job.progress}%`);

    if (job.status === 'completed' || job.status === 'failed') {
      return job;
    }

    await new Promise(resolve => setTimeout(resolve, 2000));
  }
}

// Get events
async function getEvents(jobId) {
  const response = await fetch(
    `http://localhost:8000/api/v1/results/${jobId}/events`
  );
  return await response.json();
}

// Usage
const jobId = await uploadVideo(videoFile);
const job = await pollJobStatus(jobId);
if (job.status === 'completed') {
  const events = await getEvents(jobId);
  console.log('Events:', events);
}
```

### curl (Bash)

```bash
#!/bin/bash

# Upload video
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@video.mp4")

JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"

# Poll for completion
while true; do
  JOB=$(curl -s "http://localhost:8000/api/v1/jobs/$JOB_ID")
  STATUS=$(echo $JOB | jq -r '.status')
  PROGRESS=$(echo $JOB | jq -r '.progress')

  echo "Status: $STATUS, Progress: $PROGRESS%"

  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi

  sleep 2
done

# Download results if completed
if [ "$STATUS" = "completed" ]; then
  curl "http://localhost:8000/api/v1/results/$JOB_ID/video" -o processed.mp4
  curl "http://localhost:8000/api/v1/results/$JOB_ID/events" -o events.json
  echo "Results downloaded"
fi
```

---

## Rate Limiting

**Current Status**: No rate limiting (development mode)

**Future**: Rate limiting will be added in Phase 5
- 100 requests per minute per IP
- 1000 requests per hour per API key
- Exponential backoff for retry logic

---

## Webhooks (Future)

**Status**: Planned for Phase 3

Receive notifications when jobs complete:

```json
{
  "event": "job.completed",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "timestamp": "2025-01-16T10:32:00Z",
  "results": {
    "video_url": "/api/v1/results/{job_id}/video",
    "events_url": "/api/v1/results/{job_id}/events"
  }
}
```

---

## Interactive API Docs

Visit `http://localhost:8000/api/docs` for interactive Swagger UI documentation where you can:
- Explore all endpoints
- Test API calls directly from the browser
- View request/response schemas
- See example requests and responses

Alternative: `http://localhost:8000/api/redoc` for ReDoc documentation

---

**Last Updated**: January 16, 2025
**Version**: 0.1.0
**Support**: See [README.md](README.md) for more information
