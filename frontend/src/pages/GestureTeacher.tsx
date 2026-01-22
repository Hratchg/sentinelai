/**
 * GestureTeacher Component
 *
 * Interface for teaching the system new gestures.
 * Records pose sequence and saves to backend.
 */

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface Gesture {
  gesture_id: string;
  label: string;
  num_frames: number;
  created_by: string | null;
  created_at: string;
  detection_count: number;
}

interface GestureTeacherProps {
  apiBaseUrl?: string;
}

export function GestureTeacher({ apiBaseUrl = 'http://localhost:8000' }: GestureTeacherProps) {
  const [gestures, setGestures] = useState<Gesture[]>([]);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [newGestureName, setNewGestureName] = useState('');
  const [recordingProgress, setRecordingProgress] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    loadGestures();
  }, []);

  const loadGestures = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/api/v1/gestures`);
      setGestures(response.data);
    } catch (error) {
      console.error('Failed to load gestures:', error);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }
    } catch (error) {
      console.error('Camera access error:', error);
      alert('Failed to access camera. Please grant camera permissions.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  const recordGesture = async () => {
    if (!newGestureName.trim()) {
      alert('Please enter a gesture name');
      return;
    }

    setRecording(true);
    setRecordingProgress(0);

    // Simulate recording for 1 second (30 frames @ 30 FPS)
    const totalFrames = 30;
    const frameInterval = 1000 / 30; // 33ms per frame

    const recordedPoses: number[][] = [];

    for (let i = 0; i < totalFrames; i++) {
      // TODO: Extract actual pose features from video frame using MediaPipe
      // For now, generate dummy data
      const dummyPose = Array(99).fill(0).map(() => Math.random());
      recordedPoses.push(dummyPose);

      setRecordingProgress(((i + 1) / totalFrames) * 100);

      await new Promise(resolve => setTimeout(resolve, frameInterval));
    }

    // Convert to base64 for transmission
    const poseSequence = recordedPoses; // In real implementation, this would be numpy array
    const poseSequenceB64 = btoa(JSON.stringify(poseSequence));

    setLoading(true);

    try {
      await axios.post(`${apiBaseUrl}/api/v1/gestures/teach`, {
        label: newGestureName.trim(),
        pose_sequence_b64: poseSequenceB64,
        num_frames: totalFrames
      });

      alert(`Gesture "${newGestureName}" learned successfully!`);
      setNewGestureName('');
      loadGestures();

    } catch (error: any) {
      console.error('Failed to teach gesture:', error);
      alert(`Failed to teach gesture: ${error.response?.data?.detail || error.message}`);
    } finally {
      setRecording(false);
      setLoading(false);
      setRecordingProgress(0);
    }
  };

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Gesture Teacher</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recording panel */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Teach New Gesture</h2>

            {/* Video preview */}
            <div className="bg-black rounded-lg overflow-hidden mb-4 relative">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-auto"
              />

              {/* Recording overlay */}
              {recording && (
                <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-white text-6xl font-bold mb-4">
                      {Math.ceil((30 - recordingProgress * 30 / 100) / 30)}
                    </div>
                    <div className="text-white text-xl mb-4">Hold your pose...</div>
                    <div className="w-64 bg-gray-700 rounded-full h-4">
                      <div
                        className="bg-red-600 h-4 rounded-full transition-all duration-100"
                        style={{ width: `${recordingProgress}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input and record button */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gesture Name
                </label>
                <input
                  type="text"
                  value={newGestureName}
                  onChange={(e) => setNewGestureName(e.target.value)}
                  placeholder="e.g., peace_sign, thumbs_up, wave"
                  className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={recording || loading}
                />
              </div>

              <button
                onClick={recordGesture}
                disabled={recording || loading || !newGestureName.trim()}
                className="w-full px-6 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
              >
                {recording ? (
                  <>
                    <div className="animate-pulse w-3 h-3 bg-white rounded-full"></div>
                    <span>Recording...</span>
                  </>
                ) : loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <circle cx="10" cy="10" r="8" />
                    </svg>
                    <span>Record Gesture (1 second)</span>
                  </>
                )}
              </button>

              <p className="text-sm text-gray-600">
                Click "Record Gesture" and hold your pose for 1 second.
                The system will capture 30 frames and learn the gesture.
              </p>
            </div>
          </div>

          {/* Learned gestures panel */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Learned Gestures</h2>
              <button
                onClick={loadGestures}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Refresh
              </button>
            </div>

            {gestures.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <p>No gestures learned yet</p>
                <p className="text-sm mt-2">Teach your first gesture to get started!</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {gestures.map((gesture) => (
                  <div
                    key={gesture.gesture_id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">{gesture.label}</h3>
                        <div className="text-sm text-gray-600 mt-1 space-y-1">
                          <p>Frames: {gesture.num_frames}</p>
                          <p>Detected: {gesture.detection_count} times</p>
                          <p className="text-xs text-gray-500">
                            Created: {new Date(gesture.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>

                      <div className="ml-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Active
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">How to Teach Gestures</h3>
          <ol className="list-decimal list-inside space-y-2 text-blue-800">
            <li>Enter a descriptive name for your gesture (e.g., "peace_sign", "thumbs_up")</li>
            <li>Position yourself in front of the camera</li>
            <li>Click "Record Gesture" and immediately strike your pose</li>
            <li>Hold the pose steady for 1 second while recording</li>
            <li>The system will learn the gesture and recognize it in the future!</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
