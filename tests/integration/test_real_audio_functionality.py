"""
Tests that require real audio files and test        # Verify transcription structure
        assert isinstance(result, dict)
        assert 'text' in res        if result['word_count'] > 0:
            # Calculate WPM manually since transcribe doesn't return it
            wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])

            # Test pace feedback
            pace_feedback = transcriber.get_speaking_pace_feedback(wpm)
        assert 'word_count' in result
        assert 'duration' in result

        # Calculate WPM manually since transcribe doesn't return it
        if result['duration'] > 0 and result['word_count'] > 0:
            wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])
            assert isinstance(wpm, (int, float))
            assert wpm >= 0
"""
import pytest
import numpy as np
import wave
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from transcriber import Transcriber
from analyzer import CommunicationAnalyzer
import config

class TestWithRealAudio:
    """Tests using the actual test_capture.wav file"""

    @pytest.fixture
    def test_audio_path(self):
        """Path to test audio file."""
        return os.path.join(
            os.path.dirname(__file__),
            '..', 'fixtures', 'test_capture.wav'
        )

    @pytest.fixture
    def audio_data(self, test_audio_path):
        """Load audio data from test file."""
        if not os.path.exists(test_audio_path):
            pytest.skip("test_capture.wav not found - run 'python main.py --test-audio' to create it")

        with wave.open(test_audio_path, 'rb') as wf:
            audio_bytes = wf.readframes(wf.getnframes())
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        return audio_array

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.requires_audio
    def test_real_audio_transcription_accuracy(self, audio_data):
        """Test transcription with real captured audio."""
        transcriber = Transcriber()

        result = transcriber.transcribe(audio_data)

        # Verify transcription structure
        assert isinstance(result, dict)
        assert 'text' in result
        assert 'word_count' in result
        assert 'duration' in result

        # Calculate WPM manually since transcribe doesn't return it
        if result['duration'] > 0 and result['word_count'] > 0:
            wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])
            assert isinstance(wpm, (int, float))
            assert wpm >= 0

        # Verify reasonable values
        assert result['duration'] > 0
        assert result['word_count'] >= 0

        # If there was actual speech, we should get some words
        if result['word_count'] > 0:
            assert len(result['text'].strip()) > 0

            # Calculate WPM for sanity check
            wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])
            assert wpm < 1000  # Sanity check - shouldn't be impossibly fast

        print(f"Real audio transcription: '{result['text']}'")
        print(f"Duration: {result['duration']:.2f}s, Words: {result['word_count']}, WPM: {result['wpm']:.1f}")

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.requires_audio
    def test_real_audio_filler_detection(self, audio_data):
        """Test filler word detection on real audio."""
        transcriber = Transcriber()

        result = transcriber.transcribe(audio_data)

        if result['word_count'] > 0:
            filler_counts = transcriber.count_filler_words(result['text'])

            # Should return a dictionary
            assert isinstance(filler_counts, dict)

            # All counts should be positive integers
            for word, count in filler_counts.items():
                assert isinstance(count, int)
                assert count > 0
                assert word in config.FILLER_WORDS

            print(f"Detected filler words: {filler_counts}")

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.requires_audio
    @pytest.mark.requires_ollama
    def test_real_audio_full_analysis_pipeline(self, audio_data):
        """Test complete analysis pipeline with real audio."""
        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()

        # Transcribe real audio
        transcription_result = transcriber.transcribe(audio_data)

        if transcription_result['word_count'] >= config.MIN_WORDS_FOR_ANALYSIS:
            # Analyze the real transcribed text
            analysis_result = analyzer.analyze(transcription_result['text'])

            # Verify analysis structure
            assert 'emotional_state' in analysis_result
            assert 'confidence' in analysis_result
            assert 'reasoning' in analysis_result

            # Verify reasonable values
            assert 0 <= analysis_result['confidence'] <= 1
            assert analysis_result['tone'] in [
                'supportive', 'dismissive', 'neutral', 'aggressive', 'passive', 'unknown'
            ]

            # Test alert logic
            should_alert = analyzer.should_alert(
                analysis_result['tone'],
                analysis_result['confidence']
            )
            assert isinstance(should_alert, bool)

            # Test emoji generation
            emoji = analyzer.get_emotional_state_emoji(analysis_result['emotional_state'])
            assert emoji is not None
            assert len(emoji) > 0

            print(f"Real audio analysis:")
            print(f"  Text: '{transcription_result['text']}'")
            print(f"  Emotional State: {analysis_result['emotional_state']} ({analysis_result['confidence']:.2f})")
            print(f"  Alert: {should_alert}")
            print(f"  Emoji: {emoji}")
            print(f"  Reasoning: {analysis_result['reasoning']}")
        else:
            print(f"Audio too short for analysis ({transcription_result['word_count']} words)")

    @pytest.mark.integration
    @pytest.mark.requires_audio
    def test_real_audio_pace_analysis(self, audio_data):
        """Test speaking pace analysis with real audio."""
        transcriber = Transcriber()

        result = transcriber.transcribe(audio_data)

        if result['word_count'] > 0:
            # Test pace feedback
            pace_feedback = transcriber.get_speaking_pace_feedback(result['wpm'])

            assert isinstance(pace_feedback, dict)
            assert 'message' in pace_feedback
            assert 'level' in pace_feedback

            # Level should be one of the expected values
            assert pace_feedback['level'] in ['too_fast', 'too_slow', 'ideal', 'normal']

            # Message should be a non-empty string
            assert isinstance(pace_feedback['message'], str)
            assert len(pace_feedback['message']) > 0

            print(f"Speaking pace: {result['wpm']:.1f} WPM - {pace_feedback['message']}")
        else:
            print("No speech detected in audio for pace analysis")

