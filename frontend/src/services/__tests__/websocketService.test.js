import ReconnectingWebSocket from 'reconnecting-websocket';
import {
  connect,
  disconnect,
  send,
  subscribe,
  onStatusChange,
  getSocket,
  getConnectionState,
  ConnectionStatus,
  __reset,
} from '../websocketService';

jest.mock('reconnecting-websocket', () => {
  const instances = [];

  const Mock = jest.fn().mockImplementation(() => {
    const listeners = new Map();

    const socket = {
      readyState: 0,
      url: 'ws://localhost:3001',
      send: jest.fn(),
      close: jest.fn(),
      addEventListener: jest.fn((event, handler) => {
        const handlers = listeners.get(event) ?? new Set();
        handlers.add(handler);
        listeners.set(event, handlers);
      }),
      removeEventListener: jest.fn((event, handler) => {
        const handlers = listeners.get(event);
        handlers?.delete(handler);
      }),
      dispatch(event, payload) {
        const handlers = listeners.get(event);
        handlers?.forEach((handler) => handler(payload));
      },
    };

    instances.push(socket);
    return socket;
  });

  Mock.__getInstances = () => instances;
  Mock.__clearInstances = () => instances.splice(0, instances.length);

  return Mock;
});

const getMockSocket = () => {
  const instances = ReconnectingWebSocket.__getInstances();
  if (!instances.length) {
    throw new Error('No mock sockets created');
  }

  return instances[instances.length - 1];
};

describe('websocketService', () => {
  beforeAll(() => {
    global.__DEV__ = false;
  });

  beforeEach(() => {
    jest.useFakeTimers();
    ReconnectingWebSocket.__clearInstances();
    global.WebSocket = function MockNativeWebSocket(url, protocols, options) {
      return { url, protocols, options };
    };
    global.WebSocket.OPEN = 1;
    global.WebSocket.CLOSED = 3;
  });

  afterEach(() => {
    disconnect();
    __reset();
    jest.clearAllTimers();
    jest.useRealTimers();
    jest.clearAllMocks();
    delete global.WebSocket;
  });

  it('resolves connect promise on open and allows sending messages', async () => {
    const connectPromise = connect();
    const socket = getMockSocket();

    socket.readyState = 1;
    socket.dispatch('open');

    await expect(connectPromise).resolves.toBe(socket);

    send({ type: 'ping' });
    expect(socket.send).toHaveBeenCalledWith(JSON.stringify({ type: 'ping' }));
  });

  it('dispatches parsed payloads to subscribers', async () => {
    const handler = jest.fn();
    const unsubscribe = subscribe('meeting_update', handler);

    const connectPromise = connect({ AUTO_RECONNECT: false });
    const socket = getMockSocket();
    socket.readyState = 1;
    socket.dispatch('open');
    await connectPromise;

    const payload = { type: 'meeting_update', text: 'hello world' };
    socket.dispatch('message', { data: JSON.stringify(payload) });

    expect(handler).toHaveBeenCalledWith(payload);

    unsubscribe();
    socket.dispatch('message', { data: JSON.stringify(payload) });
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('notifies status listeners during connect and reconnect cycles', async () => {
    const statuses = [];
    const unsubscribeStatus = onStatusChange((snapshot) => {
      statuses.push(snapshot.status);
    });

    const connectPromise = connect();
    const socket = getMockSocket();

    socket.readyState = 1;
    socket.dispatch('open');
    await connectPromise;

    socket.dispatch('connecting', { reconnectAttempts: 1 });

    expect(statuses).toEqual([
      ConnectionStatus.IDLE,
      ConnectionStatus.CONNECTING,
      ConnectionStatus.OPEN,
      ConnectionStatus.RECONNECTING,
    ]);

    unsubscribeStatus();
  });

  it('cleans up on disconnect', async () => {
    const connectPromise = connect();
    const socket = getMockSocket();
    socket.readyState = 1;
    socket.dispatch('open');
    await connectPromise;

    disconnect();

    expect(socket.close).toHaveBeenCalled();
    expect(getSocket()).toBeNull();
    expect(getConnectionState().status).toBe(ConnectionStatus.CLOSED);
  });
});
