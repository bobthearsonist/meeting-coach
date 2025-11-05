# Teams Meeting Coach

🎯 **Real-time AI coaching for Microsoft Teams meetings**

A powerful real-time meeting feedback system that captures Teams audio, transcribes speech, and provides live coaching on speaking pace, tone, and communication effectiveness.

## 🏗️ Project Structure (Monorepo)

This project is organized as a monorepo with two main components:

```
teams-meeting-coach/
├── backend/              # Python console application & analysis engine
│   ├── main.py          # Console application entry point
│   ├── analyzer.py      # AI-powered communication analysis
│   ├── transcriber.py   # Real-time speech-to-text
│   ├── tests/           # Comprehensive test suite
│   └── README.md        # Backend documentation
├── frontend/            # React Native UI (in development)
│   ├── src/
│   │   └── components/
│   └── README.md        # Frontend documentation
├── docs/                # Shared documentation
├── Makefile            # Monorepo orchestration
└── README.md           # This file
```

## ✨ Features

- **🎤 Live Audio Capture**: Captures Teams audio via BlackHole virtual audio device
- **📝 Real-time Transcription**: Uses Faster-Whisper for streaming speech-to-text
- **⏱️ Speaking Pace Analysis**: Monitors words per minute with smart alerts
- **🎭 Tone Detection**: AI-powered analysis of communication style and sentiment
- **🔄 Filler Word Tracking**: Counts and reports usage of "um", "uh", "like", etc.
- **📊 Live Feedback Display**: Clean console interface (UI app in development)
- **🤖 Local AI Processing**: Uses Ollama for private, offline tone analysis

## 🚀 Quick Start

### Prerequisites

- **macOS** (required for React Native macOS app)
- **Homebrew** (for installing dependencies)
- **Node.js 20+** (for frontend)
- **Python 3.12+** (for backend)
- **Overmind** (process manager for development)

```bash
brew install overmind
```

### Installation

```bash
# Clone the repository
git clone <your-repo>
cd teams-meeting-coach

# Install both backend and frontend
make install

# Or install individually
make backend-install    # Python backend only
make frontend-install   # React Native frontend only
```

The backend installation will:
- Install BlackHole audio driver
- Install Ollama and download the LLM model
- Set up Python virtual environment
- Install all dependencies
- Run setup verification

### Configuration

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

**.env file (all values required):**
```bash
# Backend WebSocket Server
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=3002

# Frontend Metro Bundler
METRO_PORT=8082
```

**⚠️ Important:** All environment variables are required. The application will fail to start if any are missing.

### Usage

**Start everything:**

```bash
make run
```

This starts the backend server, Metro bundler, and macOS app.

**Control processes:**

```bash
overmind connect macos    # View app logs
overmind restart macos    # Restart the app
Ctrl+C                    # Stop all processes
```

Run `make help` for more commands. See `overmind help` for process management options.

## 🎮 Backend

The Python backend runs a WebSocket server on port 3002 (configurable), broadcasting real-time meeting analysis to connected clients:

```bash
make run backend
```

**Key features:**

- WebSocket API on `ws://localhost:3002` (or configured port)
- Real-time audio capture and transcription
- AI-powered tone analysis via Ollama
- Emotional timeline tracking

See [backend/README.md](backend/README.md) for architecture details, configuration, and API documentation.

## 📱 Frontend

React Native macOS app that connects to the backend WebSocket server:

```bash
make run metro    # Start Metro bundler
make run macos    # Launch macOS app
```

**Current status:** UI mockup with WebSocket integration in progress.

See [frontend/README.md](frontend/README.md) for setup, component structure, and development workflow.

## 🎵 Audio Configuration

**Critical**: You must configure audio routing for the coach to hear Teams audio:

1. **Open Audio MIDI Setup** (Applications → Utilities)
2. **Create Multi-Output Device**: Click `+` → "Create Multi-Output Device"
3. **Configure the Multi-Output**:
   - ✅ Check "BlackHole 2ch"
   - ✅ Check your speakers/headphones
   - Set drift correction if needed
4. **Configure Teams**:
   - Teams Settings → Devices
   - Set **Speaker** to your Multi-Output Device
   - Keep **Microphone** as your preferred mic

This setup allows the coach to "listen" to Teams audio while you still hear everything normally.

## 📊 What You'll See

