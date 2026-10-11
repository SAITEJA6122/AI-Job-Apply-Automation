import { useEffect, useState, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

interface ProgressUpdate {
  message: string;
  progress: number;
  timestamp: string;
}

interface StatusUpdate {
  status: string;
  timestamp: string;
}

export const useWebSocket = (url: string = 'http://localhost:5000') => {
  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [status, setStatus] = useState<StatusUpdate | null>(null);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    // Create socket connection
    socketRef.current = io(url);

    socketRef.current.on('connect', () => {
      console.log('Connected to WebSocket server');
      setIsConnected(true);
    });

    socketRef.current.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
      setIsConnected(false);
    });

    socketRef.current.on('automation_progress', (data: ProgressUpdate) => {
      console.log('WebSocket progress:', data);
      setProgress(data);
    });

    socketRef.current.on('automation_status', (data: StatusUpdate) => {
      console.log('WebSocket status:', data);
      setStatus(data);
    });

    // Subscribe to automation updates
    socketRef.current.emit('subscribe_automation');

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [url]);

  const subscribeToAutomation = () => {
    if (socketRef.current) {
      socketRef.current.emit('subscribe_automation');
    }
  };

  return {
    isConnected,
    progress,
    status,
    subscribeToAutomation,
  };
};
