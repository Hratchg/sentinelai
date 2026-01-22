/**
 * SystemHealth Component
 *
 * Monitors system health and storage usage.
 * Displays database size, known persons, events, and allows manual cleanup.
 */

import { useState, useEffect } from 'react';
import axios from 'axios';

interface SystemHealthProps {
  apiBaseUrl?: string;
}

interface HealthStats {
  database_size_mb: number;
  total_persons: number;
  active_persons: number;
  archived_persons: number;
  total_events: number;
  total_clips: number;
  total_gestures: number;
  clips_size_gb: number;
}

export function SystemHealth({ apiBaseUrl = 'http://localhost:8000' }: SystemHealthProps) {
  const [stats, setStats] = useState<HealthStats>({
    database_size_mb: 0,
    total_persons: 0,
    active_persons: 0,
    archived_persons: 0,
    total_events: 0,
    total_clips: 0,
    total_gestures: 0,
    clips_size_gb: 0
  });
  const [loading, setLoading] = useState(false);
  const [cleanupRunning, setCleanupRunning] = useState(false);

  useEffect(() => {
    loadStats();

    // Refresh stats every 30 seconds
    const interval = setInterval(loadStats, 30000);

    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${apiBaseUrl}/api/v1/admin/health`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const runCleanup = async () => {
    if (!confirm('Are you sure you want to run cleanup? This will delete old events and video clips according to retention policies.')) {
      return;
    }

    setCleanupRunning(true);

    try {
      // Call cleanup API endpoint
      await axios.post(`${apiBaseUrl}/api/v1/admin/cleanup`);

      alert('Cleanup completed successfully!');
      loadStats();

    } catch (error) {
      console.error('Cleanup failed:', error);
      alert('Cleanup failed. Check console for details.');
    } finally {
      setCleanupRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">System Health</h1>
          <p className="text-gray-600 mt-2">Monitor storage usage and system statistics</p>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {/* Database Size */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Database Size</h3>
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7z" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.database_size_mb} MB</p>
            <p className="text-sm text-gray-500 mt-1">of 10 GB available</p>
            <div className="mt-3 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${(stats.database_size_mb / 10000) * 100}%` }}
              />
            </div>
          </div>

          {/* Known Persons */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Known Persons</h3>
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.total_persons.toLocaleString()}</p>
            <p className="text-sm text-gray-500 mt-1">
              {stats.active_persons} active, {stats.archived_persons} archived
            </p>
          </div>

          {/* Total Events */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Total Events</h3>
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.total_events.toLocaleString()}</p>
            <p className="text-sm text-gray-500 mt-1">Last 90 days</p>
          </div>

          {/* Video Clips */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">Video Clips</h3>
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.total_clips.toLocaleString()}</p>
            <p className="text-sm text-gray-500 mt-1">{stats.clips_size_gb.toFixed(1)} GB storage</p>
            <div className="mt-3 bg-gray-200 rounded-full h-2">
              <div
                className="bg-red-600 h-2 rounded-full"
                style={{ width: `${(stats.clips_size_gb / 10) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Detailed Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Gestures */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Learned Gestures</h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-4xl font-bold text-gray-900">{stats.total_gestures}</p>
                <p className="text-sm text-gray-500 mt-1">Custom gestures</p>
              </div>
              <svg className="w-16 h-16 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11" />
              </svg>
            </div>
          </div>

          {/* Retention Policies */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Retention Policies</h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Inactive Persons:</span>
                <span className="font-semibold">Archive after 6 months</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Event Logs:</span>
                <span className="font-semibold">Delete after 1 year</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Video Clips:</span>
                <span className="font-semibold">Delete after 30 days</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Archived Persons:</span>
                <span className="font-semibold">Delete after 2 years</span>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Maintenance Actions</h2>

          <div className="space-y-4">
            <button
              onClick={runCleanup}
              disabled={cleanupRunning || loading}
              className="w-full px-6 py-3 bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              {cleanupRunning ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Running Cleanup...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  <span>Run Cleanup Now</span>
                </>
              )}
            </button>

            <button
              onClick={loadStats}
              disabled={loading}
              className="w-full px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 disabled:bg-gray-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Refresh Stats</span>
            </button>
          </div>

          <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">
              <strong>Note:</strong> Cleanup will permanently delete old events and video clips according to retention policies.
              This action cannot be undone. Archived persons and their face embeddings will remain in the database.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