The coach provides real-time feedback on:

### Speaking Pace
- 🐢 **Too Slow** (< 100 WPM): "Consider picking up the pace"
- ✅ **Ideal** (120-160 WPM): "Great pace!"
- 🐇 **Too Fast** (> 180 WPM): "Try to slow down"

### Communication Tone
- 🤝 **Supportive**: Collaborative and encouraging language
- 🙄 **Dismissive**: Language that might shut down discussion
- 😤 **Aggressive**: Forceful or confrontational tone
- 😐 **Neutral**: Professional, matter-of-fact communication

### Filler Words
Real-time tracking of: "um", "uh", "like", "you know", "basically", "actually", "literally"

## 🛠️ Development

```bash
make help    # See all available commands
```

**Common tasks:**
- `make run` - Start full environment
- `make test` - Run all tests
- `make lint` - Lint all code
- `make check-ports` - Debug WebSocket connection issues

**Component-specific:**
- `make backend-test` - Backend tests only
- `make frontend-test` - Frontend tests only
- `make backend-install` - Reinstall backend dependencies
- `make frontend-install` - Reinstall frontend dependencies

For detailed development workflows, see:
- Backend: [backend/README.md](backend/README.md)
- Frontend: [frontend/README.md](frontend/README.md)

## 🧪 Testing

Run comprehensive tests:

```bash
# Run all tests (backend + frontend)
make test

# Backend tests
make backend-test

# Tests with coverage report
make test-coverage
```

## ⚙️ Configuration

Application configuration is managed through code constants in each component:

**Backend:** `backend/src/config.py`

Key settings:
- `WHISPER_MODEL` - Transcription model size (tiny/base/small/medium/large)
- `OLLAMA_MODEL` - LLM for tone analysis (default: gemma2:2b)
- `PACE_THRESHOLDS` - WPM thresholds for pace alerts
- `MIN_WORDS_FOR_ANALYSIS` - Minimum words before analysis
- `WEBSOCKET_HOST` / `WEBSOCKET_PORT` - Server configuration (from .env)

**Frontend:** `frontend/src/utils/constants.js`

Key settings:
- `WEBSOCKET.URL` - Backend WebSocket URL (built from .env)
- `WEBSOCKET.AUTO_RECONNECT` - Auto-reconnect on disconnect
- `WEBSOCKET.MAX_RECONNECT_ATTEMPTS` - Maximum reconnection attempts

See [backend/README.md](backend/README.md#configuration) for complete configuration options.

## 🏗️ Architecture

```
Microsoft Teams Audio
          ↓
    BlackHole Driver
          ↓
     Audio Capture (PyAudio)
          ↓
    Faster-Whisper Transcription
          ↓
    ┌─────────────┬─────────────┐
    │             │             │
Pace Analysis  Filler Words  Tone Analysis
    │             │         (Ollama LLM)
    └─────────────┼─────────────┘
                  ↓
            Feedback Display
         (Console / React Native UI)
```

## 🔒 Privacy & Security

- **Local Processing**: All analysis runs locally on your machine
- **No Cloud Services**: Audio never leaves your computer
- **No Data Storage**: Transcriptions are processed in real-time and discarded
- **Open Source**: Full code transparency

## 🎯 Use Cases

- **Meeting Facilitation**: Get real-time feedback on speaking pace and tone
- **Presentation Practice**: Monitor your delivery during practice sessions
- **Communication Training**: Build awareness of speaking habits
- **Accessibility**: Real-time transcription for hearing assistance
- **Neurodivergent Support**: Helpful for ADHD and autism spectrum individuals

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run `make lint` and `make test`
6. Submit a pull request

This project follows [Conventional Commits](https://www.conventionalcommits.org/) for commit messages (e.g., `feat:`, `fix:`, `docs:`, `chore:`).

## 📄 License

Apache 2.0 with Commons Clause - see LICENSE file for details.

**Summary**: Free for personal, educational, and internal use. Commercial use (selling the software or offering it as a paid service) requires a separate commercial license.

## 🙏 Acknowledgments

- **Faster-Whisper**: High-performance speech recognition
- **Ollama**: Local LLM inference
- **BlackHole**: Virtual audio driver
- **PyAudio**: Audio I/O library
- **React Native**: Cross-platform mobile framework
---

**For detailed project status, architecture decisions, and next steps, see [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**