class TestAudioFileFormats:
    """Test handling of different audio file characteristics"""

    @pytest.mark.integration
    @pytest.mark.requires_audio
    def test_audio_file_properties(self):
        """Test that the audio file has expected properties."""
        test_audio_path = os.path.join(
            os.path.dirname(__file__),
            '..', 'fixtures', 'test_capture.wav'
        )

        if not os.path.exists(test_audio_path):
            pytest.skip("test_capture.wav not found")

        with wave.open(test_audio_path, 'rb') as wf:
            # Check basic properties
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            duration = wf.getnframes() / sample_rate

            # Should match expected format
            assert sample_rate == config.SAMPLE_RATE or sample_rate in [16000, 44100, 48000]
            assert channels in [1, 2]  # Mono or stereo
            assert sample_width in [2, 4]  # 16-bit or 32-bit
            assert duration > 0
            assert duration < 60  # Shouldn't be longer than a minute for test file

            print(f"Audio file properties:")
            print(f"  Sample rate: {sample_rate} Hz")
            print(f"  Channels: {channels}")
            print(f"  Sample width: {sample_width} bytes")
            print(f"  Duration: {duration:.2f} seconds")

    @pytest.mark.integration
    def test_transcriber_handles_different_audio_formats(self):
        """Test that transcriber can handle various audio input formats."""
        transcriber = Transcriber()

        # Test with different numpy array formats
        test_cases = [
            np.array([0.1, -0.1, 0.05, -0.05], dtype=np.float32),  # Float32
            np.array([1000, -1000, 500, -500], dtype=np.int16),    # Int16
            np.array([0.1, -0.1, 0.05], dtype=np.float64),        # Float64 (should convert)
        ]

        for i, audio_data in enumerate(test_cases):
            try:
                result = transcriber.transcribe(audio_data)

                # Should not crash and should return proper structure
                assert isinstance(result, dict)
                assert 'text' in result
                assert 'word_count' in result
                assert 'duration' in result

                print(f"Test case {i+1} ({audio_data.dtype}): Success")

            except Exception as e:
                pytest.fail(f"Failed to handle audio format {audio_data.dtype}: {e}")

class TestApplicationStartup:
    """Test application startup and configuration with real conditions"""

    @pytest.mark.integration
    def test_main_components_initialize_with_real_conditions(self):
        """Test that main components can initialize under real conditions."""
        from audio_capture import AudioCapture
        from transcriber import Transcriber
        from analyzer import CommunicationAnalyzer
        from feedback_display import SimpleFeedbackDisplay
        from dashboard import LiveDashboard
        from timeline import EmotionalTimeline

        # These should all initialize without errors
        try:
            # Test each component individually first
            transcriber = Transcriber()
            assert transcriber.model is not None

            analyzer = CommunicationAnalyzer()
            assert hasattr(analyzer, 'get_emotional_state_emoji')

            display = SimpleFeedbackDisplay()
            assert hasattr(display, 'update_tone')

            dashboard = LiveDashboard()
            assert hasattr(dashboard, 'update_current_status')

            timeline = EmotionalTimeline()
            assert hasattr(timeline, 'add_entry')

            print("✅ All components initialized successfully")

        except Exception as e:
            pytest.fail(f"Component initialization failed: {e}")

    @pytest.mark.integration
    @pytest.mark.requires_audio
    def test_audio_capture_with_real_devices(self):
        """Test audio capture with real audio devices."""
        from audio_capture import AudioCapture

        try:
            # Test microphone mode
            capture_mic = AudioCapture(use_microphone=True)
            assert capture_mic.device_index is not None

            device_name = capture_mic.get_device_name(capture_mic.device_index)
            assert len(device_name) > 0

            print(f"✅ Microphone device: {device_name}")

        except RuntimeError as e:
            if "No suitable microphone found" in str(e):
                pytest.skip("No suitable microphone found on this system")
            else:
                raise

        try:
            # Test BlackHole mode (might not be available)
            capture_blackhole = AudioCapture(use_microphone=False)
            assert capture_blackhole.device_index is not None

            device_name = capture_blackhole.get_device_name(capture_blackhole.device_index)
            print(f"✅ BlackHole device: {device_name}")

        except RuntimeError as e:
            if "BlackHole device not found" in str(e):
                print("⚠️  BlackHole not installed (expected for many setups)")
            else:
                raise
