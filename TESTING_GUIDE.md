# SentinelAI Testing Guide - Phase 1 & Phase 2

## 🎯 What We're Testing

✅ **Phase 1**: Voice activation with "Hey Sentinel" wake word
✅ **Phase 2**: Real AI responses using Claude API (or stub mode)

---

## 📋 Pre-Test Checklist

### 1. Environment Setup

**Check `.env` file** (`backend/.env`):
```bash
# For Phase 1 only (stub mode):
CAMERA_IDS=0
VOICE_ENABLED=true

# For Phase 2 (real AI):
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx  # Uncomment and add your key
```

**Get Anthropic API Key** (for Phase 2):
1. Visit: https://console.anthropic.com/
2. Sign in or create account
3. Go to "API Keys" → "Create Key"
4. Copy key and add to `.env`

### 2. Browser Requirements

✅ **Recommended**: Chrome or Edge
⚠️ **Limited Support**: Safari
❌ **Not Supported**: Firefox (Web Speech API issues)

### 3. Microphone Permissions

Make sure your microphone is:
- ✅ Connected and working
- ✅ Not muted
- ✅ Set as default device (optional)

---

## 🚀 Starting the System

### Terminal 1: Backend

```powershell
cd C:\Users\hratc\sentinelai
python run.py
```

**Expected Output:**
```
INFO - Starting SentinelAI API server...
INFO - Database initialized successfully
INFO - Real-time pipeline initialized
INFO - Camera streams started: [0]
INFO - Application startup complete
INFO - Uvicorn running on http://0.0.0.0:8000
```

**Troubleshooting**:
- ❌ `ModuleNotFoundError`: Run `pip install -r requirements.txt`
- ❌ `Camera failed`: Check if webcam is in use by another app
- ❌ `Port 8000 in use`: Close other apps using port 8000

### Terminal 2: Frontend

```powershell
cd C:\Users\hratc\sentinelai\frontend
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Troubleshooting**:
- ❌ `npm: command not found`: Install Node.js from https://nodejs.org/
- ❌ `Dependencies not found`: Run `npm install`
- ❌ `Port 5173 in use`: Close other apps or use different port

---

## 🧪 Test Scenarios

### Test 1: Login & Dashboard Access

**Steps**:
1. Open browser: `http://localhost:5173`
2. You should see login page
3. If no account exists, click "Register"
4. Register with:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `password123`
5. Should redirect to dashboard

**Expected Result**:
- ✅ Dashboard loads with dark theme
- ✅ Left side: Live camera feed
- ✅ Right side: Chat interface with AI Assistant header
- ✅ Bottom-right: Voice Control component (microphone button)

**Troubleshooting**:
- ❌ Blank page: Check browser console (F12) for errors
- ❌ Login fails: Check backend is running on port 8000
- ❌ 404 errors: Verify both frontend and backend are running

---

### Test 2: Voice Control Activation (Phase 1)

**Steps**:
1. Click the **microphone icon** in bottom-right
2. Browser should prompt for microphone permission
3. Click **Allow**
4. Component should show:
   - Green pulsing dot
   - "Say 'Hey Sentinel' to activate"
   - Audio waveform animation

**Expected Result**:
- ✅ Microphone button turns red (recording)
- ✅ Waveform shows audio levels
- ✅ Status shows "Say 'Hey Sentinel' to activate"

**Troubleshooting**:
- ❌ "Voice control unavailable": Browser doesn't support Web Speech API
- ❌ "Microphone access denied": Check browser permissions
- ❌ No waveform: Check microphone is not muted

---

### Test 3: Wake Word Detection (Phase 1)

**Steps**:
1. With voice control active, say clearly: **"Hey Sentinel"**
2. Wait 1-2 seconds

**Expected Result**:
- ✅ Waveform turns **blue** (wake word detected)
- ✅ Status changes to "Listening for command..."
- ✅ Blue pulsing indicator appears

**Troubleshooting**:
- ❌ No detection: Speak louder or closer to microphone
- ❌ False positives: Adjust `WAKE_WORD_SENSITIVITY` in `.env` (lower = less sensitive)
- ❌ Audio level too low: Check microphone volume settings

---

### Test 4: Voice Command (Phase 1 - Stub Mode)

