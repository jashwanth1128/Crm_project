import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from './AuthContext';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const { token } = useAuth();

  useEffect(() => {
    if (!token) {
      if (socket) {
        socket.close();
        setSocket(null);
        setConnected(false);
      }
      return;
    }

    const wsUrl = process.env.REACT_APP_API_URL
      .replace('https', 'wss')
      .replace('http', 'ws');

    const ws = new WebSocket(`${wsUrl}/ws?token=${token}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error', err);
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [token]);

  return (
    <WebSocketContext.Provider value={{ socket, connected }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};
