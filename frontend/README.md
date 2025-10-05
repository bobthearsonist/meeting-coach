# Meeting Coach Frontend

React Native macOS frontend for the Teams Meeting Coach application.

## Prerequisites

- **Node.js 20.19.4** (use `nvm use` to switch to the correct version)
- **Xcode** (for macOS development)
- **CocoaPods** (`gem install cocoapods`)
- **Watchman** (`brew install watchman`)

## Setup

```bash
# Use the correct Node.js version
nvm use

# Install dependencies
npm install

# Install CocoaPods dependencies (macOS)
cd macos && pod install && cd ..
```

## Development

```bash
# Start Metro bundler (in one terminal)
npm start

# Run on macOS (in another terminal)
npm run macos

# Or run without packager if Metro is already running
npx react-native run-macos --no-packager
```

## Testing

```bash
npm test
```

## Structure

```text
src/
├── components/
│   └── MeetingCoachUI.jsx    # Main emotional monitoring UI
App.js                        # Main app entry point
index.js                      # React Native app registration
macos/                        # macOS-specific Xcode project
```

## Notes

This React Native macOS app provides a native desktop interface for the Teams Meeting Coach with:
- Live emotional monitoring dashboard
- Real-time status indicators (emotional state, social cues, confidence, speech pace)
- Emotional timeline visualization
- Recent activity log
- Native macOS window integration

Integration with the Python backend for live audio analysis is planned.