**Prerequisites**: No `ANTHROPIC_API_KEY` in `.env` (stub mode)

**Steps**:
1. Say: **"Hey Sentinel, who is on camera 1?"**
2. Wait for response

**Expected Result**:
- ✅ Question appears in chat (user message, blue bubble)
- ✅ AI response appears (assistant message, dark gray bubble)
- ✅ Response says: "I received your question: 'who is on camera 1?'. Voice command system is working! Full LLM integration with Claude API will be implemented in Phase 2..."

**Troubleshooting**:
- ❌ No response: Check WebSocket connection in browser console
- ❌ Connection error: Verify backend is running and JWT token is valid
- ❌ Error message: Check backend logs for errors

---

### Test 5: Voice Command (Phase 2 - Real AI)

**Prerequisites**: `ANTHROPIC_API_KEY` is set in `.env`

**Steps**:
1. Restart backend (if running): `Ctrl+C` then `python run.py`
2. Say: **"Hey Sentinel, who is on camera 1?"**
3. Wait for AI response (may take 2-5 seconds)

**Expected Result** (Empty Database):
```
AI: "System Status: No persons detected yet. Monitoring is active."
```

**Expected Result** (With Data):
```
AI: "I can see 2 people in the system:
     1. John Smith - last seen 5 minutes ago
     2. Sarah Johnson - last seen 2 hours ago"
     [Video clips may appear if available]
```

**Troubleshooting**:
- ❌ "Invalid API key": Check key in `.env` is correct
- ❌ API errors: Check https://status.anthropic.com/
- ❌ Slow responses: Normal for first request (model cold start)

---

### Test 6: Typed Chat (Phase 2)

**Steps**:
1. In the chat input box (bottom of right panel)
2. Type: **"Who is on camera 1?"**
3. Click **Send** or press **Enter**

**Expected Result**:
- ✅ Loading indicator (3 bouncing dots)
- ✅ AI response appears after 2-5 seconds
- ✅ Response is contextually relevant
- ✅ Timestamp shows below message

**Troubleshooting**:
- ❌ No response: Check backend logs for errors
- ❌ Error message: Likely API issue or database error

---

### Test 7: Video Clip Display (Phase 2)

**Note**: Only works if video clips exist in database

**Steps**:
1. Ask a question that should return clips: **"Show me recent activity"**
2. Wait for response

**Expected Result**:
- ✅ AI response includes video player(s)
- ✅ Video controls (play, pause, seek)
- ✅ Clip metadata below video (person name, event type, timestamp)

**Troubleshooting**:
- ❌ No clips: Database is empty (normal for new installation)
- ❌ Video won't play: Check clip file path in database
- ❌ 404 error: Clip file doesn't exist on disk

---

### Test 8: Multiple Conversations (Phase 2)

**Steps**:
1. Ask: **"Hey Sentinel, who is on camera 1?"**
2. Wait for response
3. Ask: **"When did I last see anyone?"**
4. Wait for response
5. Type in chat: **"What gestures have been detected?"**

**Expected Result**:
- ✅ All messages appear in chronological order
- ✅ Each response is relevant to its question
- ✅ Chat scrolls to bottom automatically
- ✅ Up to 10 voice responses stored

**Troubleshooting**:
- ❌ Out of order: Check timestamps
- ❌ Duplicate responses: May be a rendering issue, refresh page

---

### Test 9: WebSocket Reconnection (Phase 1)

**Steps**:
1. Stop the backend (`Ctrl+C`)
2. Observe frontend (camera feed should show "Disconnected")
3. Restart backend (`python run.py`)
4. Wait 3 seconds

**Expected Result**:
- ✅ Frontend automatically reconnects
- ✅ Status changes to "Connected"
- ✅ Camera feed resumes (if camera stream works)

**Troubleshooting**:
- ❌ No reconnection: Check browser console for errors
- ❌ Connection loop: Backend may be crashing, check logs

---

### Test 10: Multi-User Isolation (Phase 1 & 2)

**Steps**:
1. Open browser in **incognito/private mode**
2. Login with a **different account**
3. Ask a question in both windows

**Expected Result**:
- ✅ Each user sees only their own conversations
- ✅ No cross-user data leakage
- ✅ Separate WebSocket connections for each user

**Troubleshooting**:
- ❌ Shared data: Critical security issue, check JWT implementation

