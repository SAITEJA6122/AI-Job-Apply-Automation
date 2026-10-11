import { useWebSocket } from '../hooks/useWebSocket';
import { Activity, CheckCircle, AlertCircle } from 'lucide-react';

const RealTimeProgress = () => {
  const { isConnected, progress, status } = useWebSocket();

  if (!isConnected && !progress) {
    return null;
  }

  return (
    <div className="card bg-white dark:bg-gray-800 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Activity className="w-5 h-5 text-primary-600" />
          Live Progress
        </h3>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {progress && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">{progress.message}</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {Math.round(progress.progress)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress.progress}%` }}
            />
          </div>
        </div>
      )}

      {status && (
        <div className="mt-4 p-3 rounded-lg bg-gray-50 dark:bg-gray-700">
          <div className="flex items-center gap-2">
            {status.status === 'running' ? (
              <Activity className="w-4 h-4 text-blue-600 animate-spin" />
            ) : status.status === 'completed' ? (
              <CheckCircle className="w-4 h-4 text-green-600" />
            ) : (
              <AlertCircle className="w-4 h-4 text-yellow-600" />
            )}
            <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
              {status.status}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default RealTimeProgress;
