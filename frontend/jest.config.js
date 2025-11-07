// REGRESSION TESTING CONFIGURATION
// =================================
// This Jest configuration ensures ALL tests run every time.
// DO NOT add selective testing options like --onlyChanged or --changedSince.
// See TESTING_STRATEGY.md for rationale.

module.exports = {
  preset: 'react-native',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|reconnecting-websocket)/)',
  ],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  moduleFileExtensions: ['js', 'jsx', 'json', 'node'],

  // Coverage configuration (for PRs only, not required to pass)
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/**/*.test.{js,jsx}',
    '!src/**/index.js',
  ],
  coverageReporters: ['text', 'lcov', 'json-summary'],
  coverageThresholds: {
    // No thresholds - coverage is for insight, not gating
    // See TESTING_STRATEGY.md for details
  },

  // Test execution settings
  testMatch: ['**/*.test.js', '**/*.test.jsx'],
  testPathIgnorePatterns: ['/node_modules/', '/macos/'],
  verbose: true,

  // Performance settings
  maxWorkers: '50%', // Use half of available cores
};
