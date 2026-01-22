import { MapPin, BarChart3 } from 'lucide-react';
import { getHeatmapUrl } from '../services/api';
import { useState } from 'react';

interface HeatmapViewerProps {
  jobId: string;
}

export function HeatmapViewer({ jobId }: HeatmapViewerProps) {
  const [viewMode, setViewMode] = useState<'video' | 'heatmap'>('video');
  const [imageError, setImageError] = useState(false);
  const heatmapUrl = getHeatmapUrl(jobId);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      {/* Header with View Toggle */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
          <MapPin className="w-5 h-5 mr-2" />
          Activity Heatmap
        </h2>

        <div className="inline-flex rounded-lg border border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setViewMode('video')}
            className={`px-4 py-2 text-sm font-medium rounded-l-lg transition-colors ${
              viewMode === 'video'
                ? 'bg-primary-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            Video
          </button>
          <button
            onClick={() => setViewMode('heatmap')}
            className={`px-4 py-2 text-sm font-medium rounded-r-lg transition-colors ${
              viewMode === 'heatmap'
                ? 'bg-primary-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            Heatmap
          </button>
        </div>
      </div>

      {viewMode === 'heatmap' ? (
        <>
          {/* Heatmap Image */}
          {!imageError ? (
            <div className="bg-black rounded-lg overflow-hidden mb-4">
              <img
                src={heatmapUrl}
                alt="Activity Heatmap"
                className="w-full max-h-[600px] object-contain"
                onError={() => setImageError(true)}
              />
            </div>
          ) : (
            <div className="bg-gray-100 dark:bg-gray-900 rounded-lg p-8 text-center mb-4">
              <BarChart3 className="w-12 h-12 mx-auto mb-3 text-gray-400 dark:text-gray-600" />
              <p className="text-gray-600 dark:text-gray-400">Failed to load heatmap image</p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                The heatmap may still be processing or unavailable
              </p>
            </div>
          )}

          {/* Color Scale Legend */}
          <div className="bg-gradient-to-r from-blue-500 via-yellow-500 to-red-500 h-3 rounded mb-2"></div>
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-4">
            <span>Low Activity</span>
            <span>High Activity</span>
          </div>

          {/* Explanation */}
          <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            <p>• Red/yellow areas indicate high activity zones</p>
            <p>• Blue areas show low activity regions</p>
            <p>• Accumulated from all person detections in the video</p>
          </div>
        </>
      ) : (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>Switch to Heatmap view to see activity zones</p>
        </div>
      )}
    </div>
  );
}
