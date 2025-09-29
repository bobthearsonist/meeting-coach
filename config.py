"""
Configuration settings for Teams Meeting Coach
"""

# Audio Capture Settings
SAMPLE_RATE = 16000  # Whisper works best with 16kHz
CHUNK_DURATION = 5  # Seconds per transcription chunk
CHANNELS = 2  # Stereo for BlackHole

# Whisper Model Settings
WHISPER_MODEL = "tiny"  # Options: tiny, base, small, medium, large
COMPUTE_TYPE = "int8"  # Options: int8, float16, float32
DEVICE = "cpu"  # Options: cpu, cuda

# Analysis Settings
OLLAMA_MODEL = "gemma2:2b"  # LLM model for tone analysis
MIN_WORDS_FOR_ANALYSIS = 5  # Minimum words before analyzing

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
MICROPHONE_DEVICE_INDEX = None  # Will prompt for selection if None

# Analysis Prompt Template
ANALYSIS_PROMPT = """Analyze this meeting transcript segment for communication tone. Be conservative and precise in your assessment:

"{text}"

Guidelines for tone classification:
- NEUTRAL: Default for factual statements, data presentations, or emotionally flat content
- SUPPORTIVE: Clear encouragement, appreciation, or positive reinforcement (e.g., "great idea", "I appreciate")
- DISMISSIVE: Explicit rejection or disregard (e.g., "whatever", "I don't care", outright dismissal)
- AGGRESSIVE: Hostile language, personal attacks, or confrontational phrasing
- PASSIVE: Withdrawn, reluctant participation, or avoiding responsibility

IMPORTANT:
- Factual statements and brief responses should typically be NEUTRAL
- Only flag as problematic (dismissive/aggressive/passive) when tone is clearly evident
- Be conservative with confidence scores - use lower confidence (0.3-0.6) for borderline cases
- Higher confidence (0.7+) only for clear, unambiguous tone indicators

Provide a JSON response with:
1. tone: "supportive", "dismissive", "neutral", "aggressive", or "passive"
2. confidence: 0.0-1.0 (be conservative)
3. key_indicators: specific phrases that influenced the assessment
4. suggestions: brief feedback (one sentence) or "No specific feedback needed" for neutral content"""
