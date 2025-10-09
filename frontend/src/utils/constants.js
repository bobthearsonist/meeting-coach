/**
 * Application Constants
 *
 * LEARNING: Constants prevent "magic numbers" and strings throughout your code.
 * They make values self-documenting and easy to update in one place.
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000', // Python backend URL
  TIMEOUT: 10000, // 10 seconds
  RETRY_ATTEMPTS: 3,
};

// WebSocket configuration
export const WEBSOCKET = {
  URL: 'ws://localhost:3001',
  AUTO_RECONNECT: true,
  MAX_RECONNECT_ATTEMPTS: 10,
  BASE_RECONNECT_DELAY_MS: 1000,
  MAX_RECONNECT_DELAY_MS: 10000,
  RECONNECT_DELAY_GROWTH_FACTOR: 2,
  CONNECTION_TIMEOUT_MS: 5000,
  HEARTBEAT_INTERVAL_MS: 25000,
  HEARTBEAT_MESSAGE: {
    type: 'ping',
  },
  DEBUG: false,
};

// Polling intervals (in milliseconds)
export const POLLING = {
  DASHBOARD_UPDATE: 1000, // Update dashboard every 1 second
  SLOW_UPDATE: 5000, // Update less critical data every 5 seconds
  FAST_UPDATE: 500, // Very fast updates (if needed)
};

// Speech pace thresholds (words per minute)
export const SPEECH_PACE = {
  TOO_SLOW: 100,
  OPTIMAL_MIN: 120,
  OPTIMAL_MAX: 180,
  TOO_FAST: 200,
};

// Emotional state classifications
export const EMOTIONAL_STATES = [
  'calm',
  'engaged',
  'elevated',
  'intense',
  'overwhelmed',
  'neutral',
  'unknown',
];

// Social cue types
export const SOCIAL_CUES = ['appropriate', 'watch carefully', 'concerning'];

// Emoji mappings for emotional states
export const EMOTIONAL_EMOJIS = {
  calm: '🧘',
  engaged: '✨',
  elevated: '⬆️',
  intense: '🔥',
  overwhelmed: '😵‍💫',
  neutral: '😐',
  unknown: '❓',
};

// Timeline settings
export const TIMELINE = {
  DISPLAY_MINUTES: 5, // Show last 5 minutes
  MAX_ENTRIES: 50, // Keep max 50 entries in memory
  BUCKET_COUNT: 40, // Number of timeline segments to display
};

// Activity feed settings
export const ACTIVITY_FEED = {
  MAX_ITEMS: 10, // Show max 10 recent items
  TRUNCATE_LENGTH: 150, // Truncate long text after this many chars
};

// Filler words to track
export const FILLER_WORDS = [
  'um',
  'uh',
  'like',
  'you know',
  'basically',
  'actually',
  'literally',
  'so',
];

// Alert thresholds
export const ALERTS = {
  WPM_TOO_FAST: 200,
  WPM_TOO_SLOW: 100,
  FILLER_WORD_THRESHOLD: 5, // Alert if same filler word used 5+ times
  OVERWHELMED_DURATION: 30, // Alert if overwhelmed for 30+ seconds
};

// UI Constants
export const UI = {
  HEADER_HEIGHT: 60,
  ANIMATION_DURATION: 300,
  TOAST_DURATION: 3000,
  MAX_TEXT_WIDTH: 600,
};

// Date/Time formats
export const DATE_FORMATS = {
  TIME: 'HH:mm:ss',
  SHORT_TIME: 'HH:mm',
  DATE: 'MMM DD, YYYY',
  DATETIME: 'MMM DD, YYYY HH:mm:ss',
};

// Local storage keys
export const STORAGE_KEYS = {
  USER_PREFERENCES: '@meeting_coach:preferences',
  SESSION_HISTORY: '@meeting_coach:history',
  SETTINGS: '@meeting_coach:settings',
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Unable to connect to the backend. Is it running?',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  UNKNOWN_ERROR: 'An unexpected error occurred.',
  NO_DATA: 'No data available yet. Start speaking!',
};

// Success messages
export const SUCCESS_MESSAGES = {
  SESSION_STARTED: 'Session started successfully',
  SESSION_STOPPED: 'Session stopped',
  SETTINGS_SAVED: 'Settings saved',
};

export default {
  API_CONFIG,
  POLLING,
  SPEECH_PACE,
  EMOTIONAL_STATES,
  SOCIAL_CUES,
  EMOTIONAL_EMOJIS,
  TIMELINE,
  ACTIVITY_FEED,
  FILLER_WORDS,
  ALERTS,
  UI,
  DATE_FORMATS,
  STORAGE_KEYS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  WEBSOCKET,
};
