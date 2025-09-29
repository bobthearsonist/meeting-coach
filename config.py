"""
Configuration settings for Teams Meeting Coach
"""

# Audio Capture Settings
SAMPLE_RATE = 16000  # Whisper works best with 16kHz
CHUNK_DURATION = 15  # Seconds per transcription chunk
CHANNELS = 2  # Stereo for BlackHole

# Whisper Model Settings
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
COMPUTE_TYPE = "int8"  # Options: int8, float16, float32
DEVICE = "cpu"  # Options: cpu, cuda

# Analysis Settings
OLLAMA_MODEL = "llama3:8b"  # LLM model for tone analysis
MIN_WORDS_FOR_ANALYSIS = 10  # Minimum words before analyzing

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
USE_MICROPHONE_INPUT = True  # True = analyze YOUR speech, False = analyze Teams output audio
BLACKHOLE_DEVICE_INDEX = None  # Will auto-detect if None
MICROPHONE_DEVICE_INDEX = None  # Will auto-detect if None

# Analysis Prompt Template
ANALYSIS_PROMPT = """Analyze this meeting transcript segment:
"{text}"

Provide a JSON response with:
1. tone: "supportive", "dismissive", "neutral", "aggressive", or "passive"
2. confidence: 0.0-1.0
3. key_indicators: list of phrases that influenced the assessment
4. suggestions: brief feedback (one sentence)

Be concise and focus on actionable feedback."""
