/**
 * Video Upload Component
 *
 * Allows users to upload video files for AI analysis.
 * Integrated into the Dashboard sidebar navigation.
 */

import { useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100 MB
const ALLOWED_FORMATS = ['video/mp4', 'video/avi', 'video/mov', 'video/x-msvideo', 'video/quicktime'];

interface UploadJob {
  id: string;
  filename: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string;
}

export function VideoUpload() {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [jobs, setJobs] = useState<UploadJob[]>([]);

  const validateFile = (file: File): string | null => {
    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds 100 MB limit. Your file is ${(file.size / (1024 * 1024)).toFixed(1)} MB.`;
    }
    if (!ALLOWED_FORMATS.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|mkv)$/i)) {
      return 'Invalid file format. Please upload MP4, AVI, MOV, or MKV files only.';
    }
    return null;
  };

  const handleFile = useCallback((selectedFile: File) => {
    setError(null);
    const validationError = validateFile(selectedFile);
    if (validationError) {
      setError(validationError);
      return;
    }
    setFile(selectedFile);
  }, []);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, [handleFile]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !token) return;

    setUploading(true);
    setUploadProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/v1/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || 'Upload failed');
      }

      const data = await response.json();

      // Add to jobs list
      setJobs((prev) => [
        {
          id: data.job_id,
          filename: file.name,
          status: 'processing',
          progress: 100,
        },
        ...prev,
      ]);

      // Clear file
      setFile(null);
      setUploadProgress(100);

      // Start polling for job status
      pollJobStatus(data.job_id);
    } catch (err: any) {
      setError(err.message || 'Failed to upload video');
    } finally {
      setUploading(false);
    }
  };

  const pollJobStatus = async (jobId: string) => {
    const poll = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const job = await response.json();
          setJobs((prev) =>
            prev.map((j) =>
              j.id === jobId
                ? { ...j, status: job.status, progress: job.progress || 0 }
                : j
            )
          );

          if (job.status !== 'completed' && job.status !== 'failed') {
            setTimeout(poll, 2000);
          }
        }
      } catch (err) {
        console.error('Failed to poll job status:', err);
      }
    };

    poll();
  };

  const clearFile = () => {
    setFile(null);
    setError(null);
  };

  return (
    <div className="h-full bg-gray-900 p-6 overflow-auto">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-white">Upload Video</h1>
          <p className="text-gray-400">
            Upload surveillance footage for AI-powered analysis
          </p>
        </div>

        {/* Upload Area */}
        <div className="bg-gray-800 rounded-xl p-6 border-2 border-dashed border-gray-600">
          {!file ? (
            <form
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className="space-y-4"
            >
              <label
                className={`
                  block cursor-pointer transition-colors rounded-lg p-8
                  ${dragActive
                    ? 'bg-blue-900/30 border-blue-500'
                    : 'hover:bg-gray-700/50'
                  }
                `}
              >
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleChange}
                  className="hidden"
                />
                <div className="flex flex-col items-center space-y-4">
                  <div className="bg-blue-600 w-16 h-16 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-medium text-white">
                      Drop video file here or click to browse
                    </p>
                    <p className="text-sm text-gray-400 mt-1">
                      MP4, AVI, MOV, or MKV (max 100 MB)
                    </p>
                  </div>
                </div>
              </label>
            </form>
          ) : (
            <div className="space-y-4">
              {/* File Preview */}
              <div className="flex items-start justify-between bg-gray-700/50 rounded-lg p-4">
                <div className="flex items-start space-x-3 flex-1">
                  <svg className="w-10 h-10 text-blue-400 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-white truncate">{file.name}</p>
                    <p className="text-sm text-gray-400">
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={clearFile}
                  className="ml-4 p-2 hover:bg-gray-600 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Upload Button */}
              <button
                onClick={handleUpload}
                disabled={uploading}
                className={`
                  w-full py-3 px-6 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2
                  ${uploading
                    ? 'bg-gray-600 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }
                `}
              >
                {uploading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Uploading... {uploadProgress}%</span>
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                    <span>Upload and Process</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-4 bg-red-900/30 border border-red-700 rounded-lg p-4 flex items-start space-x-3">
              <svg className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}
        </div>

        {/* Processing Jobs */}
        {jobs.length > 0 && (
          <div className="bg-gray-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Processing Jobs</h2>
            <div className="space-y-3">
              {jobs.map((job) => (
                <div key={job.id} className="bg-gray-700/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium truncate">{job.filename}</span>
                    <span className={`text-sm px-2 py-1 rounded ${
                      job.status === 'completed' ? 'bg-green-600 text-white' :
                      job.status === 'failed' ? 'bg-red-600 text-white' :
                      job.status === 'processing' ? 'bg-yellow-600 text-white' :
                      'bg-blue-600 text-white'
                    }`}>
                      {job.status}
                    </span>
                  </div>
                  {job.status === 'processing' && (
                    <div className="w-full bg-gray-600 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all"
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-blue-900/30 rounded-lg p-4 border border-blue-700">
            <h3 className="font-medium text-blue-300 mb-2">Supported Formats</h3>
            <p className="text-sm text-blue-400">MP4, AVI, MOV, and MKV video files</p>
          </div>
          <div className="bg-purple-900/30 rounded-lg p-4 border border-purple-700">
            <h3 className="font-medium text-purple-300 mb-2">AI Analysis</h3>
            <p className="text-sm text-purple-400">Person detection, tracking, and action recognition</p>
          </div>
        </div>
      </div>
    </div>
  );
}
