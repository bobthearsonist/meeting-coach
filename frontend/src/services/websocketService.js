/**
 * Minimal WebSocket service built on top of reconnecting-websocket.
 *
 * LEARNING: Instead of reimplementing reconnection, queuing, and timeouts,
 * rely on a battle-tested client and expose a tiny, composable surface area for
 * hooks and context providers.
 */

import ReconnectingWebSocket from 'reconnecting-websocket';
import { WEBSOCKET } from '../utils/constants';

export const ConnectionStatus = {
  IDLE: 'idle',
  CONNECTING: 'connecting',
  OPEN: 'open',
  RECONNECTING: 'reconnecting',
  CLOSED: 'closed',
  ERROR: 'error',
};

const READY_STATE = {
  0: 'CONNECTING',
  1: 'OPEN',
  2: 'CLOSING',
  3: 'CLOSED',
};

const ANY_EVENT = '*';

let socket = null;
let connectPromise = null;
let resolveConnect = null;
let rejectConnect = null;
let currentConfig = { ...WEBSOCKET };

const listeners = new Map();
const statusListeners = new Set();

const connectionState = {
  status: ConnectionStatus.IDLE,
  attempts: 0,
  lastError: null,
  lastCloseEvent: null,
};

const emit = (event, payload) => {
  const eventListeners = listeners.get(event);
  if (eventListeners) {
    eventListeners.forEach((listener) => {
      try {
        listener(payload);
      } catch (error) {
        if (typeof __DEV__ !== 'undefined' && __DEV__) {
          console.error('[websocketService] listener error', error);
        }
      }
    });
  }

  if (event !== ANY_EVENT) {
    emit(ANY_EVENT, { event, payload });
  }
};

const notifyStatus = (status, extras = {}) => {
  connectionState.status = status;
  Object.assign(connectionState, extras);

  const snapshot = getConnectionState();
  statusListeners.forEach((listener) => {
    try {
      listener(snapshot);
    } catch (error) {
      if (typeof __DEV__ !== 'undefined' && __DEV__) {
        console.error('[websocketService] status listener error', error);
      }
    }
  });
};

const buildSocketOptions = (config) => ({
  constructor:
    typeof globalThis !== 'undefined' ? globalThis.WebSocket : undefined,
  minReconnectionDelay: Math.max(0, config.BASE_RECONNECT_DELAY_MS ?? 500),
  maxReconnectionDelay: Math.max(
    config.BASE_RECONNECT_DELAY_MS ?? 500,
    config.MAX_RECONNECT_DELAY_MS ?? 5000
  ),
  reconnectionDelayGrowFactor: config.RECONNECT_DELAY_GROWTH_FACTOR ?? 2,
  connectionTimeout: config.CONNECTION_TIMEOUT_MS ?? 4000,
  maxRetries: config.AUTO_RECONNECT
    ? config.MAX_RECONNECT_ATTEMPTS ?? Infinity
    : 0,
  debug: Boolean(config.DEBUG),
  WebSocket:
    typeof globalThis !== 'undefined' ? globalThis.WebSocket : undefined,
});

const withSocket = (fn) => {
  if (!socket) {
    throw new Error(
      'WebSocket has not been initialised. Call connect() first.'
    );
  }

  return fn(socket);
};

const handleConnecting = (event) => {
  const attempts =
    typeof event?.reconnectAttempts === 'number'
      ? event.reconnectAttempts
      : connectionState.attempts;
  notifyStatus(
    attempts > 0 ? ConnectionStatus.RECONNECTING : ConnectionStatus.CONNECTING,
    {
      attempts,
    }
  );
};

const handleOpen = () => {
  notifyStatus(ConnectionStatus.OPEN, { attempts: 0, lastError: null });

  if (resolveConnect) {
    resolveConnect(socket);
  }

  connectPromise = null;
  resolveConnect = null;
  rejectConnect = null;
};

const handleMessage = (event) => {
  const { data } = event;

  if (typeof data !== 'string') {
    emit('error', { error: new Error('Unsupported message type'), raw: data });
    return;
  }

  try {
    const parsed = JSON.parse(data);
    emit(parsed?.type ?? 'message', parsed);
  } catch (error) {
    connectionState.lastError = error;
    emit('error', { error, raw: data });
  }
};

