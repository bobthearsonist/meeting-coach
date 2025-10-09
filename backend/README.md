# Meeting Coach Backend

Real-time communication coach with emotional monitoring and speaking pace feedback for neurodivergent individuals.

## Architecture

**WebSocket-based Client-Server Architecture**

```
┌─────────────────────────────────────────────────┐
│         Backend (main.py - Port 8000)           │
│                                                 │
│  ┌──────────────┐    ┌──────────────┐         │
│  │ RealtimeSTT  │ -> │  Analyzer    │         │
│  │ (Audio)      │    │  (LLM)       │         │
│  └──────────────┘    └──────────────┘         │
│         ↓                    ↓                  │
│  ┌─────────────────────────────────┐          │
│  │   Timeline & State Tracking     │          │
│  └─────────────────────────────────┘          │
│         ↓                                       │
│  ┌─────────────────────────────────┐          │
│  │   WebSocket Broadcasting        │          │
│  └─────────────────────────────────┘          │
└─────────────────┬───────────────────────────────┘
                  ↓
    ┌─────────────┴─────────────┐
    ↓                           ↓
┌─────────────┐         ┌──────────────┐
│Console Client│         │React Native  │
│(console_     │         │App (frontend)│
│ client.py)   │         │              │
└─────────────┘         └──────────────┘
```

### Key Design Decisions

**WebSocket over HTTP/SSE**
- Bidirectional real-time communication with <100ms latency
- Supports multiple simultaneous clients (console + mobile app)
- Alternative considered: Server-Sent Events (SSE) - rejected due to one-way communication

**Single Engine, Multiple Clients**
- Eliminates code duplication, single source of truth
- Backend broadcasts, clients display - clean separation of concerns
- Before: Dual modes (console vs menu bar) with duplicated rendering logic

**Python with Async/Await**
- Native async support for WebSocket server + concurrent audio processing
- `asyncio` for WebSocket, `threading` for RealtimeSTT integration

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Audio Capture** | [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) | Best-in-class VAD (voice activity detection), automatic speech boundary detection |
| **LLM Analysis** | Ollama (llama2/mistral) | Privacy-first local LLM, no API costs, works offline |
| **WebSocket** | `websockets` 15.0.1 | Industry standard for real-time bidirectional communication |
| **Console UI** | Custom ANSI (colors.py, dashboard.py) | Full control over layout, real-time animations |
| **Timeline** | Custom state machine | Tracks emotional states over session |

## Setup

```bash
# Install dependencies (uses virtual environment automatically)
make install

# Or manually:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai) installed and running
- Microphone access

## Usage

### Start Backend Server

```bash
cd backend
python main.py
```

This starts:
- WebSocket server on `ws://localhost:8000`
- Audio capture from default microphone
- Real-time transcription & LLM analysis
- Broadcasting to all connected clients

### Connect Console Client

```bash
# In another terminal
cd backend
python console_client.py
```

The console client displays real-time updates:
- Transcription
- Emotional state (calm, engaged, anxious, etc.)
- Speaking pace (WPM)
- Filler word counts (um, uh, like)
- Coaching feedback
- Alerts (too fast, too many fillers, etc.)

## Testing

```bash
# Run all tests
make test

# Run fast unit tests only (no Ollama/audio hardware)
make test-unit

# Run with coverage
make test-coverage

# Format and lint
make format
make lint
```

### Test Organization

- **Unit tests** (`tests/unit/`) - Fast, mocked, no external dependencies
- **Integration tests** (`tests/integration/`) - End-to-end with real components

### Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Tests > 5 seconds
- `@pytest.mark.requires_ollama` - Needs Ollama server
- `@pytest.mark.requires_audio` - Needs audio hardware

## WebSocket Protocol

### Server → Client Messages

#### `meeting_update` - Full State Update
```json
{
  "type": "meeting_update",
  "emotional_state": "calm",
  "social_cue": "appropriate",
  "confidence": 0.9,
  "wpm": 150,
  "text": "Hello, this is a test",
  "coaching": "Great pace! Keep it up.",
  "alert": false,
  "filler_counts": {"um": 2, "uh": 1},
  "timestamp": 1696598400.123
}
```

#### `transcription` - New Speech Detected
```json
{
  "type": "transcription",
  "text": "Hello this is what I said",
  "wpm": 145,
  "word_count": 5,
  "timestamp": 1696598401.456
}
```

#### `emotion_update` - State Changed
```json
{
  "type": "emotion_update",
  "emotional_state": "engaged",
  "confidence": 0.85,
  "timestamp": 1696598402.789
}
```

#### `alert` - Coaching Alert
```json
{
  "type": "alert",
  "message": "Speaking too fast! Slow down.",
  "severity": "warning",
  "category": "pace",
  "timestamp": 1696598403.012
}
```

#### `session_status` - Session Started/Stopped
```json
{
  "type": "session_status",
  "status": "started",
  "message": "Session started",
  "timestamp": 1696598404.345
}
```

### Client → Server Messages

```json
{"type": "start_session", "config": {"model": "base", "language": "en"}}
{"type": "stop_session"}
{"type": "ping"}
```

## Project Structure

```
backend/
├── main.py                  # WebSocket server + MeetingCoach engine
├── ws_server.py            # WebSocket server implementation
├── console_client.py       # Console WebSocket client
├── analyzer.py             # LLM emotional analysis
├── transcriber.py          # RealtimeSTT wrapper
├── audio_capture.py        # Audio device management
├── timeline.py             # State tracking over time
├── dashboard.py            # Console UI rendering
├── colors.py               # ANSI color constants
├── config.py               # Configuration constants
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data
└── demos/                  # Demo applications
```

## Development

```bash
# Install dev dependencies
make install-dev

# Format code (black, isort)
make format

# Lint code (flake8, mypy)
make lint

# See all commands
make help
```
