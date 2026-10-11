import { useState, useEffect, useRef } from 'react';
import { Monitor, Maximize2, Minimize2, X } from 'lucide-react';

const LiveScreen = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [screenshotUrl, setScreenshotUrl] = useState<string | null>(null);
  const [hasScreenshots, setHasScreenshots] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const urlRef = useRef<string | null>(null);

  useEffect(() => {
    if (!isVisible) {
      // Clear interval and cleanup URL when hidden
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (urlRef.current) {
        URL.revokeObjectURL(urlRef.current);
        urlRef.current = null;
      }
      setScreenshotUrl(null);
      return;
    }

    // Load latest screenshot
    const loadScreenshot = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/screenshots/latest');

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
          // JSON response means no screenshot available yet
          const data = await response.json();
          setHasScreenshots(data.available || false);
          if (!data.available) {
            setScreenshotUrl(null);
          }
        } else if (contentType && contentType.includes('image')) {
          // Image response
          const blob = await response.blob();

          // Cleanup previous URL
          if (urlRef.current) {
            URL.revokeObjectURL(urlRef.current);
          }

          const url = URL.createObjectURL(blob);
          urlRef.current = url;
          setScreenshotUrl(url);
          setHasScreenshots(true);
        } else {
          throw new Error(`Unexpected content type: ${contentType}`);
        }
      } catch (error) {
        console.error('Error loading screenshot:', error);
        setError(error instanceof Error ? error.message : 'Failed to load screenshot');
        setHasScreenshots(false);
      } finally {
        setIsLoading(false);
      }
    };

    // Initial load
    loadScreenshot();

    // Refresh every 2 seconds
    intervalRef.current = setInterval(() => {
      loadScreenshot();
    }, 2000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (urlRef.current) {
        URL.revokeObjectURL(urlRef.current);
      }
    };
  }, [isVisible]);

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-20 right-4 bg-blue-600 dark:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors flex items-center gap-2 z-40"
      >
        <Monitor className="w-4 h-4" />
        Live Screen
      </button>
    );
  }

  return (
    <div
      className={`fixed bg-gray-900 dark:bg-black border border-gray-700 dark:border-gray-800 rounded-lg shadow-2xl z-50 ${
        isExpanded ? 'bottom-4 right-4 left-4 top-20' : 'bottom-20 right-4 w-[800px] h-[600px]'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 dark:bg-gray-900 border-b border-gray-700 dark:border-gray-800 rounded-t-lg">
        <div className="flex items-center gap-2">
          <Monitor className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-medium text-gray-200">Live Browser Screen</span>
          {hasScreenshots && (
            <span className="text-xs text-green-400">● Live</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-400 hover:text-gray-200"
            title={isExpanded ? 'Minimize' : 'Maximize'}
          >
            {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setIsVisible(false)}
            className="text-gray-400 hover:text-red-400"
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Screen Content */}
      <div className="relative w-full h-full bg-gray-800 flex items-center justify-center overflow-hidden">
        {isLoading && !screenshotUrl && !error && (
          <div className="text-gray-500 flex items-center gap-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            Loading screen...
          </div>
        )}

        {error && (
          <div className="text-red-400 text-center p-8">
            <Monitor className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Error loading screen</p>
            <p className="text-sm mt-2">{error}</p>
          </div>
        )}

        {!hasScreenshots && !isLoading && !error && (
          <div className="text-gray-500 text-center p-8">
            <Monitor className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No screen capture available</p>
            <p className="text-sm mt-2">Start automation to see live screen</p>
          </div>
        )}

        {screenshotUrl && (
          <img
            src={screenshotUrl}
            alt="Live Browser Screen"
            className="max-w-full max-h-full object-contain"
            onError={() => {
              setScreenshotUrl(null);
              setError('Failed to load image');
            }}
          />
        )}

        {isLoading && screenshotUrl && (
          <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
            Refreshing...
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveScreen;
