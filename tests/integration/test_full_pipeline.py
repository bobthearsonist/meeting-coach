"""
Integration tests for the full meeting coach pipeline.
Tests the interaction between audio capture, transcription, and analysis components.
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import time
import json

import config
from audio_capture import AudioCapture
from transcriber import Transcriber
from analyzer import CommunicationAnalyzer


@pytest.mark.integration
class TestFullPipeline:
    """Integration tests for the complete meeting coach pipeline."""

    @pytest.fixture
    def mock_audio_data(self):
        """Generate realistic mock audio data."""
        # Generate 3 seconds of synthetic speech-like audio
        duration = 3.0
        sample_rate = config.SAMPLE_RATE
        t = np.linspace(0, duration, int(sample_rate * duration))

        # Create speech-like audio with multiple frequency components
        audio = (
            np.sin(2 * np.pi * 200 * t) * 0.1 +  # Low frequency
            np.sin(2 * np.pi * 800 * t) * 0.05 +  # Mid frequency
            np.random.normal(0, 0.01, len(t))     # Noise
        )

        # Apply envelope to simulate speech patterns
        envelope = np.concatenate([
            np.linspace(0, 1, len(t)//4),     # fade in
            np.ones(len(t)//2),               # sustained
            np.linspace(1, 0, len(t)//4)      # fade out
        ])
        audio = audio * envelope

        return audio.astype(np.float32)

    @pytest.fixture
    def mock_transcription_response(self):
        """Mock Whisper transcription response."""
        return {
            'text': 'I really appreciate your input on this project. That is a great point you have made.',
            'segments': []
        }

    @pytest.fixture
    def mock_analysis_response(self):
        """Mock Ollama analysis response."""
        return {
            'response': json.dumps({
                'emotional_state': 'engaged',
                'social_cues': 'appropriate',
                'speech_pattern': 'normal',
                'confidence': 0.8,
                'key_indicators': ['appreciate', 'great point'],
                'coaching_feedback': 'Continue as you are'
            })
        }

    @patch('audio_capture.pyaudio.PyAudio')
    @patch('transcriber.WhisperModel')
    @patch('analyzer.ollama.list')
    @patch('analyzer.ollama.generate')
    def test_complete_audio_to_analysis_pipeline(self, mock_ollama_generate, mock_ollama_list,
                                                  mock_whisper_model_class, mock_pyaudio_class,
                                                  mock_audio_data, mock_transcription_response,
                                                  mock_analysis_response):
        """Test the complete pipeline from audio capture through analysis."""

        # Setup mock audio capture
        def audio_side_effect_func(i):
            devices = [
                {
                    'name': 'Built-in Microphone',
                    'maxInputChannels': 1,
                    'maxOutputChannels': 0,
                    'defaultSampleRate': 44100.0
                },
                {
                    'name': 'BlackHole 2ch',
                    'maxInputChannels': 2,
                    'maxOutputChannels': 2,
                    'defaultSampleRate': 48000.0
                },
                {
                    'name': 'Built-in Output',
                    'maxInputChannels': 0,
                    'maxOutputChannels': 2,
                    'defaultSampleRate': 44100.0
                }
            ]
            return devices[i]

        mock_pyaudio = Mock()
        mock_pyaudio.get_device_count.return_value = 3
        mock_pyaudio.get_device_info_by_index.side_effect = audio_side_effect_func

        # Mock audio stream that returns our test audio data
        audio_bytes = (mock_audio_data * 32768).astype(np.int16).tobytes()
        mock_stream = Mock()
        mock_stream.read.return_value = audio_bytes
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        # Setup mock transcription
        # Create mock segments that can be iterated
        mock_segment = Mock()
        mock_segment.start = 0.0
        mock_segment.end = 3.0
        mock_segment.text = 'I really appreciate your input on this project. That is a great point you have made.'

        mock_info = Mock()
        mock_info.language = 'en'

        mock_whisper_model = Mock()
        mock_whisper_model.transcribe.return_value = ([mock_segment], mock_info)
        mock_whisper_model_class.return_value = mock_whisper_model

        # Setup mock analysis
        mock_ollama_generate.return_value = mock_analysis_response

        # Initialize components
        audio_capture = AudioCapture()
        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()

        # Test the pipeline
        audio_capture.start_capture()

        # Step 1: Capture audio
        audio_chunk = audio_capture.read_chunk(3.0)
        assert isinstance(audio_chunk, np.ndarray)
        assert audio_chunk.dtype == np.float32
        assert len(audio_chunk) > 0

        # Step 2: Transcribe audio
        transcription_result = transcriber.transcribe(audio_chunk)
        assert 'text' in transcription_result
        assert 'word_count' in transcription_result
        assert 'duration' in transcription_result
        assert transcription_result['text'] == mock_segment.text
        assert transcription_result['word_count'] == 16  # Word count of the mock text

        # Calculate WPM separately if needed
        wpm = transcriber.calculate_wpm(transcription_result['word_count'], transcription_result['duration'])

        # Step 3: Analyze transcription
        analysis_result = analyzer.analyze_tone(transcription_result['text'])
        assert 'emotional_state' in analysis_result
        assert 'social_cues' in analysis_result
        assert 'confidence' in analysis_result
        assert analysis_result['emotional_state'] == 'engaged'
        assert analysis_result['social_cues'] == 'appropriate'
        assert analysis_result['confidence'] == 0.8

        # Step 4: Check alert logic
        should_alert = analyzer.should_alert(
            analysis_result['emotional_state'],
            analysis_result['confidence']
        )
        assert not should_alert  # 'engaged' with high confidence should not alert

        audio_capture.stop_capture()

    @patch('audio_capture.pyaudio.PyAudio')
    @patch('transcriber.WhisperModel')
    @patch('analyzer.ollama.list')
    @patch('analyzer.ollama.generate')
    def test_pipeline_with_concerning_analysis(self, mock_ollama_generate, mock_ollama_list,
                                               mock_whisper_model_class, mock_pyaudio_class,
                                               mock_audio_data):
        """Test pipeline with analysis that should trigger alerts."""

        # Setup mocks (similar to above but with different responses)
        def audio_side_effect_func(i):
            devices = [
                {
                    'name': 'Built-in Microphone',
                    'maxInputChannels': 1,
                    'maxOutputChannels': 0,
                    'defaultSampleRate': 44100.0
                },
                {
                    'name': 'BlackHole 2ch',
                    'maxInputChannels': 2,
                    'maxOutputChannels': 2,
                    'defaultSampleRate': 48000.0
                },
                {
                    'name': 'Built-in Output',
                    'maxInputChannels': 0,
                    'maxOutputChannels': 2,
                    'defaultSampleRate': 44100.0
                }
            ]
            return devices[i]

        mock_pyaudio = Mock()
        mock_pyaudio.get_device_count.return_value = 3
        mock_pyaudio.get_device_info_by_index.side_effect = audio_side_effect_func

        audio_bytes = (mock_audio_data * 32768).astype(np.int16).tobytes()
        mock_stream = Mock()
        mock_stream.read.return_value = audio_bytes
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        # Mock concerning transcription
        mock_segment = Mock()
        mock_segment.start = 0.0
        mock_segment.end = 3.0
        mock_segment.text = 'Whatever, I do not really care about that at all. Let us just move on immediately.'

        mock_info = Mock()
        mock_info.language = 'en'

        mock_whisper_model = Mock()
        mock_whisper_model.transcribe.return_value = ([mock_segment], mock_info)
        mock_whisper_model_class.return_value = mock_whisper_model

        # Mock concerning analysis
        concerning_analysis = {
            'response': json.dumps({
                'emotional_state': 'dismissive',
                'social_cues': 'inappropriate',
                'speech_pattern': 'rushed',
                'confidence': 0.9,
                'key_indicators': ['whatever', 'do not care'],
                'coaching_feedback': 'Try to show more engagement and interest in the discussion'
            })
        }

        mock_ollama_generate.return_value = concerning_analysis

        # Initialize components
        audio_capture = AudioCapture()
        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()

        # Test the pipeline
        audio_capture.start_capture()
        audio_chunk = audio_capture.read_chunk(3.0)
        transcription_result = transcriber.transcribe(audio_chunk)
        analysis_result = analyzer.analyze_tone(transcription_result['text'])

        # Verify concerning results
        assert analysis_result['emotional_state'] == 'dismissive'
        assert analysis_result['social_cues'] == 'inappropriate'
        assert analysis_result['confidence'] == 0.9

        # Check that alerts would be triggered
        should_alert_emotion = analyzer.should_alert(
            analysis_result['emotional_state'],
            analysis_result['confidence']
        )
        should_alert_social = analyzer.should_social_cue_alert(
            analysis_result['social_cues'],
            analysis_result['confidence']
        )

        assert should_alert_emotion  # 'dismissive' should trigger alert
        assert not should_alert_social  # 'inappropriate' not in the social alert list

        audio_capture.stop_capture()

    @patch('audio_capture.pyaudio.PyAudio')
    @patch('transcriber.WhisperModel')
    @patch('analyzer.ollama.list')
    @patch('analyzer.ollama.generate')
    def test_pipeline_error_handling(self, mock_ollama_generate, mock_ollama_list,
                                     mock_whisper_model_class, mock_pyaudio_class,
                                     mock_audio_data):
        """Test pipeline error handling when components fail."""

        # Setup audio capture mock
        def audio_side_effect_func(i):
            devices = [
                {
                    'name': 'Built-in Microphone',
                    'maxInputChannels': 1,
                    'maxOutputChannels': 0,
                    'defaultSampleRate': 44100.0
                },
                {
                    'name': 'BlackHole 2ch',
                    'maxInputChannels': 2,
                    'maxOutputChannels': 2,
                    'defaultSampleRate': 48000.0
                },
                {
                    'name': 'Built-in Output',
                    'maxInputChannels': 0,
                    'maxOutputChannels': 2,
                    'defaultSampleRate': 44100.0
                }
            ]
            return devices[i]

        mock_pyaudio = Mock()
        mock_pyaudio.get_device_count.return_value = 3
        mock_pyaudio.get_device_info_by_index.side_effect = audio_side_effect_func

        audio_bytes = (mock_audio_data * 32768).astype(np.int16).tobytes()
        mock_stream = Mock()
        mock_stream.read.return_value = audio_bytes
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        # Mock transcription that works
        mock_segment = Mock()
        mock_segment.start = 0.0
        mock_segment.end = 3.0
        mock_segment.text = 'This is a test transcription with sufficient words for analysis to proceed correctly and demonstrate error handling.'

        mock_info = Mock()
        mock_info.language = 'en'

        mock_whisper_model = Mock()
        mock_whisper_model.transcribe.return_value = ([mock_segment], mock_info)
        mock_whisper_model_class.return_value = mock_whisper_model

        # Mock analysis that fails (invalid JSON)
        mock_ollama_generate.return_value = {
            'response': 'Invalid JSON response that cannot be parsed'
        }

        # Initialize components
        audio_capture = AudioCapture()
        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()

        # Test the pipeline with error handling
        audio_capture.start_capture()
        audio_chunk = audio_capture.read_chunk(3.0)

        # Transcription should succeed
        transcription_result = transcriber.transcribe(audio_chunk)
        assert 'text' in transcription_result
        assert len(transcription_result['text']) > 0

        # Analysis should fail gracefully and return error state
        analysis_result = analyzer.analyze_tone(transcription_result['text'])
        assert analysis_result['tone'] == 'neutral'  # Long enough text should reach error handler
        assert analysis_result['confidence'] == 0.0
        assert analysis_result['error'] == 'parse_error'
        assert analysis_result['suggestions'] == 'Analysis error'

        audio_capture.stop_capture()

    @patch('audio_capture.pyaudio.PyAudio')
    @patch('transcriber.WhisperModel')
    @patch('analyzer.ollama.list')
    @patch('analyzer.ollama.generate')
    def test_pipeline_performance_timing(self, mock_ollama_generate, mock_ollama_list,
                                          mock_whisper_model_class, mock_pyaudio_class,
                                          mock_audio_data, mock_transcription_response,
                                          mock_analysis_response):
        """Test that the pipeline completes within reasonable time limits."""

        # Setup mocks similar to the first test
        def audio_side_effect_func(i):
            devices = [
                {
                    'name': 'Built-in Microphone',
                    'maxInputChannels': 1,
                    'maxOutputChannels': 0,
                    'defaultSampleRate': 44100.0
                },
                {
                    'name': 'BlackHole 2ch',
                    'maxInputChannels': 2,
                    'maxOutputChannels': 2,
                    'defaultSampleRate': 48000.0
                },
                {
                    'name': 'Built-in Output',
                    'maxInputChannels': 0,
                    'maxOutputChannels': 2,
                    'defaultSampleRate': 44100.0
                }
            ]
            return devices[i]

        mock_pyaudio = Mock()
        mock_pyaudio.get_device_count.return_value = 3
        mock_pyaudio.get_device_info_by_index.side_effect = audio_side_effect_func

        audio_bytes = (mock_audio_data * 32768).astype(np.int16).tobytes()
        mock_stream = Mock()
        mock_stream.read.return_value = audio_bytes
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio

        mock_segment = Mock()
        mock_segment.start = 0.0
        mock_segment.end = 3.0
        mock_segment.text = mock_transcription_response['text']

        mock_info = Mock()
        mock_info.language = 'en'

        mock_whisper_model = Mock()
        mock_whisper_model.transcribe.return_value = ([mock_segment], mock_info)
        mock_whisper_model_class.return_value = mock_whisper_model

        mock_ollama_generate.return_value = mock_analysis_response

        # Initialize components
        audio_capture = AudioCapture()
        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()

        # Time the entire pipeline
        start_time = time.time()

        audio_capture.start_capture()
        audio_chunk = audio_capture.read_chunk(3.0)
        transcription_result = transcriber.transcribe(audio_chunk)
        analysis_result = analyzer.analyze_tone(transcription_result['text'])
        audio_capture.stop_capture()

        end_time = time.time()
        pipeline_duration = end_time - start_time

        # Pipeline should complete quickly with mocked components
        assert pipeline_duration < 1.0  # Should complete in under 1 second

        # Verify all components produced valid results
        assert len(audio_chunk) > 0
        assert 'text' in transcription_result
        assert 'emotional_state' in analysis_result

    def test_summary_generation_integration(self):
        """Test the analysis summary generation with multiple results."""
        analyzer = CommunicationAnalyzer()

        # Simulate multiple analysis results from a meeting
        analysis_results = [
            {
                'tone': 'engaged',
                'confidence': 0.8,
                'suggestions': 'Continue as you are',
                'key_indicators': ['appreciate', 'input']
            },
            {
                'tone': 'neutral',
                'confidence': 0.6,
                'suggestions': 'Try to be more expressive',
                'key_indicators': ['results', 'data']
            },
            {
                'tone': 'elevated',
                'confidence': 0.9,
                'suggestions': 'Consider slowing down',
                'key_indicators': ['excited', 'quickly']
            },
            {
                'tone': 'engaged',
                'confidence': 0.7,
                'suggestions': 'Good enthusiasm',
                'key_indicators': ['great', 'idea']
            },
            {
                'tone': 'dismissive',
                'confidence': 0.8,
                'suggestions': 'Show more interest',
                'key_indicators': ['whatever', 'fine']
            }
        ]

        summary = analyzer.generate_summary(analysis_results)

        # Verify summary structure
        assert 'dominant_tone' in summary
        assert 'tone_distribution' in summary
        assert 'average_confidence' in summary
        assert 'key_suggestions' in summary
        assert 'total_analyses' in summary

        # Verify content
        assert summary['dominant_tone'] == 'engaged'  # Most frequent
        assert summary['tone_distribution']['engaged'] == 2
        assert summary['tone_distribution']['elevated'] == 1
        assert summary['tone_distribution']['dismissive'] == 1
        assert summary['total_analyses'] == 5
        assert len(summary['key_suggestions']) <= 3  # Should limit to top 3

        # Verify average confidence calculation
        expected_avg = (0.8 + 0.6 + 0.9 + 0.7 + 0.8) / 5
        assert abs(summary['average_confidence'] - expected_avg) < 0.001

    @pytest.mark.slow
    def test_emoji_and_formatting_integration(self):
        """Test that emoji mappings work correctly for all tone types."""
        analyzer = CommunicationAnalyzer()

        # Test all tone types have corresponding emojis
        tone_types = [
            'supportive', 'dismissive', 'neutral', 'aggressive', 'passive',
            'positive', 'negative', 'elevated', 'intense', 'rapid', 'calm',
            'engaged', 'distracted', 'overwhelmed', 'unknown'
        ]

        for tone in tone_types:
            emoji = analyzer.get_tone_emoji(tone)
            assert emoji is not None
            assert len(emoji) > 0
            assert emoji != ''

        # Test social cue emojis
        social_cues = [
            'interrupting', 'dominating', 'monotone', 'too_quiet',
            'appropriate', 'off_topic', 'repetitive'
        ]

        for cue in social_cues:
            emoji = analyzer.get_social_cue_emoji(cue)
            assert emoji is not None
            assert len(emoji) > 0
            assert emoji != ''

        # Test unknown values return default emoji
        assert analyzer.get_tone_emoji('unknown_tone') == '💬'
        assert analyzer.get_social_cue_emoji('unknown_cue') == '💬'
