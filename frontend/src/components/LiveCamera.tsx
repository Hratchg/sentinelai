/**
 * LiveCamera Component
 *
 * Real-time webcam display with WebSocket streaming.
 * Shows live video feed with person detections and event overlays.
 * Supports voice command responses via WebSocket.
 */

import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Track {
  track_id: number;
  person_id: string;
  bbox: number[]; // [x1, y1, x2, y2]
  confidence: number;
}

interface EventData {
  event_type: string;
  person_id: string;
  action: string;
  confidence: number;
  timestamp: number;
}

interface VoiceResponse {
  type: 'voice_response';
  question: string;
  answer: string;
  video_clips?: any[];
  timestamp: string;
}

interface LiveCameraProps {
  cameraId: number;
  width?: number;
  height?: number;
  onVoiceResponse?: (response: VoiceResponse) => void;
  onVoiceCommandReady?: (sendCommand: (command: string) => void) => void;
}

export function LiveCamera({
  cameraId,
  width = 1280,
  height = 720,
  onVoiceResponse,
  onVoiceCommandReady
}: LiveCameraProps) {
  const { token } = useAuth();
  const wsRef = useRef<WebSocket | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [connected, setConnected] = useState(false);
  const [persons, setPersons] = useState<Track[]>([]);
  const [events, setEvents] = useState<EventData[]>([]);
  const [fps, setFps] = useState(0);

  // Function to send voice command
  const sendVoiceCommand = (command: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(`voice:${command}`);
    } else {
      console.warn('WebSocket not connected, cannot send voice command');
    }
  };

  // Expose sendVoiceCommand to parent component
  useEffect(() => {
    onVoiceCommandReady?.(sendVoiceCommand);
  }, [onVoiceCommandReady]);

  useEffect(() => {
    if (!token) {
      console.error('No authentication token available');
      return;
    }

    // Connect to WebSocket with JWT token
    const ws = new WebSocket(`ws://localhost:8000/ws/camera/${cameraId}?token=${token}`);

    ws.onopen = () => {
      console.log(`Connected to camera ${cameraId}`);
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'connected') {
        console.log(data.message);
      }
      else if (data.type === 'frame') {
        // Update canvas with new frame
        if (canvasRef.current && data.data.frame) {
          const ctx = canvasRef.current.getContext('2d');
          if (!ctx) return;

          const img = new Image();
          img.onload = () => {
            // Draw frame
            ctx.drawImage(img, 0, 0, width, height);

            // Draw bounding boxes and labels
            data.data.tracks?.forEach((track: Track) => {
              drawBoundingBox(ctx, track, width, height);
            });

            // Draw FPS
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillRect(10, 10, 100, 40);
            ctx.fillStyle = '#00ff00';
            ctx.font = '20px monospace';
            ctx.fillText(`FPS: ${fps.toFixed(1)}`, 20, 35);

            // Draw LIVE indicator
            ctx.fillStyle = 'rgba(255, 0, 0, 0.8)';
            ctx.fillRect(width - 80, 10, 70, 30);
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 16px Arial';
            ctx.fillText('LIVE', width - 70, 32);
          };
          img.src = `data:image/jpeg;base64,${data.data.frame}`;

          // Update tracks
          setPersons(data.data.tracks || []);

          // Calculate FPS
          setFps((prev) => prev * 0.9 + 1 * 0.1); // Exponential moving average
        }

        // Update events
        if (data.data.events) {
          setEvents(data.data.events.slice(0, 5)); // Keep last 5 events
        }
      }
      else if (data.type === 'event') {
        // New event received
        setEvents((prev) => [data.data, ...prev].slice(0, 5));
      }
      else if (data.type === 'voice_response') {
        // Voice command response received
        console.log('Voice response:', data);
        onVoiceResponse?.(data as VoiceResponse);
      }
      else if (data.type === 'pong') {
        // Heartbeat response
        console.debug('Heartbeat acknowledged');
      }
      else if (data.type === 'error') {
        console.error('WebSocket error:', data.message);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
    };

    ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.reason);
      setConnected(false);

      // Automatic reconnection after 3 seconds
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }

      reconnectTimeoutRef.current = setTimeout(() => {
        console.log('Attempting to reconnect...');
        // Will trigger reconnection by re-running effect
        setConnected(false);
      }, 3000);
    };

    wsRef.current = ws;

    // Send heartbeat every 30 seconds
    const heartbeat = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      }
    }, 30000);

    return () => {
      clearInterval(heartbeat);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      ws.close();
    };
  }, [cameraId, width, height, fps, token]);

  const drawBoundingBox = (ctx: CanvasRenderingContext2D, track: Track, canvasWidth: number, canvasHeight: number) => {
    const [x1, y1, x2, y2] = track.bbox;

    // Draw bounding box
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 3;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

    // Draw label background
    const label = `${track.person_id} (${(track.confidence * 100).toFixed(0)}%)`;
    ctx.font = '14px Arial';
    const textWidth = ctx.measureText(label).width;

    ctx.fillStyle = 'rgba(0, 255, 0, 0.8)';
    ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);

    // Draw label text
    ctx.fillStyle = '#000000';
    ctx.fillText(label, x1 + 5, y1 - 8);
  };

  return (
    <div className="relative bg-black rounded-lg overflow-hidden shadow-xl">
      {/* Canvas for video display */}
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="w-full h-auto"
      />

      {/* Connection status indicator */}
      <div className="absolute top-4 left-4">
        <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
          connected
            ? 'bg-green-500 text-white'
            : 'bg-red-500 text-white'
        }`}>
          {connected ? '● Connected' : '● Disconnected'}
        </div>
      </div>

      {/* Active persons count */}
      {persons.length > 0 && (
        <div className="absolute top-4 right-24 bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
          {persons.length} {persons.length === 1 ? 'Person' : 'People'}
        </div>
      )}

      {/* Event feed overlay */}
      {events.length > 0 && (
        <div className="absolute bottom-4 left-4 right-4 bg-black bg-opacity-70 rounded-lg p-3 max-h-32 overflow-y-auto">
          <div className="text-white text-sm space-y-1">
            {events.map((event, i) => (
              <div key={i} className="flex items-center space-x-2">
                <span className="text-yellow-400">●</span>
                <span className="font-semibold">{event.person_id}</span>
                <span className="text-gray-300">→</span>
                <span>{event.action || event.event_type}</span>
                <span className="text-gray-400 text-xs ml-auto">
                  {new Date(event.timestamp * 1000).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No connection message */}
      {!connected && (
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="text-white text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p className="text-lg">Connecting to camera {cameraId}...</p>
          </div>
        </div>
      )}
    </div>
  );
}
