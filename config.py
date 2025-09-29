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
MIN_WORDS_FOR_ANALYSIS = 15  # Minimum words before analyzing; 15 words typically provide enough context for meaningful tone and social cue analysis.

# Speaking Pace Thresholds
PACE_TOO_FAST = 180  # Words per minute
PACE_TOO_SLOW = 100  # Words per minute
PACE_IDEAL_MIN = 120
PACE_IDEAL_MAX = 160

# Filler Words to Track
FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "actually", "literally"]

# Feedback Settings
FEEDBACK_HISTORY_SIZE = 10  # Number of recent chunks to keep (increased for better context)
NOTIFICATION_COOLDOWN = 30  # Seconds between similar notifications

# Timeline Display Settings
TIMELINE_ALERT_WEIGHT_THRESHOLD = 0.3  # Alert states need this much of bucket duration to dominate

# Audio Input Mode
USE_MICROPHONE_INPUT = True  # True = analyze YOUR speech, False = analyze Teams output audio
BLACKHOLE_DEVICE_INDEX = None  # Will auto-detect if None
MICROPHONE_DEVICE_INDEX = None  # Will prompt for selection if None

# Analysis Prompt Template - Specialized for Autism/ADHD Social Coaching
ANALYSIS_PROMPT = """Analyze this meeting transcript for social cues and emotional regulation patterns.
Focus on objective assessment to help someone with autism and ADHD understand their communication.

Text: "{text}"

Provide a JSON response with:
1. emotional_state: "calm", "engaged", "elevated", "intense", "rapid", "distracted", or "overwhelmed"
2. social_cues: "appropriate", "interrupting", "dominating", "monotone", "too_quiet", "off_topic", or "repetitive"
3. speech_pattern: "normal", "rushed", "rambling", "clear", "hesitant", "loud", or "quiet"
4. confidence: 0.0-1.0 (how certain you are of the assessment)
5. key_indicators: list of specific words/phrases that support your assessment
6. coaching_feedback: practical, supportive suggestion if needed (one sentence, or "Continue as you are" if appropriate)

Assessment guidelines:
- Default to "calm" and "appropriate" for normal conversational speech (e.g., steady pace, clear articulation, turn-taking, and absence of excessive interruptions or emotional outbursts)
- Only flag "intense" or "elevated" if there are clear indicators like excitement, urgency, or emotional language
- Consider context - sharing accomplishments or explaining technical topics is often normal enthusiasm
- "engaged" is positive - someone actively participating in discussion
- Focus on patterns, not single words or phrases

Be conservative in flagging issues - most conversation should be assessed as appropriate."""
