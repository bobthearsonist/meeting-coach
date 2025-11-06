module.exports = {
  root: true,
  extends: '@react-native',
  env: {
    'jest/globals': true,
  },
  globals: {
    globalThis: 'readonly',
  },
};
