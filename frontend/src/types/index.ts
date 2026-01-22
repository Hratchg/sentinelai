/**
 * TypeScript type definitions for SentinelAI API
 */

export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface Job {
  job_id: string;
  filename: string;
  status: JobStatus;
  progress: number;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  error_message: string | null;
}

export interface UploadResponse {
  job_id: string;
  filename: string;
  status: JobStatus;
  message: string;
}

export interface JobListResponse {
  jobs: Job[];
  total: number;
  skip: number;
  limit: number;
}

export interface EventData {
  timestamp: string;  // ISO datetime string
  track_id: number;
  action: 'standing' | 'walking' | 'running' | 'loitering';
  confidence: number;
  bbox: [number, number, number, number];
}

export interface VideoInfo {
  filename: string;
  duration: number;
  fps: number;
  resolution: [number, number];
  total_frames: number;
}

export interface EventsResponse {
  job_id: string;
  video_info: VideoInfo | null;  // Optional (may be null)
  events: EventData[];
  summary: {
    total_events: number;
    unique_tracks: number;
    actions: Record<string, number>;
  };
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
}

// Week 3: Alert Types
export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface Alert {
  id: string;
  alert_type: 'fall_detected' | 'fight_detected' | 'prolonged_loitering' | 'crowd_detected';
  severity: AlertSeverity;
  message: string;
  timestamp: string;  // ISO datetime
  frame_id: number;
  track_ids: number[];
}

export interface AlertsResponse {
  summary: {
    total_alerts: number;
    by_severity: {
      critical: number;
      high: number;
      medium: number;
      low: number;
    };
    by_type: Record<string, number>;
    unacknowledged: number;
  };
  alerts: Alert[];
}

// Week 3: Heatmap Types
export interface HeatmapStats {
  total_detections: number;
  active_cells: number;
  grid_size: [number, number];
  cell_size: number;
  max_density: number;
  mean_density: number;
}

// Week 4: Voice Control Types
export interface VoiceResponse {
  type: 'voice_response';
  question: string;
  answer: string;
  video_clips?: VideoClip[];
  timestamp: string;
}

export interface VideoClip {
  clip_url: string;
  person_id: string;
  timestamp: string;
  event_type: string;
}

export interface VoiceControlOptions {
  onWakeWordDetected?: () => void;
  onTranscript?: (text: string) => void;
  wakeWord?: string;
  enabled?: boolean;
}

// Week 4: WebSocket Message Types
export type WebSocketMessageType =
  | 'connected'
  | 'frame'
  | 'event'
  | 'voice_response'
  | 'pong'
  | 'stats'
  | 'error';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  camera_id?: number;
  timestamp?: string;
  data?: any;
  message?: string;
}

export interface FrameData {
  frame: string; // base64 encoded JPEG
  tracks: Track[];
  events: EventData[];
}

export interface Track {
  track_id: number;
  person_id: string;
  bbox: number[]; // [x1, y1, x2, y2]
  confidence: number;
  action?: string;
}

// Week 4: Real-time Person Types
export interface Person {
  id: string;
  name: string | null;
  display_name: string | null;
  face_embedding: number[] | null;
  first_seen_at: string;
  last_seen_at: string;
  total_appearances: number;
  archived: boolean;
  name_source: 'audio' | 'manual' | 'unknown';
}

export interface PersonEvent {
  id: string;
  person_id: string;
  camera_id: number;
  event_type: string;
  action: string | null;
  confidence: number;
  bbox: number[] | null;
  created_at: string;
}

// Week 4: Gesture Types
export interface GestureTemplate {
  id: string;
  label: string;
  template_data: number[][];
  created_at: string;
  user_id: string;
}
