// Jest setup for React Native testing

// Silence the warning: Animated: `useNativeDriver` is not supported
jest.mock('react-native/Libraries/Animated/NativeAnimatedHelper');

// Mock WebSocket for React Native environment
// This prevents "WebSocket is not defined" errors in tests
global.WebSocket = jest.fn().mockImplementation((url) => {
  return {
    url,
    readyState: 1, // OPEN
    send: jest.fn(),
    close: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  };
});

// Mock reconnecting-websocket with full event handling capabilities
// This prevents connection errors and allows tests to dispatch events
jest.mock('reconnecting-websocket', () => {
  const instances = [];

  const Mock = jest.fn().mockImplementation(() => {
    const listeners = new Map();

    const socket = {
      readyState: 0,
      url: 'ws://localhost:8000',
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

// Optional: Suppress console warnings during tests
// global.console = {
//   ...console,
//   error: jest.fn(),
//   warn: jest.fn(),
// };
