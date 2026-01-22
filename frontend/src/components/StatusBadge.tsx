import type { JobStatus } from '../types';
import { Clock, Loader2, CheckCircle2, XCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: JobStatus;
  className?: string;
}

export default function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const configs: Record<JobStatus, { icon: any; label: string; color: string }> = {
    queued: {
      icon: Clock,
      label: 'Queued',
      color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
    },
    processing: {
      icon: Loader2,
      label: 'Processing',
      color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    },
    completed: {
      icon: CheckCircle2,
      label: 'Completed',
      color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    },
    failed: {
      icon: XCircle,
      label: 'Failed',
      color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    },
  };

  const config = configs[status];
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium ${config.color} ${className}`}
    >
      <Icon className={`w-4 h-4 ${status === 'processing' ? 'animate-spin' : ''}`} />
      <span>{config.label}</span>
    </span>
  );
}