const handleError = (event) => {
  const error = event?.message
    ? new Error(event.message)
    : event?.error ?? new Error('WebSocket error');
  connectionState.lastError = error;
  notifyStatus(ConnectionStatus.ERROR, { lastError: error });
  emit('error', { error, event });

  if (rejectConnect) {
    rejectConnect(error);
    connectPromise = null;
    resolveConnect = null;
    rejectConnect = null;
  }
};

const handleClose = (event) => {
  connectionState.lastCloseEvent = event;

  if (connectionState.status !== ConnectionStatus.CLOSED) {
    notifyStatus(ConnectionStatus.CLOSED, { lastCloseEvent: event });
  }

  if (rejectConnect) {
    rejectConnect(new Error('WebSocket connection closed before opening'));
    connectPromise = null;
    resolveConnect = null;
    rejectConnect = null;
  }

  if (!currentConfig.AUTO_RECONNECT) {
    cleanup();
  }
};

const attachHandlers = () => {
  if (!socket) {
    return;
  }

  socket.addEventListener('connecting', handleConnecting);
  socket.addEventListener('open', handleOpen);
  socket.addEventListener('message', handleMessage);
  socket.addEventListener('error', handleError);
  socket.addEventListener('close', handleClose);
};

const detachHandlers = () => {
  if (!socket) {
    return;
  }

  socket.removeEventListener('connecting', handleConnecting);
  socket.removeEventListener('open', handleOpen);
  socket.removeEventListener('message', handleMessage);
  socket.removeEventListener('error', handleError);
  socket.removeEventListener('close', handleClose);
};

const cleanup = () => {
  detachHandlers();
  socket = null;
  notifyStatus(ConnectionStatus.CLOSED);
};

export const connect = async (overrides = {}) => {
  if (socket && socket.readyState === 1) {
    return socket;
  }

  if (connectPromise) {
    return connectPromise;
  }

  currentConfig = { ...WEBSOCKET, ...overrides };

  const options = buildSocketOptions(currentConfig);
  socket = new ReconnectingWebSocket(
    currentConfig.URL,
    currentConfig.PROTOCOLS,
    options
  );
  attachHandlers();
  notifyStatus(ConnectionStatus.CONNECTING);

  connectPromise = new Promise((resolve, reject) => {
    resolveConnect = resolve;
    rejectConnect = reject;
  });

  return connectPromise;
};

export const disconnect = () => {
  if (!socket) {
    return;
  }

  const closingSocket = socket;
  detachHandlers();
  connectPromise = null;
  resolveConnect = null;
  rejectConnect = null;
  currentConfig = { ...WEBSOCKET };
  notifyStatus(ConnectionStatus.CLOSED);

  closingSocket.close();
  socket = null;
};

export const send = (message) =>
  withSocket((activeSocket) => {
    const payload =
      typeof message === 'string' ? message : JSON.stringify(message);
    activeSocket.send(payload);
  });

export const subscribe = (eventType, handler) => {
  if (typeof handler !== 'function') {
    throw new Error('subscribe requires a handler function');
  }

  const handlers = listeners.get(eventType) ?? new Set();
  handlers.add(handler);
  listeners.set(eventType, handlers);

  return () => {
    handlers.delete(handler);
    if (!handlers.size) {
      listeners.delete(eventType);
    }
  };
};

export const onStatusChange = (handler) => {
  if (typeof handler !== 'function') {
    throw new Error('onStatusChange requires a handler function');
  }

  statusListeners.add(handler);
  handler(getConnectionState());

  return () => {
    statusListeners.delete(handler);
  };
};

export const getSocket = () => socket;

export const getConnectionState = () => ({
  ...connectionState,
  readyState: socket?.readyState ?? 3,
  readyStateLabel: READY_STATE[socket?.readyState ?? 3],
  url: socket?.url ?? currentConfig.URL,
});

export const __reset = () => {
  detachHandlers();
  try {
    socket?.close?.();
  } catch (_) {
    // ignore close errors during test cleanup
  }

  socket = null;
  connectPromise = null;
  resolveConnect = null;
  rejectConnect = null;
  currentConfig = { ...WEBSOCKET };

  listeners.clear();
  statusListeners.clear();

  connectionState.status = ConnectionStatus.IDLE;
  connectionState.attempts = 0;
  connectionState.lastError = null;
  connectionState.lastCloseEvent = null;
};

export default {
  connect,
  disconnect,
  send,
  subscribe,
  onStatusChange,
  getSocket,
  getConnectionState,
  ConnectionStatus,
  __reset,
};
