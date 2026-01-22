# Week 4: Real-Time Conversational Surveillance - Implementation Progress

**Status:** Phase 1 Complete (Core Backend Components) ✅
**Date:** 2026-01-18

---

## What We're Building

A **real-time conversational surveillance assistant** that:
- Uses live webcam feed (not video uploads)
- Remembers faces with auto-assigned IDs
- Learns custom gestures on the fly
- Extracts names from audio ("Hi, I'm John")
- Answers questions via LLM ("When did I last see Sarah?")
- Shows video evidence in responses

---

## Completed Components ✅

### 1. Database Schema
**File:** [backend/storage/models.py](backend/storage/models.py)

Four new tables created:
```sql
- persons (face embeddings, names, timestamps, appearances)
- person_events (action logs, detections)
- gesture_templates (learned gestures with DTW matching)
- event_clips (video clip references)
```

**Migration:** [backend/storage/migrate_realtime.py](backend/storage/migrate_realtime.py)

### 2. CRUD Operations
**File:** [backend/storage/crud.py](backend/storage/crud.py)

Added operations for:
- Person management (create, get, update name, update last_seen)
- Event logging (create events, get person history)
- Gesture templates (create, get all, update detection counts)
- Event clips (create, get by person, get recent)

### 3. Face Recognition Engine
**File:** [backend/core/face_recognition.py](backend/core/face_recognition.py)

**Features:**
- DeepFace + Facenet512 (512-d embeddings)
- Cosine similarity matching (threshold: 0.6)
- Auto-assign person IDs (e.g., "Person_A47B8C12")
- Serialize/deserialize for database storage

**Key Methods:**
```python
extract_face_embedding(frame, bbox) -> np.ndarray
find_matching_identity(embedding, known_faces) -> person_id
verify_faces(embedding1, embedding2) -> (is_match, similarity)
```

### 4. Camera Stream Manager
**File:** [backend/core/camera_stream.py](backend/core/camera_stream.py)

**Features:**
- Multi-camera support (configurable IDs)
- 30 FPS capture with frame rate limiting
- Rolling frame buffer (5 seconds = 150 frames)
- Real-time FPS monitoring
- Async callback integration

**Usage:**
```python
camera = CameraStreamManager(camera_ids=[0])
camera.start_stream(0, frame_callback=async_process_frame)
```

### 5. Event Clip Recorder
**File:** [backend/core/clip_recorder.py](backend/core/clip_recorder.py)

**Features:**
- Event-based recording (not 24/7)
- H.264 compression
- Rolling buffer (captures 5 seconds before event)
- Auto-generates clips on events

**Triggers:**
- Person first appears
- Gesture detected
- Voice detected

**Storage:** ~180 MB/day (90 clips × 2 MB)

### 6. Audio Processor
**File:** [backend/core/audio_processor.py](backend/core/audio_processor.py)

**Features:**
- Whisper speech-to-text (base model)
- spaCy Named Entity Recognition
- Real-time microphone capture
- Pattern matching for names

**Patterns Detected:**
```
"I'm John" → John
"My name is Sarah" → Sarah
"This is Michael" → Michael
"Call me Alex" → Alex
```

### 7. Gesture Learner
**File:** [backend/core/gesture_learner.py](backend/core/gesture_learner.py)

**Features:**
- MediaPipe Pose (33 body landmarks)
- Dynamic Time Warping (DTW) for matching
- Self-learning (unlimited gestures)
- Confidence scoring

**Workflow:**
1. Record pose sequence (30 frames)
2. Save to database with label
3. Match future sequences via DTW
4. Return (gesture_name, confidence)

---

## Pending Components (Next Steps)

### Backend
1. **Real-Time Pipeline** - Orchestrates all components
2. **WebSocket Handler** - Live streaming to frontend
3. **LLM Query Engine** - Claude-powered Q&A
4. **Chat API** - `/api/v1/chat` endpoint
5. **Gesture API** - `/api/v1/gestures/teach` endpoint
6. **Cleanup Worker** - Auto-delete old data

### Frontend
1. **LiveCamera** - WebSocket video display
2. **ChatInterface** - Q&A with video playback
3. **GestureTeacher** - Record & name gestures
4. **SystemHealth** - Storage monitoring

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│           FRONTEND (React)                   │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Live Camera  │  │ Chat + Video Clips   │ │
│  └──────────────┘  └──────────────────────┘ │
└──────────────┬──────────────────────────────┘
               │ WebSocket
┌──────────────┼──────────────────────────────┐
│         BACKEND (FastAPI)                    │
│  ┌───────────────────────────────────────┐  │
│  │     Real-Time Pipeline                │  │
│  │  Camera → Detector → Tracker          │  │
│  │     ↓         ↓         ↓             │  │
│  │  Face Rec  Gesture  Audio Name        │  │
│  │     ↓         ↓         ↓             │  │
│  │  Event Logging + Clip Recording       │  │
│  └───────────────────────────────────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │   LLM Query Engine (Claude)           │  │
│  │   Context Retrieval → Answer + Clips  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────┬───────────────────────┘
                      │
                ┌─────┴─────┐
                │  SQLite   │
                │  Persons  │
                │  Events   │
                │  Gestures │
                └───────────┘
