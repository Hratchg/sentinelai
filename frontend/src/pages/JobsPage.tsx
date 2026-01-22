import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { RefreshCw, Eye, Trash2, Filter } from 'lucide-react';
import { listJobs, deleteJob } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import ProgressBar from '../components/ProgressBar';
import type { JobStatus } from '../types';

export default function JobsPage() {
  const [statusFilter, setStatusFilter] = useState<JobStatus | 'all'>('all');

  // Fetch jobs with auto-refresh every 2 seconds
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['jobs', statusFilter],
    queryFn: () => listJobs(0, 20, statusFilter === 'all' ? undefined : statusFilter),
    refetchInterval: 2000, // Poll every 2 seconds
  });

  const handleDelete = async (jobId: string) => {
    if (confirm('Are you sure you want to delete this job?')) {
      try {
        await deleteJob(jobId);
        refetch();
      } catch (error) {
        console.error('Failed to delete job:', error);
      }
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Jobs</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitor your video processing jobs
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as JobStatus | 'all')}
              className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Status</option>
              <option value="queued">Queued</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          {/* Refresh Button */}
          <button
            onClick={() => refetch()}
            className="p-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <RefreshCw className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>
      </div>

      {/* Jobs List */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
          <p className="text-red-800 dark:text-red-300">Failed to load jobs. Please try again.</p>
        </div>
      ) : !data || data.jobs.length === 0 ? (
        <div className="bg-gray-50 dark:bg-gray-800 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-12 text-center">
          <p className="text-gray-600 dark:text-gray-400 text-lg">No jobs found</p>
          <Link
            to="/upload"
            className="inline-block mt-4 text-primary-600 dark:text-primary-400 hover:underline"
          >
            Upload your first video →
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {data.jobs.map((job) => (
            <div
              key={job.job_id}
              className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                {/* Job Info */}
                <div className="flex-1 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white text-lg">
                        {job.filename}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        Created {formatDate(job.created_at)}
                      </p>
                    </div>
                    <StatusBadge status={job.status} />
                  </div>

                  {/* Progress Bar */}
                  {(job.status === 'processing' || job.status === 'queued') && (
                    <ProgressBar progress={job.progress} showLabel={false} />
                  )}

                  {/* Error Message */}
                  {job.error_message && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      Error: {job.error_message}
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2">
                  {job.status === 'completed' && (
                    <Link
                      to={`/results/${job.job_id}`}
                      className="inline-flex items-center space-x-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                      <span>View Results</span>
                    </Link>
                  )}

                  <button
                    onClick={() => handleDelete(job.job_id)}
                    className="p-2 text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                    title="Delete job"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}

          {/* Pagination Info */}
          <div className="text-center text-sm text-gray-600 dark:text-gray-400 py-4">
            Showing {data.jobs.length} of {data.total} jobs
          </div>
        </div>
      )}
    </div>
  );
}