---

## 📊 Performance Benchmarks

### Expected Metrics:

| Metric | Phase 1 (Stub) | Phase 2 (Real AI) |
|--------|----------------|-------------------|
| Wake word detection | < 1 second | < 1 second |
| Voice → Response | 1-2 seconds | 3-7 seconds |
| Typed → Response | < 1 second | 2-5 seconds |
| WebSocket latency | < 100ms | < 100ms |
| Video frame rate | 15-30 FPS | 15-30 FPS |

### Performance Issues:

**Slow Responses**:
- Check network connection
- Check API status (Phase 2)
- Check CPU usage (high load may slow camera processing)

**High Latency**:
- Check WebSocket connection quality
- Try using localhost instead of network IP

---

## 🐛 Common Issues & Solutions

### Issue 1: "Speech recognition not supported"
**Cause**: Browser doesn't support Web Speech API
**Solution**: Use Chrome or Edge

### Issue 2: "WebSocket disconnected: Invalid authentication"
**Cause**: JWT token expired or invalid
**Solution**: Logout and login again

### Issue 3: "Failed to initialize camera streams"
**Cause**: Camera in use or not accessible
**Solution**:
- Close other apps using camera
- Check camera permissions
- Try different `CAMERA_IDS` in `.env`

### Issue 4: "Context is empty" (Phase 2)
**Cause**: No data in database
**Solution**: Normal for new installation. System will respond: "No persons detected yet"

### Issue 5: API Rate Limit (Phase 2)
**Cause**: Too many requests to Claude API
**Solution**: Wait 60 seconds, or implement caching

### Issue 6: Voice commands not working
**Possible Causes**:
1. Microphone not enabled
2. Browser doesn't support Web Speech API
3. WebSocket connection lost
4. Backend not running

**Debug Steps**:
1. Check browser console (F12) for errors
2. Check microphone permissions
3. Verify WebSocket connection (Network tab)
4. Check backend logs

---

## 📝 Test Results Template

Use this to document your test results:

```
# SentinelAI Test Results

Date: _______________
Tester: _______________

## Environment
- OS: Windows ___
- Browser: _______________
- Python: _______________
- Node: _______________

## Test Results

### Phase 1 Tests
- [ ] Login & Dashboard Access
- [ ] Voice Control Activation
- [ ] Wake Word Detection
- [ ] Voice Command (Stub)
- [ ] WebSocket Reconnection
- [ ] Multi-User Isolation

### Phase 2 Tests
- [ ] Voice Command (Real AI)
- [ ] Typed Chat
- [ ] Video Clip Display
- [ ] Multiple Conversations

## Issues Found
1. _____________________________
2. _____________________________
3. _____________________________

## Performance Notes
- Wake word latency: _______ seconds
- AI response time: _______ seconds
- WebSocket reconnection: _______ seconds

## Overall Status
- [ ] All tests passed
- [ ] Minor issues found (document above)
- [ ] Critical issues found (document above)
```

---

## 🎯 Success Criteria

**Phase 1 is successful if**:
- ✅ Voice control activates with microphone click
- ✅ "Hey Sentinel" is detected reliably (>80% of attempts)
- ✅ Voice commands sent to backend
- ✅ Stub responses appear in chat
- ✅ WebSocket auto-reconnects on disconnect

**Phase 2 is successful if**:
- ✅ Real AI responses from Claude API
- ✅ Responses are contextually relevant
- ✅ Video clips display (if data exists)
- ✅ Both voice and typed chat work
- ✅ Multiple conversations tracked correctly

---

## 🔧 Quick Troubleshooting Commands

**Check if backend is running**:
```bash
curl http://localhost:8000/
```
Expected: `{"status":"ok","service":"SentinelAI API"}`

**Check if frontend is running**:
Open: `http://localhost:5173`

**Check database**:
```bash
ls c:/Users/hratc/sentinelai/data/
```
Should show: `sentinelai.db`

**View backend logs**:
Backend terminal shows real-time logs

**View frontend errors**:
Browser → F12 → Console tab

---

## 📞 Need Help?

If you encounter issues:
1. Check this guide's troubleshooting sections
2. Review backend logs for error messages
3. Check browser console (F12) for frontend errors
4. Verify all prerequisites are met

Happy Testing! 🎉
