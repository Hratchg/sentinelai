/**
 * API Service for SentinelAI Backend
 */

import axios from 'axios';
import type { Job, JobListResponse, UploadResponse, EventsResponse, AlertsResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('[API] Response error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('[API] No response received:', error.request);
    } else {
      console.error('[API] Error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Upload a video file for processing
 */
export const uploadVideo = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Get status of a specific job
 */
export const getJobStatus = async (jobId: string): Promise<Job> => {
  const response = await api.get<Job>(`/jobs/${jobId}`);
  return response.data;
};

/**
 * List all jobs with pagination and filtering
 */
export const listJobs = async (
  skip: number = 0,
  limit: number = 20,
  status?: string
): Promise<JobListResponse> => {
  const params: Record<string, any> = { skip, limit };
  if (status) {
    params.status = status;
  }

  const response = await api.get<JobListResponse>('/jobs', { params });
  return response.data;
};

/**
 * Delete a job and its results
 */
export const deleteJob = async (jobId: string): Promise<void> => {
  await api.delete(`/jobs/${jobId}`);
};

/**
 * Get URL for downloading processed video
 */
export const getVideoUrl = (jobId: string): string => {
  return `${API_BASE_URL}/results/${jobId}/video`;
};

/**
 * Get events data for a completed job
 */
export const getEvents = async (jobId: string): Promise<EventsResponse> => {
  const response = await api.get<EventsResponse>(`/results/${jobId}/events`);
  return response.data;
};

/**
 * Get alerts for a completed job (Week 3)
 */
export const getAlerts = async (jobId: string): Promise<AlertsResponse> => {
  const response = await api.get<AlertsResponse>(`/results/${jobId}/alerts`);
  return response.data;
};

/**
 * Get heatmap image URL for a completed job (Week 3)
 */
export const getHeatmapUrl = (jobId: string): string => {
  return `${API_BASE_URL}/results/${jobId}/heatmap`;
};

/**
 * Check API health
 */
export const checkHealth = async (): Promise<{ status: string }> => {
  const response = await axios.get('http://localhost:8000/health');
  return response.data;
};

export default api;
