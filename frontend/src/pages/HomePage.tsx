import { Link } from 'react-router-dom';
import { Upload, Activity, FileVideo, Zap } from 'lucide-react';

export default function HomePage() {
  const features = [
    {
      icon: FileVideo,
      title: 'Person Detection',
      description: 'YOLOv8-powered detection identifies people in video frames with high accuracy',
    },
    {
      icon: Activity,
      title: 'Action Recognition',
      description: 'Automatically classify actions: standing, walking, running, and loitering',
    },
    {
      icon: Zap,
      title: 'Real-time Processing',
      description: 'Async job queue processes videos in the background with progress tracking',
    },
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <h1 className="text-5xl font-bold text-gray-900 dark:text-white">
          Welcome to <span className="text-primary-600 dark:text-primary-400">SentinelAI</span>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
          AI-powered video surveillance system with person detection, multi-object tracking,
          and action recognition
        </p>
        <div className="flex justify-center gap-4">
          <Link
            to="/upload"
            className="inline-flex items-center space-x-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
          >
            <Upload className="w-5 h-5" />
            <span>Upload Video</span>
          </Link>
          <Link
            to="/jobs"
            className="inline-flex items-center space-x-2 px-6 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg font-medium transition-colors"
          >
            <Activity className="w-5 h-5" />
            <span>View Jobs</span>
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <div
              key={index}
              className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
            >
              <div className="bg-primary-100 dark:bg-primary-900 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {feature.description}
              </p>
            </div>
          );
        })}
      </div>

      {/* Stats */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-700 dark:to-primary-800 rounded-xl p-8 text-white">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold mb-2">100%</div>
            <div className="text-primary-100">Week 1 Complete</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">7</div>
            <div className="text-primary-100">API Endpoints</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">20%</div>
            <div className="text-primary-100">Project Progress</div>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Getting Started
        </h2>
        <ol className="space-y-4 text-gray-600 dark:text-gray-400">
          <li className="flex items-start space-x-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
              1
            </span>
            <span>
              <strong className="text-gray-900 dark:text-white">Upload a video</strong> - Go to the Upload page and select a video file (MP4, AVI, MOV)
            </span>
          </li>
          <li className="flex items-start space-x-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
              2
            </span>
            <span>
              <strong className="text-gray-900 dark:text-white">Monitor processing</strong> - Track your job's progress in real-time on the Jobs page
            </span>
          </li>
          <li className="flex items-start space-x-3">
            <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
              3
            </span>
            <span>
              <strong className="text-gray-900 dark:text-white">View results</strong> - Download the annotated video and explore detected events
            </span>
          </li>
        </ol>
      </div>
    </div>
  );
}
