# SentinelAI Roadmap

## Current Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | Complete | Real-Time Camera Pipeline + Voice Activation |
| Phase 2 | Complete | LLM-Powered Conversational Interface |
| Phase 3 | Pending | Audio Name Extraction + Gesture Learning |
| Phase 4 | Pending | Polish & Production Ready |
| Phase 5 | Planned | Multi-Device Support & Mobile Apps |

---

## Phase 1: Real-Time Camera Pipeline (COMPLETE)

### Features Implemented
- WebSocket-based live camera streaming
- JWT authentication for secure connections
- "Hey Sentinel" wake word detection
- Voice command processing via Web Speech API
- Multi-tenant user isolation
- Auto-reconnection on disconnect

### Files Modified
- `backend/api/websocket.py` - WebSocket handler with auth
- `backend/core/camera_stream.py` - Camera capture manager
- `frontend/src/hooks/useVoiceControl.ts` - Voice control hook
- `frontend/src/components/VoiceControl.tsx` - Voice UI
- `frontend/src/components/LiveCamera.tsx` - Camera display

---

## Phase 2: LLM-Powered Interface (COMPLETE)

### Features Implemented
- Claude API integration (claude-3-5-sonnet)
- Intelligent context retrieval from database
- Person name extraction and matching
- Time-aware responses ("5 minutes ago")
- Video clip attachment to responses
- Dark theme chat interface

### Files Modified
- `backend/llm/query_engine.py` - LLM query engine
- `frontend/src/components/ChatInterface.tsx` - Chat UI

---

## Phase 3: Audio Name Extraction + Gesture Learning (PENDING)

### Planned Features
- **Audio Name Extraction**
  - Whisper-based speech-to-text
  - Name detection from conversations
  - Auto-associate names with detected faces

- **Gesture Learning**
  - Record custom gestures
  - Train gesture recognition model
  - Trigger actions on gesture detection

### Estimated Effort
3-4 days

---

## Phase 4: Polish & Production Ready (PENDING)

### Planned Features
- Error handling improvements
- Performance optimization
- Security hardening
- Deployment documentation
- Unit and integration tests

### Estimated Effort
2-3 days

---

## Phase 5: Multi-Device Support & Mobile Apps (PLANNED)

### Overview
Enable users to access SentinelAI from any device - phones, tablets, TVs, and custom home security integrations.

### Planned Features

#### 5.1 Mobile Apps
- **iOS App** (Swift/SwiftUI)
  - Live camera viewing
  - Push notifications for events
  - Voice commands via Siri integration
  - Face ID authentication

- **Android App** (Kotlin/Jetpack Compose)
  - Live camera viewing
  - Push notifications via Firebase
  - Voice commands via Google Assistant
  - Biometric authentication

#### 5.2 Smart TV Apps
- **Apple TV** - tvOS app for big-screen viewing
- **Fire TV / Roku** - Living room monitoring
- **Android TV** - Native TV experience

#### 5.3 Web Progressive App (PWA)
- Install on any device with a browser
- Offline support for cached data
- Push notifications
- Home screen icon

#### 5.4 API Integrations
- **Home Assistant** - Smart home integration
- **HomeKit** - Apple ecosystem support
- **Google Home** - Voice control integration
- **IFTTT** - Custom automation triggers

#### 5.5 Device Management
- Device registration and authentication
- Per-device permissions
- Remote device logout
- Activity logging per device

### Architecture Components

```
                    ┌─────────────────────┐
                    │   SentinelAI API    │
                    │   (FastAPI Server)  │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
    ┌──────▼──────┐    ┌───────▼───────┐   ┌──────▼──────┐
    │  iOS App    │    │  Android App  │   │   Web PWA   │
    │  (Swift)    │    │   (Kotlin)    │   │   (React)   │
    └─────────────┘    └───────────────┘   └─────────────┘
           │                   │                   │
    ┌──────▼──────┐    ┌───────▼───────┐   ┌──────▼──────┐
    │  Apple TV   │    │   Fire TV     │   │  Smart TV   │
    │  (tvOS)     │    │   (Android)   │   │  Browsers   │
    └─────────────┘    └───────────────┘   └─────────────┘
```

### New Backend Endpoints

```python
# Device Management
POST   /api/v1/devices/register     # Register new device
GET    /api/v1/devices              # List user's devices
DELETE /api/v1/devices/{device_id}  # Remove device

# Push Notifications
POST   /api/v1/notifications/subscribe   # Subscribe to events
POST   /api/v1/notifications/send        # Send test notification

# Multi-Camera Support
GET    /api/v1/cameras              # List available cameras
POST   /api/v1/cameras              # Add new camera
GET    /api/v1/cameras/{id}/stream  # Get stream URL
```

### Database Schema Additions

```sql
-- Device registration
CREATE TABLE devices (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    device_name VARCHAR(255),
    device_type VARCHAR(50),  -- 'ios', 'android', 'tv', 'web'
    push_token VARCHAR(512),
    last_active TIMESTAMP,
    created_at TIMESTAMP
);

-- Notification preferences
CREATE TABLE notification_settings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    device_id UUID REFERENCES devices(id),
    event_type VARCHAR(50),
    enabled BOOLEAN DEFAULT true
);
```

### Estimated Effort
2-3 weeks for full implementation

### Priority Order
1. Web PWA (fastest to implement, works everywhere)
2. iOS App (largest mobile market share)
3. Android App
4. Smart TV apps

---

## Future Ideas (Backlog)

### Analytics Dashboard
- Person visit frequency charts
- Heat maps of activity
- Time-based activity patterns

### Advanced AI Features
- Anomaly detection (unusual behavior)
- Crowd counting
- Vehicle detection and tracking
- License plate recognition

### Cloud Integration
- Cloud backup of clips
- Multi-location support
- Remote access without port forwarding

### Privacy Features
- Face blurring for non-registered persons
- Automatic clip deletion policies
- GDPR compliance tools

---

## Contributing

Want to help build SentinelAI? Here's how:

1. Pick a feature from the roadmap
2. Create a branch: `feature/phase-X-feature-name`
3. Implement with tests
4. Submit a pull request

---

*Last Updated: January 2026*
