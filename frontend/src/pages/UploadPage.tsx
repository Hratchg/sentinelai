import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Upload, FileVideo, X, AlertCircle, CheckCircle2 } from 'lucide-react';
import { uploadVideo } from '../services/api';

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100 MB
const ALLOWED_FORMATS = ['video/mp4', 'video/avi', 'video/mov', 'video/x-msvideo', 'video/quicktime'];

export default function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadMutation = useMutation({
    mutationFn: uploadVideo,
    onSuccess: (data) => {
      console.log('Upload successful:', data);
      // Navigate to results page for this job
      navigate(`/results/${data.job_id}`);
    },
    onError: (error: any) => {
      console.error('Upload failed:', error);
      setError(error.response?.data?.message || 'Failed to upload video. Please try again.');
    },
  });

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds 100 MB limit. Your file is ${(file.size / (1024 * 1024)).toFixed(1)} MB.`;
    }

    // Check file type
    if (!ALLOWED_FORMATS.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|mkv)$/i)) {
      return 'Invalid file format. Please upload MP4, AVI, or MOV files only.';
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

  const handleUpload = () => {
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  const clearFile = () => {
    setFile(null);
    setError(null);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
          Upload Video
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Upload a surveillance video for AI-powered analysis
        </p>
      </div>

      {/* Upload Area */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border-2 border-dashed border-gray-300 dark:border-gray-600">
        {!file ? (
          <form
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className="space-y-6"
          >
            <label
              className={`
                block cursor-pointer transition-colors rounded-lg p-8
                ${dragActive
                  ? 'bg-primary-50 dark:bg-primary-900/20 border-primary-500'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
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
                <div className="bg-primary-100 dark:bg-primary-900 w-16 h-16 rounded-full flex items-center justify-center">
                  <Upload className="w-8 h-8 text-primary-600 dark:text-primary-400" />
                </div>
                <div className="text-center">
                  <p className="text-lg font-medium text-gray-900 dark:text-white">
                    Drop video file here or click to browse
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    MP4, AVI, or MOV (max 100 MB)
                  </p>
                </div>
              </div>
            </label>
          </form>
        ) : (
          <div className="space-y-6">
            {/* File Preview */}
            <div className="flex items-start justify-between bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
              <div className="flex items-start space-x-3 flex-1">
                <FileVideo className="w-10 h-10 text-primary-600 dark:text-primary-400 flex-shrink-0 mt-1" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 dark:text-white truncate">
                    {file.name}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={clearFile}
                className="ml-4 p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={uploadMutation.isPending}
              className={`
                w-full py-3 px-6 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2
                ${uploadMutation.isPending
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-primary-600 hover:bg-primary-700 text-white'
                }
              `}
            >
              {uploadMutation.isPending ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Uploading...</span>
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  <span>Upload and Process</span>
                </>
              )}
            </button>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-800 dark:text-red-300">{error}</p>
          </div>
        )}

        {/* Success Message */}
        {uploadMutation.isSuccess && (
          <div className="mt-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-start space-x-3">
            <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-green-800 dark:text-green-300">
              Upload successful! Redirecting to results page...
            </p>
          </div>
        )}
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <h3 className="font-medium text-blue-900 dark:text-blue-300 mb-2">
            Supported Formats
          </h3>
          <p className="text-sm text-blue-700 dark:text-blue-400">
            MP4, AVI, MOV, and MKV video files
          </p>
        </div>
        <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
          <h3 className="font-medium text-purple-900 dark:text-purple-300 mb-2">
            Processing Time
          </h3>
          <p className="text-sm text-purple-700 dark:text-purple-400">
            Varies based on video length and hardware (GPU recommended)
          </p>
        </div>
      </div>
    </div>
  );
}
