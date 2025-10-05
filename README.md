# Teams Meeting Coach

🎯 **Real-time AI coaching for Microsoft Teams meetings**

A powerful real-time meeting feedback system that captures Teams audio, transcribes speech, and provides live coaching on speaking pace, tone, and communication effectiveness.

## ✨ Features

- **🎤 Live Audio Capture**: Captures Teams audio via BlackHole virtual audio device
- **📝 Real-time Transcription**: Uses Faster-Whisper for streaming speech-to-text
- **⏱️ Speaking Pace Analysis**: Monitors words per minute with smart alerts
- **🎭 Tone Detection**: AI-powered analysis of communication style and sentiment
- **🔄 Filler Word Tracking**: Counts and reports usage of "um", "uh", "like", etc.
- **📊 Live Feedback Display**: Clean menu bar app or console interface
- **🤖 Local AI Processing**: Uses Ollama for private, offline tone analysis

## 🚀 Quick Start

### Automated Installation (Recommended)

```bash
git clone <your-repo>
cd teams-meeting-coach
chmod +x install_deps.sh
./install_deps.sh
```

This script will:
- Install BlackHole audio driver
- Install Ollama and download the LLM model
- Set up Python virtual environment
- Install all dependencies
- Run setup verification

### Manual Installation

1. **Install System Dependencies**
   ```bash
   # Install BlackHole audio driver
   brew install blackhole-2ch

   # Install Ollama for AI analysis
   brew install ollama
   ```

2. **Set Up Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Ollama**
   ```bash
   brew services start ollama
   ollama pull llama3
   ```

4. **Verify Setup**
   ```bash
   python setup_check.py
   ```

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

## 🎮 Usage

### Menu Bar App (Recommended)
```bash
./run_with_venv.sh
```

### Console Mode
```bash
./run_with_venv.sh --console
```

### Test Audio Setup
```bash
./run_with_venv.sh --test-audio
```

### Test Transcription
```bash
./run_with_venv.sh --test-transcription
```

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

## ⚙️ Configuration

Edit `config.py` to customize:

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
         (Menu Bar / Console)
```

## 🧪 Testing

Run comprehensive tests:

```bash
# Test individual components
python test_transcription.py
python test_analyzer.py

# Test complete pipeline
python test_end_to_end.py

# Verify setup
python setup_check.py
```

## 🛠️ Development Setup

This project uses a Python virtual environment and Make for task automation.

### Virtual Environment Configuration

The project includes automatic virtual environment detection through:

- **`.python-version`** - Specifies Python 3.12+ requirement (similar to `.nvmrc` for Node.js)
- **VS Code settings** (`.vscode/settings.json`) - Automatically activates venv in integrated terminal
- **Shell scripts** - `run_with_venv.sh` and `run_tests_venv.sh` handle activation
- **Make targets** - All Python commands automatically use the virtual environment

### Development Commands

Use Make for all development tasks:

```bash
# Install dependencies
make install

# Run tests
make test                # All tests
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-fast          # Fast tests (no slow external deps)

# Code quality
make lint               # Linting
make format             # Code formatting

# Run demos
make run-demos          # All demonstration scripts
```

### Direct Virtual Environment Usage

If you need to run Python commands directly:

```bash
# Use the convenience scripts
./run_with_venv.sh python script.py
./run_tests_venv.sh test_module.py

# Or manually activate
source venv/bin/activate
python script.py
```

### Environment Files

- **`.python-version`** - Python version requirement (for pyenv, VS Code, etc.)
- **`requirements.txt`** - Python dependencies
- **`Makefile`** - Development task automation
- **`.vscode/settings.json`** - VS Code Python configuration

## 🔧 Troubleshooting

### No Audio Captured
- **Check BlackHole**: Run `./run_with_venv.sh --test-audio`
- **Verify Teams Setup**: Ensure Teams speaker is set to Multi-Output Device
- **Check Permissions**: macOS may require microphone permissions

### Slow Transcription
- **Use Smaller Model**: Set `WHISPER_MODEL = "tiny"` in config.py
- **Increase Chunk Duration**: Set `CHUNK_DURATION = 20` in config.py
- **Use GPU**: Set `DEVICE = "cuda"` if available

### High CPU Usage
- **Optimize Whisper**: Set `COMPUTE_TYPE = "int8"` in config.py
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

### Audio Device Issues
```bash
# List all audio devices
./run_with_venv.sh --test-audio

# Manually set device in config.py
BLACKHOLE_DEVICE_INDEX = 7  # Use index from test output
```

## 📁 Project Structure

```
teams-meeting-coach/
├── main.py              # Main application entry point
├── audio_capture.py     # BlackHole audio capture
├── transcriber.py       # Faster-Whisper integration
├── analyzer.py          # Ollama tone analysis
├── feedback_display.py  # Menu bar and console UI
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── run_with_venv.sh    # Convenient runner script
├── install_deps.sh     # Automated installation
├── setup_check.py      # Setup verification
└── test_*.py          # Test scripts
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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

Apache 2.0 with Commons Clause - see LICENSE file for details.

**Summary**: Free for personal, educational, and internal use. Commercial use (selling the software or offering it as a paid service) requires a separate commercial license.

## 🙏 Acknowledgments

- **Faster-Whisper**: High-performance speech recognition
- **Ollama**: Local LLM inference
- **BlackHole**: Virtual audio driver
- **PyAudio**: Audio I/O library
- **Rumps**: macOS menu bar apps in Python
