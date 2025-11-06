module.exports = {
  presets: ['module:@react-native/babel-preset'],
  plugins: [
    [
      'module:react-native-dotenv',
      {
        envName: 'APP_ENV',
        moduleName: '@env',
        path: process.env.NODE_ENV === 'test' ? '../.env.test' : '../.env',
        safe: false,
        allowUndefined: false,
        verbose: false,
      },
    ],
  ],
};