```

---

## Key Technical Decisions

### Face Recognition
- **Model:** Facenet512 (512-d embeddings)
- **Threshold:** 0.6 cosine similarity
- **ID Format:** "Person_<HASH>" (e.g., "Person_A47B8C12")

### Gesture Recognition
- **Landmarks:** 33 body points × 3 coords = 99-d features
- **Sequence:** 30 frames (~1 second @ 30 FPS)
- **Matching:** DTW distance → confidence score

### Audio Processing
- **STT:** Whisper base model (16kHz)
- **NER:** spaCy en_core_web_sm
- **Buffer:** 10 seconds of audio

### Video Clips
- **Codec:** H.264
- **Duration:** 5-10 seconds per clip
- **Retention:** 30 days (configurable)
- **Storage:** ~5.4 GB/month

---

## Database Statistics (Projected)

### 24/7 Surveillance with 1 Camera

| Component | Daily | Monthly | Yearly |
|-----------|-------|---------|--------|
| Face embeddings | 160 KB | 4.8 MB | 58 MB |
| Events | 244 KB | 7.3 MB | 89 MB |
| Gestures | - | 500 KB | 6 MB |
| **Database Total** | **404 KB** | **12.6 MB** | **153 MB** |
| **Video clips (30d)** | 180 MB | **5.4 GB** | - |
| **Grand Total** | 180 MB | **~5.5 GB** | **153 MB + clips** |

---

## Dependencies Added

```txt
# Face Recognition
deepface>=0.0.79
tf-keras>=2.16.0

# Audio Processing
openai-whisper>=20231117
spacy>=3.7.0

# Gesture Recognition
mediapipe>=0.10.0
dtaidistance>=2.3.10

# LLM Integration
anthropic>=0.18.0

# Real-Time Streaming
websockets>=12.0
```

---

## Example User Interactions (Planned)

### Conversation 1: Identity Recognition
```
User: "Who is that person on camera?"
AI: "I don't recognize this person yet. Would you like me to remember them?"

[Person says "Hi, I'm Michael"]
AI: "Name detected: Michael. Saving face profile."

[Next day, Michael returns]
User: "Who just came in?"
AI: "That's Michael. He last visited yesterday at 2:30 PM."
    [Shows 7-second video clip of Michael entering]
```

### Conversation 2: Gesture Teaching
```
User: "Teach this gesture as 'peace sign'"
AI: "Recording... Please hold the gesture for 1 second."
AI: "Gesture 'peace sign' saved! I'll recognize it from now on."

[Later, person makes peace sign]
AI: "Michael is making a peace sign (confidence: 87%)"
```

### Conversation 3: Historical Queries
```
User: "When did I last see Sarah?"
AI: "I last saw Sarah today at 11:42 AM. She waved at the camera."
    [Shows video clip of Sarah waving]

User: "Show me all times Sarah visited this week"
AI: "Sarah visited 3 times this week:
     1. Monday 9:15 AM - arrived
     2. Wednesday 2:30 PM - brief visit
     3. Friday 11:00 AM - meeting"
    [Shows 3 video clips]
```

---

## Next Implementation Phase

### Priority 1: Core Pipeline (Days 1-3)
1. Real-time processing pipeline
2. WebSocket handler
3. Basic integration testing

### Priority 2: LLM Interface (Days 4-6)
1. LLM query engine
2. Chat API endpoint
3. Context retrieval optimization

### Priority 3: Frontend (Days 7-10)
1. LiveCamera component
2. ChatInterface with video playback
3. GestureTeacher UI
4. SystemHealth dashboard

---

## Performance Targets

| Hardware | Target FPS | Expected |
|----------|-----------|----------|
| CPU (i7) | 8-12 FPS | ~10 FPS |
| GPU (T4) | 40-60 FPS | ~45 FPS |
| GPU (RTX 4090) | 100+ FPS | ~120 FPS |

**Bottleneck:** YOLOv8 detection (~35ms/frame)
**Week 4 Overhead:** <5ms/frame (face rec + gesture + audio)

---

## File Structure Created

```
backend/
├── core/
│   ├── face_recognition.py      ✅ 300 lines
│   ├── camera_stream.py         ✅ 250 lines
│   ├── clip_recorder.py         ✅ 200 lines
│   ├── audio_processor.py       ✅ 250 lines
│   ├── gesture_learner.py       ✅ 300 lines
│   └── realtime_pipeline.py     🚧 Pending
├── storage/
│   ├── models.py                ✅ Updated (4 new models)
│   ├── crud.py                  ✅ Updated (100+ new lines)
│   └── migrate_realtime.py      ✅ Migration script
└── api/
    ├── websocket.py             🚧 Pending
    └── routes/
        ├── chat.py              🚧 Pending
        └── gestures.py          🚧 Pending
```

---

## Status Summary

**Completed:** 7 / 18 tasks (39%)
**Lines of Code:** ~1,300 backend lines
**Estimated Completion:** 3-4 more days for full backend + frontend

---

**Built with Claude Sonnet 4.5** 🚀
