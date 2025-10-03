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

### Usage

```bash
# Run the backend console application
make backend-dev

# Start frontend development server (when ready)
make frontend-dev

# Or run both simultaneously
make dev
```

## 🎮 Backend Console Application

The Python backend provides a terminal-based interface with real-time feedback:

```bash
cd backend
./run_with_venv.sh

# Or use Make
make backend-dev
```

See [backend/README.md](backend/README.md) for detailed backend documentation.

## 📱 Frontend UI (In Development)

The React Native frontend is currently a UI mockup showing the planned interface design. Integration with the Python backend is in progress.

See [frontend/README.md](frontend/README.md) for frontend documentation.

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

### Available Commands

```bash
# See all available commands
make help

# Installation
make install              # Install both backend and frontend
make backend-install      # Backend only
make frontend-install     # Frontend only

# Development
make dev                  # Start both backend and frontend
make backend-dev          # Run backend console app
make frontend-dev         # Start frontend Metro bundler

# Testing
make test                 # Run all tests
make backend-test         # Backend tests only
make frontend-test        # Frontend tests only
make test-fast            # Fast tests (no slow external deps)
make test-coverage        # Backend tests with coverage

# Code Quality
make lint                 # Lint all code
make format               # Format all code
make backend-lint         # Backend linting
make frontend-lint        # Frontend linting

# Cleanup
make clean                # Clean all temporary files
make backend-clean        # Clean backend files
make frontend-clean       # Clean frontend files

# Project Info
make status               # Show project structure and status
```

### Working with Individual Components

You can also work directly in each component:

```bash
# Backend (uses Make)
cd backend
make test
make lint
make format

# Frontend (uses npm)
cd frontend
npm start
npm test
npm run lint
```

## 🧪 Testing

Run comprehensive tests:

```bash
# Run all tests (backend + frontend)
make test

# Backend tests
make backend-test

# Fast tests only (useful during development)
make test-fast

# Tests with coverage report
make test-coverage
```

## ⚙️ Configuration

Backend configuration is in `backend/config.py`:

```python
# Audio settings
CHUNK_DURATION = 15          # Seconds per analysis chunk
WHISPER_MODEL = "base"       # Model size: tiny, base, small, medium, large

# Pace thresholds
PACE_TOO_FAST = 180         # Words per minute
PACE_TOO_SLOW = 100
PACE_IDEAL_MIN = 120
PACE_IDEAL_MAX = 160

# Analysis settings
MIN_WORDS_FOR_ANALYSIS = 10  # Minimum words before tone analysis
OLLAMA_MODEL = "llama3"      # LLM model for tone analysis
```

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

## 🔧 Troubleshooting

### No Audio Captured
- **Check BlackHole**: Run `cd backend && ./run_with_venv.sh --test-audio`
- **Verify Teams Setup**: Ensure Teams speaker is set to Multi-Output Device
- **Check Permissions**: macOS may require microphone permissions

### Slow Transcription
- **Use Smaller Model**: Set `WHISPER_MODEL = "tiny"` in backend/config.py
- **Increase Chunk Duration**: Set `CHUNK_DURATION = 20`
- **Use GPU**: Set `DEVICE = "cuda"` if available

### High CPU Usage
- **Optimize Whisper**: Set `COMPUTE_TYPE = "int8"` in backend/config.py
- **Reduce Analysis Frequency**: Increase `MIN_WORDS_FOR_ANALYSIS`
- **Use Smaller LLM**: Try a smaller Ollama model

### Ollama Issues
```bash
# Restart Ollama service
brew services restart ollama

# Check available models
ollama list

# Re-download model if needed
ollama pull llama3
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

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Faster-Whisper**: High-performance speech recognition
- **Ollama**: Local LLM inference
- **BlackHole**: Virtual audio driver
- **PyAudio**: Audio I/O library
- **React Native**: Cross-platform mobile framework
