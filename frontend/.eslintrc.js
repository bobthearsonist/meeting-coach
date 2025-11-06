const path = require("path");

module.exports = {
  root: true,
  extends: "@react-native",
  env: {
    "jest/globals": true,
  },
  globals: {
    globalThis: "readonly",
  },
  parserOptions: {
    babelOptions: {
      configFile: path.join(__dirname, "babel.config.js"),
    },
  },
};
