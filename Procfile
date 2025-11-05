backend: cd backend && source ../venv/bin/activate && python main.py
metro: cd frontend && npm start -- --port ${METRO_PORT}
macos: cd frontend && RCT_METRO_PORT=${METRO_PORT} npx react-native run-macos --no-packager; echo "App launched. Keeping process alive..."; tail -f /dev/null
