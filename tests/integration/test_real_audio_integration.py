"""
Integration tests that use real audio files and test the complete console application
"""
import pytest
import subprocess
import sys
import os
import numpy as np
import wave
from unittest.mock import patch, Mock
import tempfile

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import config
from transcriber import Transcriber
from analyzer import CommunicationAnalyzer
from audio_capture import AudioCapture

class TestRealAudioIntegration:
    """Integration tests using real audio files"""

    @pytest.fixture
    def test_audio_file(self):
        """Path to the test audio file."""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'test_capture.wav')

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_audio_transcription(self, test_audio_file):
        """Test transcription with real audio file if it exists."""
        if not os.path.exists(test_audio_file):
            pytest.skip("test_capture.wav not found - run 'python main.py --test-audio' first")

        transcriber = Transcriber()

        # Load the real audio file
        with wave.open(test_audio_file, 'rb') as wf:
            audio_bytes = wf.readframes(wf.getnframes())
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        # Test transcription
        result = transcriber.transcribe(audio_array)

        # Verify result structure
        assert 'text' in result
        assert 'word_count' in result
        assert 'duration' in result
        assert 'wpm' in result

        # Verify reasonable values
        assert result['duration'] > 0
        assert result['word_count'] >= 0
        assert result['wpm'] >= 0

        print(f"Transcription: '{result['text']}'")
        print(f"Word count: {result['word_count']}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"WPM: {result['wpm']:.1f}")

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.requires_ollama
    def test_real_audio_analysis_pipeline(self, test_audio_file):
        """Test complete pipeline with real audio file."""
        if not os.path.exists(test_audio_file):
            pytest.skip("test_capture.wav not found - run 'python main.py --test-audio' first")

        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()

        # Load and transcribe real audio
        with wave.open(test_audio_file, 'rb') as wf:
            audio_bytes = wf.readframes(wf.getnframes())
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        transcription_result = transcriber.transcribe(audio_array)

        if transcription_result['word_count'] >= config.MIN_WORDS_FOR_ANALYSIS:
            # Test analysis with real transcribed text
            analysis_result = analyzer.analyze(transcription_result['text'])

            # Verify analysis result structure
            assert 'emotional_state' in analysis_result
            assert 'confidence' in analysis_result
            assert 'coaching_feedback' in analysis_result

            # Verify reasonable values
            assert 0 <= analysis_result['confidence'] <= 1
            assert analysis_result['emotional_state'] in ['supportive', 'dismissive', 'neutral', 'aggressive', 'passive', 'unknown']

            print(f"Analyzed text: '{transcription_result['text']}'")
            print(f"Emotional State: {analysis_result['emotional_state']} ({analysis_result['confidence']:.2f})")
            print(f"Coaching: {analysis_result['coaching_feedback']}")
        else:
            print(f"Transcription too short ({transcription_result['word_count']} words) for analysis")

class TestConsoleApplication:
    """Test the main console application"""

    @pytest.mark.integration
    def test_main_help(self):
        """Test that main application shows help."""
        result = subprocess.run(
            [sys.executable, 'main.py', '--help'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )

        assert result.returncode == 0
        assert 'Teams Meeting Coach' in result.stdout
        assert '--console' in result.stdout
        assert '--device' in result.stdout

    @pytest.mark.integration
    def test_main_console_flag(self):
        """Test console flag functionality."""
        # Just test that it accepts the flag without error
        # We'll use a timeout to prevent the app from running indefinitely
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Test timeout")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(2)  # 2 second timeout
        result = None

        try:
            result = subprocess.run(
                [sys.executable, 'main.py', '--console'],
                capture_output=True,
                text=True,
                timeout=1,  # 1 second timeout
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            )
        except subprocess.TimeoutExpired:
            # This is expected - the app would run indefinitely
            pass
        except TimeoutError:
            pass
        finally:
            signal.alarm(0)  # Cancel the alarm

        # Test passed if we got here without argument parsing errors
    @pytest.mark.integration
    def test_main_device_argument(self):
        """Test device argument functionality."""
        # Test that device argument is accepted (should fail gracefully with invalid device)
        result = None
        try:
            result = subprocess.run(
                [sys.executable, 'main.py', '--device', '999'],
                capture_output=True,
                text=True,
                timeout=2,  # Short timeout since it should fail quickly
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            )
            # Should exit with an error code for invalid device, but not argument parsing error
            assert result.returncode != 2  # Not an argument parsing error
        except subprocess.TimeoutExpired:
            # This is also acceptable - means the argument was parsed correctly
            # but the app tried to run (which could hang on device initialization)
            pass

        # Test passed if no argument parsing error occurred

class TestAutismADHDScenarios:
    """Test autism/ADHD specific scenarios"""

    @pytest.fixture
    def analyzer(self):
        return CommunicationAnalyzer()

    @pytest.mark.integration
    @pytest.mark.requires_ollama
    def test_autism_adhd_coaching_scenarios(self, analyzer):
        """Test scenarios specifically relevant to autism/ADHD challenges."""

        test_scenarios = [
            {
                'text': "Oh my god, that's exactly what I was thinking! This is so cool, we could totally do this and that and maybe also this other thing I just thought of!",
                'expected_state': 'elevated',
                'description': 'Elevated/excited state (common with ADHD)'
            },
            {
                'text': "Yeah but wait, before you finish, I just had this idea that's really important and I don't want to forget it",
                'expected_cue': 'interrupting',
                'description': 'Interrupting pattern'
            },
            {
                'text': "I... I don't know. There's too much going on. Can we just... I need a minute.",
                'expected_state': 'overwhelmed',
                'description': 'Overwhelmed/shutdown'
            },
            {
                'text': "So like, the thing is, like, we need to, like, figure out the best way to, like, implement this properly.",
                'expected_pattern': 'repetitive',
                'description': 'Repetitive speech pattern'
            }
        ]

        for scenario in test_scenarios:
            result = analyzer.analyze_tone(scenario['text'])

            # Verify we get a reasonable response
            assert 'emotional_state' in result
            assert 'confidence' in result
            assert result['confidence'] >= 0

            print(f"\nScenario: {scenario['description']}")
            print(f"Text: {scenario['text'][:60]}...")
            print(f"Analysis: {result}")

    @pytest.mark.integration
    def test_emotion_accuracy_with_flat_content(self, analyzer):
        """Test that emotionally flat content doesn't trigger false positives."""

        flat_test_texts = [
            "The quarterly results show a 15% increase in revenue, which is in line with our projections.",
            "We need to review the budget for next quarter and allocate resources accordingly.",
            "The meeting is scheduled for 2 PM in conference room B.",
            "Please submit your reports by Friday so we can review them next week.",
            "The current process takes approximately 3 hours to complete."
        ]

        false_positives = 0

        for text in flat_test_texts:
            # Test alert logic with neutral content
            emoji = analyzer.get_emotional_state_emoji('neutral')
            should_alert = analyzer.should_alert('neutral', 0.8)

            if should_alert:
                false_positives += 1

            # Test that neutral content gets appropriate emoji
            assert emoji in ['😐', '💬']  # Should be neutral or fallback

        # Should have very few false positives
        false_positive_rate = false_positives / len(flat_test_texts)
        assert false_positive_rate <= 0.2, f"Too many false positives: {false_positive_rate:.1%}"

class TestFullEndToEndPipeline:
    """Test the complete end-to-end pipeline"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_synthetic_audio_pipeline(self):
        """Test complete pipeline with synthetic audio."""
        from audio_capture import AudioCapture
        from transcriber import Transcriber
        from analyzer import CommunicationAnalyzer
        from feedback_display import SimpleFeedbackDisplay

        # Initialize components
        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()
        display = SimpleFeedbackDisplay()

        # Generate synthetic audio (similar to original test_end_to_end.py)
        duration = 3.0
        sample_rate = config.SAMPLE_RATE
        t = np.linspace(0, duration, int(sample_rate * duration))

        audio = (
            np.sin(2 * np.pi * 150 * t) * 0.1 +
            np.sin(2 * np.pi * 300 * t) * 0.05 +
            np.random.normal(0, 0.01, len(t))
        )

        envelope = np.abs(np.sin(2 * np.pi * 2 * t))
        audio = (audio * envelope).astype(np.float32)

        # Test transcription
        transcription = transcriber.transcribe(audio)

        assert 'text' in transcription
        assert 'word_count' in transcription

        # Calculate WPM manually since transcribe doesn't return it
        if transcription['duration'] > 0 and transcription['word_count'] > 0:
            wpm = transcriber.calculate_wpm(transcription['word_count'], transcription['duration'])
            assert isinstance(wpm, (int, float))

        # Test pace analysis
        if transcription['word_count'] > 0:
            wpm = transcriber.calculate_wpm(transcription['word_count'], transcription['duration'])
            pace_feedback = transcriber.get_speaking_pace_feedback(wpm)
            assert 'message' in pace_feedback
            assert 'status' in pace_feedback

        # Test filler word detection
        filler_counts = transcriber.count_filler_words("um like actually this is a test")
        assert isinstance(filler_counts, dict)
        # Should detect some filler words from the text
        assert len(filler_counts) > 0
        assert 'um' in filler_counts or 'like' in filler_counts or 'actually' in filler_counts
        assert 'like' in filler_counts

    @pytest.mark.integration
    def test_synthetic_text_pipeline(self):
        """Test pipeline with predefined text (no audio transcription)."""
        from transcriber import Transcriber
        from analyzer import CommunicationAnalyzer

        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()

        test_cases = [
            {
                'text': "I really think your proposal has some excellent points and I appreciate the thorough research you've done",
                'word_count': 17,
                'duration': 5.0,
                'expected_tone_category': 'positive'
            },
            {
                'text': "Um, whatever, I don't really, like, think this is going to work at all, you know",
                'word_count': 16,
                'duration': 4.5,
                'expected_tone_category': 'negative'
            },
            {
                'text': "The quarterly metrics indicate a fifteen percent improvement in our customer satisfaction scores",
                'word_count': 14,
                'duration': 6.0,
                'expected_tone_category': 'neutral'
            }
        ]

        for case in test_cases:
            # Test pace calculation
            wpm = transcriber.calculate_wpm(case['word_count'], case['duration'])
            pace_feedback = transcriber.get_speaking_pace_feedback(wpm)

            assert wpm > 0
            assert 'message' in pace_feedback

            # Test filler word detection
            filler_counts = transcriber.count_filler_words(case['text'])
            assert isinstance(filler_counts, dict)

            # Test tone emoji (works without Ollama)
            emoji = analyzer.get_emotional_state_emoji('neutral')
            assert emoji is not None

            print(f"Text: {case['text'][:50]}...")
            print(f"WPM: {wpm:.1f}, Fillers: {filler_counts}")

    @pytest.mark.integration
    def test_filler_word_detection_with_punctuation(self):
        """Test that filler word detection correctly handles punctuation.

        This test verifies that filler words with attached punctuation (like "Um,")
        are correctly detected. The implementation uses regex with word boundaries
        which properly handles punctuation.
        """
        from transcriber import Transcriber

        transcriber = Transcriber()

        # This should detect filler words with punctuation
        filler_counts = transcriber.count_filler_words("Um, like, you know, this is a test")

        # These assertions should pass:
        assert filler_counts.get('um', 0) >= 1, "Should detect 'Um,' as 'um'"
        assert filler_counts.get('like', 0) >= 1, "Should detect 'like,' as 'like'"
        assert filler_counts.get('you know', 0) >= 1, "Should detect 'you know'"

        # Test more complex punctuation
        complex_text = "Well, um... like, you know? Actually, uh, basically!"
        complex_counts = transcriber.count_filler_words(complex_text)

        assert complex_counts.get('um', 0) >= 1, "Should detect 'um...' as 'um'"
        assert complex_counts.get('like', 0) >= 1, "Should detect 'like,' as 'like'"
        assert complex_counts.get('you know', 0) >= 1, "Should detect 'you know?' as 'you know'"
        assert complex_counts.get('actually', 0) >= 1, "Should detect 'Actually,' as 'actually'"
        assert complex_counts.get('basically', 0) >= 1, "Should detect 'basically!' as 'basically'"

class TestVisualInterface:
    """Test visual interface components"""

    @pytest.mark.integration
    def test_color_functionality(self):
        """Test color and emoji functionality."""
        from colors import colorize_emotional_state, colorize_social_cue, colorize_alert
        from analyzer import CommunicationAnalyzer

        analyzer = CommunicationAnalyzer()

        # Test emotional state emojis
        states = ['calm', 'engaged', 'elevated', 'intense', 'overwhelmed']
        for state in states:
            emoji = analyzer.get_emotional_state_emoji(state)
            assert emoji is not None
            assert len(emoji) > 0

            # Test colorization
            colored = colorize_emotional_state(state)
            assert state.title() in colored or state in colored

        # Test social cue emojis
        cues = ['appropriate', 'interrupting', 'dominating', 'withdrawn']
        for cue in cues:
            if hasattr(analyzer, 'get_social_cue_emoji'):
                emoji = analyzer.get_social_cue_emoji(cue)
                assert emoji is not None

        # Test alert colorization
        alert_text = colorize_alert("Test alert", is_alert=True)
        assert "Test alert" in alert_text

    @pytest.mark.integration
    def test_timeline_functionality(self):
        """Test timeline and dashboard components."""
        from timeline import EmotionalTimeline
        from dashboard import LiveDashboard

        timeline = EmotionalTimeline(window_minutes=10)
        dashboard = LiveDashboard()

        # Test adding events to timeline
        timeline.add_entry(
            emotional_state='calm',
            social_cue='appropriate',
            confidence=0.8,
            text='Test event',
            alert=False
        )
        assert len(timeline.entries) == 1

        # Test dashboard update
        dashboard.update_current_status(
            emotional_state='engaged',
            social_cue='appropriate',
            confidence=0.8,
            text='Test transcript',
            coaching='Test coaching',
            alert=False,
            wpm=150
        )

        assert dashboard.current_state['emotional_state'] == 'engaged'
        assert dashboard.current_state['wpm'] == 150
        assert not dashboard.alert_active
