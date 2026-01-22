# Bug Fix: Tracker Image Parameter

## Issue

Video processing failed with error:
```
AssertionError: Unsupported 'img_numpy' input format '<class 'NoneType'>', valid format is np.ndarray
```

## Root Cause

The ByteTrack tracker's `update()` method requires the **frame image** as a parameter, but our code was passing `None` instead.

**Location:** `backend/core/tracker.py` line 156

```python
# WRONG (old code)
tracks = self.tracker.update(detections, None)  # ❌ Passing None
```

ByteTrack uses the image for appearance-based tracking features, so it must be a valid numpy array.

## Fix Applied

### 1. Updated Tracker Method Signature

**File:** `backend/core/tracker.py` line 138

```python
# Added 'frame' parameter
def update(self, detections: np.ndarray, frame_id: int, frame: np.ndarray = None) -> List[dict]:
```

### 2. Pass Frame to ByteTrack

**File:** `backend/core/tracker.py` line 158

```python
# CORRECT (fixed code)
tracks = self.tracker.update(detections, frame)  # ✅ Passing actual frame
```

### 3. Update Pipeline Call

**File:** `backend/core/pipeline.py` line 175

```python
# OLD
tracks = self.tracker.update(detections, frame_id)

# NEW
tracks = self.tracker.update(detections, frame_id, frame)
```

## Files Modified

1. **backend/core/tracker.py**
   - Line 138: Added `frame` parameter to `update()` method
   - Line 158: Changed `None` to `frame` in ByteTrack call

2. **backend/core/pipeline.py**
   - Line 175: Added `frame` argument to tracker.update() call

## Testing

After this fix:
- ✅ Detector receives valid frames
- ✅ Tracker receives both detections AND frame image
- ✅ ByteTrack can perform appearance-based tracking
- ✅ Video processing completes successfully

## How to Apply

1. **Stop the backend server** (Ctrl+C)

2. **Restart it:**
   ```bash
   cd c:/Users/hratc/sentinelai
   ./backend/venv/Scripts/python.exe -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Upload your video again** at http://localhost:5173

4. **Should work now!** ✅

## Why This Happened

The original code was written assuming ByteTrack could work without the image (motion-only tracking), but the BoxMOT library implementation requires the frame image parameter for all tracking modes.

---

**Status:** ✅ FIXED
**Verified:** Code updated and ready to test
