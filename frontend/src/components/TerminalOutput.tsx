import { useState, useEffect, useRef } from 'react';
import { Terminal, X, Maximize2, Minimize2 } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

interface TerminalLine {
  id: number;
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error' | 'warning';
}

const TerminalOutput = () => {
  const [lines, setLines] = useState<TerminalLine[]>([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const lineIdRef = useRef(0);
  const { progress } = useWebSocket();

  useEffect(() => {
    // Auto-scroll to bottom when new lines are added
    if (endRef.current) {
      endRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [lines]);

  // Add real logs from WebSocket progress
  useEffect(() => {
    if (progress && progress.message && isVisible) {
      let type: TerminalLine['type'] = 'info';
      const message = progress.message.toLowerCase();

      if (message.includes('error') || message.startsWith('error:')) {
        type = 'error';
      } else if (message.includes('applied') || message.includes('success')) {
        type = 'success';
      } else if (message.includes('warning') || message.includes('captcha') || message.includes('rate limit')) {
        type = 'warning';
      }

      addLine(progress.message, type);
    }
  }, [progress, isVisible]);

  const addLine = (message: string, type: TerminalLine['type']) => {
    const newLine: TerminalLine = {
      id: lineIdRef.current++,
      timestamp: new Date().toLocaleTimeString(),
      message,
      type,
    };
    setLines(prev => [...prev, newLine]);
  };

  const getLineColor = (type: TerminalLine['type']) => {
    switch (type) {
      case 'success':
        return 'text-green-600 dark:text-green-400';
      case 'error':
        return 'text-red-600 dark:text-red-400';
      case 'warning':
        return 'text-yellow-600 dark:text-yellow-400';
      default:
        return 'text-gray-700 dark:text-gray-300';
    }
  };

  const clearLines = () => {
    setLines([]);
  };

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-4 bg-gray-800 dark:bg-gray-700 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-gray-700 dark:hover:bg-gray-600 transition-colors flex items-center gap-2"
      >
        <Terminal className="w-4 h-4" />
        Show Terminal
      </button>
    );
  }

  return (
    <div
      className={`fixed bg-gray-900 dark:bg-black border border-gray-700 dark:border-gray-800 rounded-lg shadow-2xl z-50 ${
        isExpanded ? 'bottom-4 right-4 left-4 top-20' : 'bottom-4 right-4 w-96 h-80'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 dark:bg-gray-900 border-b border-gray-700 dark:border-gray-800 rounded-t-lg">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-green-400" />
          <span className="text-sm font-medium text-gray-200">Terminal Output</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={clearLines}
            className="text-gray-400 hover:text-gray-200 text-xs"
            title="Clear"
          >
            Clear
          </button>
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

      {/* Terminal Content */}
      <div className="p-4 h-full overflow-y-auto font-mono text-sm">
        {lines.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            Waiting for output...
          </div>
        ) : (
          <div className="space-y-1">
            {lines.map((line) => (
              <div key={line.id} className="flex gap-2">
                <span className="text-gray-500 select-none">[{line.timestamp}]</span>
                <span className={getLineColor(line.type)}>{line.message}</span>
              </div>
            ))}
            <div ref={endRef} />
          </div>
        )}
      </div>
    </div>
  );
};

export default TerminalOutput;
