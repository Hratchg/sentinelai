import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, Shield, Info, AlertCircle } from 'lucide-react';
import { getAlerts } from '../services/api';
import type { Alert, AlertSeverity } from '../types';

interface AlertsPanelProps {
  jobId: string;
}

export function AlertsPanel({ jobId }: AlertsPanelProps) {
  const { data: alertsData, isLoading, error } = useQuery({
    queryKey: ['alerts', jobId],
    queryFn: () => getAlerts(jobId),
    enabled: !!jobId,
  });

  if (isLoading) {
    return <div className="text-center py-8 text-gray-500 dark:text-gray-400">Loading alerts...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-600 dark:text-red-400">Failed to load alerts</p>
      </div>
    );
  }

  if (!alertsData || alertsData.summary.total_alerts === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-center py-8 text-gray-500 dark:text-gray-400">
          <Shield className="w-8 h-8 mr-2" />
          <span>No alerts detected - all clear!</span>
        </div>
      </div>
    );
  }

  const { summary, alerts } = alertsData;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Alerts ({summary.total_alerts})
        </h2>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <SummaryCard
          label="Critical"
          count={summary.by_severity.critical}
          color="red"
          icon={AlertTriangle}
        />
        <SummaryCard
          label="High"
          count={summary.by_severity.high}
          color="orange"
          icon={AlertCircle}
        />
        <SummaryCard
          label="Medium"
          count={summary.by_severity.medium}
          color="yellow"
          icon={Info}
        />
        <SummaryCard
          label="Low"
          count={summary.by_severity.low}
          color="blue"
          icon={Shield}
        />
      </div>

      {/* Alerts List */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {alerts.map((alert) => (
          <AlertCard key={alert.id} alert={alert} />
        ))}
      </div>

      {alerts.length > 10 && (
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-3 text-center">
          Showing all {alerts.length} alerts
        </p>
      )}
    </div>
  );
}

// Helper component for summary cards
function SummaryCard({
  label,
  count,
  color,
  icon: Icon,
}: {
  label: string;
  count: number;
  color: 'red' | 'orange' | 'yellow' | 'blue';
  icon: any;
}) {
  const colorClasses = {
    red: 'bg-red-100 dark:bg-red-900/30 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300',
    orange: 'bg-orange-100 dark:bg-orange-900/30 border-orange-200 dark:border-orange-800 text-orange-700 dark:text-orange-300',
    yellow: 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-300',
    blue: 'bg-blue-100 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300',
  };

  return (
    <div className={`border rounded-lg p-3 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium opacity-80">{label}</p>
          <p className="text-2xl font-bold">{count}</p>
        </div>
        <Icon className="w-6 h-6 opacity-60" />
      </div>
    </div>
  );
}

// Helper component for individual alert cards
function AlertCard({ alert }: { alert: Alert }) {
  const severityConfig = {
    critical: {
      color: 'bg-red-100 dark:bg-red-900/30 border-red-300 dark:border-red-700 text-red-800 dark:text-red-200',
      badge: 'bg-red-600 text-white',
      icon: AlertTriangle,
    },
    high: {
      color: 'bg-orange-100 dark:bg-orange-900/30 border-orange-300 dark:border-orange-700 text-orange-800 dark:text-orange-200',
      badge: 'bg-orange-600 text-white',
      icon: AlertCircle,
    },
    medium: {
      color: 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-300 dark:border-yellow-700 text-yellow-800 dark:text-yellow-200',
      badge: 'bg-yellow-600 text-white',
      icon: Info,
    },
    low: {
      color: 'bg-blue-100 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700 text-blue-800 dark:text-blue-200',
      badge: 'bg-blue-600 text-white',
      icon: Shield,
    },
  };

  const config = severityConfig[alert.severity];
  const Icon = config.icon;

  return (
    <div className={`border rounded-lg p-4 ${config.color}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${config.badge}`}>
                {alert.severity.toUpperCase()}
              </span>
              <span className="text-xs font-medium">
                {formatAlertType(alert.alert_type)}
              </span>
            </div>
            <p className="text-sm font-medium mb-1">{alert.message}</p>
            <div className="flex items-center gap-3 text-xs opacity-75">
              <span>{formatTimestamp(alert.timestamp)}</span>
              <span>Frame #{alert.frame_id}</span>
              {alert.track_ids.length > 0 && (
                <span>Tracks: {alert.track_ids.join(', ')}</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Utilities
function formatAlertType(type: string): string {
  return type.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}

function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}
