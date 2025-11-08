"""
Configuration settings for Teams Meeting Coach
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Any, Dict

import yaml


# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file if it exists"""
    # Check for .env.test first (for CI/testing), then fall back to .env
    env_test_path = Path(__file__).parent.parent.parent / ".env.test"
    env_path = Path(__file__).parent.parent.parent / ".env"

    # In test/CI environments, prefer .env.test if it exists
    if env_test_path.exists() and (
        os.getenv("CI") == "true"
        or os.getenv("PYTEST_CURRENT_TEST")
        or "pytest" in sys.modules
    ):
        with open(env_test_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())
    elif env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())
    else:
        print("ERROR: .env file not found!", file=sys.stderr)
        print("Please copy .env.example to .env and configure it:", file=sys.stderr)
        print("  cp .env.example .env", file=sys.stderr)
        sys.exit(1)


load_env()

# WebSocket Server Settings (required)
WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST")
WEBSOCKET_PORT_STR = os.getenv("WEBSOCKET_PORT")

if not WEBSOCKET_HOST:
    print("ERROR: WEBSOCKET_HOST not defined in .env file", file=sys.stderr)
    print("Please add: WEBSOCKET_HOST=localhost", file=sys.stderr)
    sys.exit(1)

if not WEBSOCKET_PORT_STR:
    print("ERROR: WEBSOCKET_PORT not defined in .env file", file=sys.stderr)
    print("Please add: WEBSOCKET_PORT=3002", file=sys.stderr)
    sys.exit(1)

try:
    WEBSOCKET_PORT = int(WEBSOCKET_PORT_STR)
except ValueError:
    print(
        f"ERROR: WEBSOCKET_PORT must be a number, got: {WEBSOCKET_PORT_STR}",
        file=sys.stderr,
    )
    sys.exit(1)

# Audio Capture Settings
SAMPLE_RATE = 16000  # Whisper works best with 16kHz
CHUNK_DURATION = 5  # Seconds per transcription chunk
CHUNK_SIZE = 1024  # Audio frames per buffer
CHANNELS = 2  # Stereo for BlackHole

# Whisper Model Settings
WHISPER_MODEL = "tiny"  # Options: tiny, base, small, medium, large
COMPUTE_TYPE = "int8"  # Options: int8, float16, float32
DEVICE = "cpu"  # Options: cpu, cuda

# Analysis Settings
OLLAMA_MODEL = "gemma2:2b"  # LLM model for tone analysis
MIN_WORDS_FOR_ANALYSIS = 15  # Minimum words before analyzing (need sufficient context)
DEBUG_ANALYSIS = False  # Set to True to see raw LLM responses

# Speaking Pace Thresholds
PACE_TOO_FAST = 180  # Words per minute
PACE_TOO_SLOW = 100  # Words per minute
PACE_IDEAL_MIN = 120
PACE_IDEAL_MAX = 160

# Filler Words to Track
FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "actually", "literally"]

# Feedback Settings
FEEDBACK_HISTORY_SIZE = 5  # Number of recent chunks to keep
NOTIFICATION_COOLDOWN = 30  # Seconds between similar notifications

# Audio Input Mode
USE_MICROPHONE_INPUT = (
    True  # True = analyze YOUR speech, False = analyze Teams output audio
)
BLACKHOLE_DEVICE_INDEX = None  # Will auto-detect if None
MICROPHONE_DEVICE_INDEX = None  # Will prompt for selection if None

# Analysis Prompt Template - Specialized for Autism/ADHD Social Coaching
ANALYSIS_PROMPT = """Analyze this meeting transcript for social cues and emotional regulation patterns.
Focus on objective assessment to help someone with autism and ADHD understand their communication.

Text: "{text}"

Provide a VALID JSON response with properly formatted arrays (use commas between array elements):
1. emotional_state: "calm", "engaged", "elevated", "intense", "rapid", "distracted", "overwhelmed", or "overly_critical"
2. social_cues: "appropriate", "interrupting", "dominating", "monotone", "too_quiet", "off_topic", or "repetitive"
3. speech_pattern: "normal", "rushed", "rambling", "clear", "hesitant", "loud", or "quiet"
4. confidence: 0.0-1.0 (how certain you are of the assessment)
5. key_indicators: array of specific words/phrases (use commas between items: ["word1", "word2"])
6. coaching_feedback: practical, supportive suggestion if needed (one sentence, or "Continue as you are" if appropriate)

Assessment guidelines:
- Default to "calm" and "appropriate" for normal conversational speech
- Only flag "intense" or "elevated" if there are clear indicators like excitement, urgency, or emotional language
- Flag "overly_critical" for harsh, judgmental, or excessively negative language toward others or ideas
- Consider context - sharing accomplishments or explaining technical topics is often normal enthusiasm
- "engaged" is positive - someone actively participating in discussion
- Focus on patterns, not single words or phrases

Be conservative in flagging issues - most conversation should be assessed as appropriate."""


# Model Configuration


class ModelConfig:
    """Load and manage model configuration from YAML file with environment variable fallback."""

    def __init__(self, config_path: str = None, mode: str = None):
        """
        Initialize model configuration.

        Args:
            config_path: Path to YAML config file. If None, uses default location.
            mode: Model mode ('self_hosted' or 'local'). If None, reads from YAML or env var.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"

        self.config_path = Path(config_path)
        self._config = self._load_config() if self.config_path.exists() else {}

        # Override mode if provided
        if mode:
            self._config["model_mode"] = mode

        # Fallback to environment variables if YAML doesn't exist or lacks values
        self._mode = self._config.get("model_mode") or os.getenv(
            "MODEL_MODE", "self_hosted"
        )

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config file {self.config_path}: {e}")
            return {}

    def get_mode(self) -> str:
        """Get the configured model mode."""
        return self._mode

    def get_self_hosted_config(self) -> Dict[str, Any]:
        """Get self-hosted configuration with environment variable fallback."""
        yaml_config = self._config.get("self_hosted", {})
        return {
            "endpoint": yaml_config.get("endpoint")
            or os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434"),
            "model": yaml_config.get("model")
            or os.getenv("OLLAMA_MODEL", OLLAMA_MODEL),
            "timeout": yaml_config.get("timeout")
            or int(os.getenv("OLLAMA_TIMEOUT", "30")),
        }

    def get_local_config(self) -> Dict[str, Any]:
        """Get local model configuration with environment variable fallback."""
        yaml_config = self._config.get("local", {})
        return {
            "model_path": yaml_config.get("model_path")
            or os.getenv("LOCAL_MODEL_PATH", "models/tinyllama.gguf"),
            "threads": yaml_config.get("threads")
            or int(os.getenv("LOCAL_THREADS", "4")),
            "context_size": yaml_config.get("context_size")
            or int(os.getenv("LOCAL_CONTEXT_SIZE", "2048")),
        }

    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis settings with environment variable fallback."""
        yaml_config = self._config.get("analysis", {})
        return {
            "min_words": yaml_config.get("min_words", MIN_WORDS_FOR_ANALYSIS),
            "temperature": yaml_config.get("temperature")
            or float(os.getenv("MODEL_TEMPERATURE", "0.3")),
            "debug": yaml_config.get("debug", DEBUG_ANALYSIS),
        }
