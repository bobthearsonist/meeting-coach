"""
Speech-to-text transcription using Faster-Whisper
"""
from faster_whisper import WhisperModel
import numpy as np
from typing import Dict, List
import config
import re


class Transcriber:
    def __init__(self):
        """Initialize Whisper model for transcription."""
        print(f"Loading Whisper model: {config.WHISPER_MODEL}")
        self.model = WhisperModel(
            config.WHISPER_MODEL,
            device=config.DEVICE,
            compute_type=config.COMPUTE_TYPE
        )
        print("Whisper model loaded successfully")

    def transcribe(self, audio: np.ndarray) -> Dict[str, any]:
        """
        Transcribe audio chunk to text.

        Args:
            audio: numpy array of audio samples (float32, normalized)

        Returns:
            Dictionary containing:
                - text: transcribed text
                - segments: list of segments with timestamps
                - duration: audio duration in seconds
                - word_count: number of words
                - wpm: words per minute
        """
        # Preprocess audio
        audio = self.preprocess_audio(audio)

        # Calculate duration first
        duration = len(audio) / config.SAMPLE_RATE

        # Transcribe
        segments, info = self.model.transcribe(
            audio,
            beam_size=5,
            vad_filter=True,  # Voice activity detection
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        # Collect all segments
        segment_list = []
        full_text = []

        for segment in segments:
            segment_list.append({
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip()
            })
            full_text.append(segment.text.strip())

        # Combine text
        combined_text = " ".join(full_text)

        # Calculate metrics
        word_count = len(combined_text.split()) if combined_text.strip() else 0
        wpm = self.calculate_wpm(word_count, duration)

        return {
            'text': combined_text,
            'segments': segment_list,
            'duration': duration,
            'word_count': word_count,
            'wpm': wpm,
            'language': info.language if hasattr(info, 'language') else 'en'
        }

    def calculate_wpm(self, word_count: int, duration: float) -> float:
        """
        Calculate words per minute.

        Args:
            word_count: number of words
            duration: duration in seconds

        Returns:
            words per minute
        """
        if duration <= 0:
            return 0.0
        return (word_count / duration) * 60

    def get_speaking_pace_feedback(self, wpm: float) -> Dict[str, str]:
        """
        Get feedback on speaking pace.

        Args:
            wpm: words per minute

        Returns:
            Dictionary with pace assessment and feedback
        """
        if wpm > config.PACE_TOO_FAST:
            return {
                'level': 'too_fast',
                'category': 'fast',
                'message': f'Speaking too fast ({wpm:.0f} WPM). Try to slow down.',
                'icon': '🐇'
            }
        elif wpm < config.PACE_TOO_SLOW:
            return {
                'level': 'too_slow',
                'category': 'slow',
                'message': f'Speaking slowly ({wpm:.0f} WPM). Consider picking up the pace.',
                'icon': '🐢'
            }
        elif config.PACE_IDEAL_MIN <= wpm <= config.PACE_IDEAL_MAX:
            return {
                'level': 'ideal',
                'category': 'good',
                'message': f'Great pace! ({wpm:.0f} WPM)',
                'icon': '✅'
            }
        else:
            return {
                'level': 'normal',
                'category': 'good',
                'message': f'Pace: {wpm:.0f} WPM',
                'icon': '🎯'
            }

    def count_filler_words(self, text: str) -> Dict[str, int]:
        """
        Count filler words in text.

        Args:
            text: transcribed text

        Returns:
            Dictionary of filler word counts
        """
        text_lower = text.lower()
        counts = {}

        for filler in config.FILLER_WORDS:
            if ' ' in filler:
                # Multi-word filler (e.g., "you know")
                count = text_lower.count(filler)
            else:
                # Single word filler - count as whole words only
                pattern = r'\b' + re.escape(filler) + r'\b'
                count = len(re.findall(pattern, text_lower))

            if count > 0:
                counts[filler] = count

        return counts

    def preprocess_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Preprocess audio for transcription - normalize and convert data types.

        Args:
            audio: numpy array of audio samples

        Returns:
            Processed audio as float32 normalized array
        """
        if len(audio) == 0:
            return np.array([], dtype=np.float32)

        # Convert to float32 if needed
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0
        elif audio.dtype == np.float64:
            audio = audio.astype(np.float32)
        elif audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Normalize if amplitude is too high
        max_val = np.abs(audio).max()
        if max_val > 1.0:
            audio = audio / max_val

        return audio


if __name__ == "__main__":
    # Test transcription
    import wave

    print("Testing transcriber...")
    transcriber = Transcriber()

    # Try to load test audio if it exists
    try:
        with wave.open("test_capture.wav", 'rb') as wf:
            audio_bytes = wf.readframes(wf.getnframes())
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            print("\nTranscribing...")
            result = transcriber.transcribe(audio_array)

            print(f"\nTranscription: {result['text']}")
            print(f"Word count: {result['word_count']}")
            print(f"Duration: {result['duration']:.2f}s")

            wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])
            pace_feedback = transcriber.get_speaking_pace_feedback(wpm)
            print(f"\nPace: {pace_feedback['message']}")

            fillers = transcriber.count_filler_words(result['text'])
            if fillers:
                print(f"Filler words: {fillers}")

    except FileNotFoundError:
        print("No test audio file found. Run audio_capture.py first to create test_capture.wav")
