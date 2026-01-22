import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Download, ArrowLeft, Clock, Activity } from 'lucide-react';
import { getJobStatus, getEvents, getVideoUrl } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import ProgressBar from '../components/ProgressBar';
import { AlertsPanel } from '../components/AlertsPanel';
import { HeatmapViewer } from '../components/HeatmapViewer';

export default function ResultsPage() {
  const { jobId } = useParams<{ jobId: string }>();

  // Poll job status until completed
  const { data: job, isLoading: jobLoading } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => getJobStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: (data) => {
      // Stop polling if completed or failed
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });

  // Fetch events only when job is completed
  const { data: events, isLoading: eventsLoading } = useQuery({
    queryKey: ['events', jobId],
    queryFn: () => getEvents(jobId!),
    enabled: !!jobId && job?.status === 'completed',
  });

  const getActionColor = (action: string) => {
    const colors: Record<string, string> = {
      standing: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      walking: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
      running: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      loitering: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    };
    return colors[action] || 'bg-gray-100 text-gray-800';
  };

  const formatTimestamp = (isoString: string) => {
    // Parse ISO datetime and convert to seconds from video start
    if (!events || events.events.length === 0) return '0:00';

    const eventTime = new Date(isoString);
    const firstEventTime = new Date(events.events[0].timestamp);
    const secondsFromStart = (eventTime.getTime() - firstEventTime.getTime()) / 1000;

    const mins = Math.floor(secondsFromStart / 60);
    const secs = Math.floor(secondsFromStart % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (jobLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!job) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">Job not found</p>
        <Link to="/jobs" className="text-primary-600 dark:text-primary-400 hover:underline mt-4 inline-block">
          Back to jobs
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link
          to="/jobs"
          className="inline-flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to jobs</span>
        </Link>
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {job.filename}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Job ID: {job.job_id}
            </p>
          </div>
          <StatusBadge status={job.status} />
        </div>
      </div>

      {/* Processing Status */}
      {(job.status === 'processing' || job.status === 'queued') && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Processing Video...
          </h2>
          <ProgressBar progress={job.progress} />
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">
            This may take a few minutes depending on video length and hardware.
          </p>
        </div>
      )}

      {/* Error Message */}
      {job.status === 'failed' && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-900 dark:text-red-300 mb-2">
            Processing Failed
          </h2>
          <p className="text-red-800 dark:text-red-400">
            {job.error_message || 'An unknown error occurred'}
          </p>
        </div>
      )}

      {/* Results */}
      {job.status === 'completed' && events && (
        <>
          {/* Video Player */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Processed Video
              </h2>
              <a
                href={getVideoUrl(job.job_id)}
                download
                className="inline-flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors text-sm"
              >
                <Download className="w-4 h-4" />
                <span>Download</span>
              </a>
            </div>
            <div className="bg-black">
              <video
                controls
                className="w-full max-h-[600px]"
                src={getVideoUrl(job.job_id)}
              >
                Your browser does not support the video tag.
              </video>
            </div>
          </div>

          {/* Week 3: Heatmap Viewer */}
          <HeatmapViewer jobId={job.job_id} />

          {/* Video Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center space-x-3">
                <Activity className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Events</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {events.summary.total_events}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center space-x-3">
                <Activity className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Unique Tracks</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white">
                    {events.summary.unique_tracks}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Summary */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Action Summary
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(events.summary.actions).map(([action, count]) => (
                <div key={action} className="text-center">
                  <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-2 ${getActionColor(action)}`}>
                    {action}
                  </div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{count}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Week 3: Alerts Panel */}
          <AlertsPanel jobId={job.job_id} />

          {/* Events Timeline */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Events Timeline
            </h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {events.events.slice(0, 50).map((event, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <span className="text-sm font-mono text-gray-600 dark:text-gray-400">
                      {formatTimestamp(event.timestamp)}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getActionColor(event.action)}`}>
                      {event.action}
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      Track #{event.track_id}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {(event.confidence * 100).toFixed(0)}% confidence
                  </div>
                </div>
              ))}
              {events.events.length > 50 && (
                <p className="text-center text-sm text-gray-600 dark:text-gray-400 py-2">
                  Showing first 50 of {events.events.length} events
                </p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
