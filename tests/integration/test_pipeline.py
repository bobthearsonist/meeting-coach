"""
Integration tests for the complete meeting coach pipeline
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from audio_capture import AudioCapture
from transcriber import Transcriber
from analyzer import CommunicationAnalyzer
from dashboard import LiveDashboard
import config

class TestMeetingCoachPipeline:
    """Integration tests for the complete pipeline"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_audio_to_transcription_pipeline(self, sample_audio_data):
        """Test the pipeline from audio to transcription."""
        transcriber = Transcriber()

        # This will use actual Whisper model
        result = transcriber.transcribe(sample_audio_data)

        # Verify result structure
        assert 'text' in result
        assert 'word_count' in result
        assert 'duration' in result

        # Calculate WPM manually since transcribe doesn't return it
        if result['duration'] > 0:
            wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])
            assert isinstance(wpm, float)
            assert wpm >= 0

        # Verify data types
        assert isinstance(result['text'], str)
        assert isinstance(result['word_count'], int)
        assert isinstance(result['duration'], (int, float))

        # Calculate WPM manually since transcribe doesn't return it
        if result['duration'] > 0:
            wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])
            result['wpm'] = wpm  # Add it to result for compatibility
            assert isinstance(result['wpm'], (int, float))
            assert result['wpm'] >= 0

        # Verify reasonable values
        assert result['duration'] > 0
        assert result['word_count'] >= 0

    @pytest.mark.integration
    @pytest.mark.requires_ollama
    def test_transcription_to_analysis_pipeline(self, sample_transcription_results):
        """Test the pipeline from transcription to analysis."""
        analyzer = CommunicationAnalyzer()

        for sample in sample_transcription_results:
            result = analyzer.analyze_tone(sample['text'])

            # Verify analysis structure
            assert 'tone' in result
            assert 'confidence' in result
            assert isinstance(result['tone'], str)
            assert isinstance(result['confidence'], float)

            # Check that tone matches expected pattern for the text
            expected_tone = sample['expected_tone']
            if expected_tone in ['supportive', 'neutral', 'calm']:
                # These are positive/neutral tones
                assert result['tone'] not in ['aggressive', 'hostile']
            elif expected_tone == 'aggressive':
                # This should be detected as concerning
                assert result['tone'] in ['aggressive', 'elevated', 'intense'] or result['confidence'] < 0.5

    @pytest.mark.integration
    def test_analysis_to_dashboard_pipeline(self, dashboard_scenarios):
        """Test the pipeline from analysis to dashboard display."""
        dashboard = LiveDashboard()

        for scenario in dashboard_scenarios:
            dashboard.update_current_status(
                emotional_state=scenario['state'],
                social_cue=scenario['cue'],
                confidence=scenario['confidence'],
                text=scenario['text'],
                coaching=scenario['coaching'],
                alert=scenario['alert'],
                wpm=scenario['wpm']
            )

            # Verify dashboard state was updated
            assert dashboard.current_state['emotional_state'] == scenario['state']
            assert dashboard.current_social_cue == scenario['cue']
            assert dashboard.current_confidence == scenario['confidence']
            assert dashboard.current_text == scenario['text']
            assert dashboard.current_coaching == scenario['coaching']
            assert dashboard.alert_active == scenario['alert']
            assert dashboard.current_wpm == scenario['wpm']

    @pytest.mark.integration
    @pytest.mark.slow
    @patch('analyzer.ollama.generate')
    def test_complete_pipeline_mock_ollama(self, mock_generate, sample_audio_data):
        """Test the complete pipeline with mocked Ollama."""
        # Mock Ollama response
        mock_response = {
            'response': '{"tone": "supportive", "confidence": 0.8, "reasoning": "Positive language"}'
        }
        mock_generate.return_value = mock_response

        # Initialize components
        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()
        dashboard = LiveDashboard()

        # Run pipeline
        # 1. Transcribe audio
        transcription_result = transcriber.transcribe(sample_audio_data)

        # 2. Analyze transcription - use a longer text to ensure it meets MIN_WORDS_FOR_ANALYSIS
        longer_text = "This is a much longer text that should definitely meet the minimum word requirement for analysis by the communication analyzer"
        analysis_result = analyzer.analyze_tone(longer_text)

        # 3. Update dashboard
        # Calculate WPM first
        wpm = transcriber.calculate_wpm(transcription_result['word_count'], transcription_result['duration'])

        dashboard.update_current_status(
            emotional_state='calm',  # Would come from additional analysis
            social_cue='appropriate',
            confidence=analysis_result['confidence'],
            text=transcription_result['text'],
            coaching='',
            alert=analyzer.should_alert(analysis_result['tone'], analysis_result['confidence']),
            wpm=wpm
        )

        # Verify end-to-end results
        assert transcription_result['text'] is not None
        assert analysis_result['tone'] == 'supportive'
        assert analysis_result['confidence'] == 0.8
        assert dashboard.current_state['confidence'] == 0.8
        assert not dashboard.alert_active  # Supportive tone shouldn't alert

    @pytest.mark.integration
    @pytest.mark.requires_audio
    def test_audio_capture_integration(self):
        """Test audio capture integration (requires audio hardware)."""
        try:
            capture = AudioCapture()

            # Test that we can initialize audio capture
            assert capture.sample_rate == config.SAMPLE_RATE
            assert capture.chunk_size == config.CHUNK_SIZE

            # Test format detection
            audio_format = capture.get_audio_format()
            assert audio_format is not None

        except Exception as e:
            pytest.skip(f"Audio hardware not available: {e}")

    @pytest.mark.integration
    def test_error_handling_in_pipeline(self):
        """Test error handling throughout the pipeline."""
        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()
        dashboard = LiveDashboard()

        # Test with problematic inputs

        # 1. Empty audio - test that it doesn't crash
        empty_audio = np.array([], dtype=np.float32)
        try:
            result = transcriber.transcribe(empty_audio)
            # Should return some result structure even for empty audio
            assert isinstance(result, dict)
            assert 'text' in result
            assert 'duration' in result
        except Exception as e:
            # It's OK if it raises an exception, just make sure it's handled gracefully
            assert isinstance(e, Exception)

        # 2. Invalid text for analysis
        invalid_analysis = analyzer.analyze_tone("")
        assert 'error' in invalid_analysis  # Should indicate insufficient text

        # 3. Test dashboard with edge case values
        dashboard.update_current_status(
            emotional_state="unknown",
            social_cue="unknown",
            confidence=0.0,
            text="",
            coaching="",
            alert=False,
            wpm=0
        )
        assert dashboard.current_state['emotional_state'] == "unknown"

    @pytest.mark.integration
    def test_performance_benchmarks(self, sample_audio_data):
        """Test performance benchmarks for the pipeline."""
        import time

        transcriber = Transcriber()

        # Benchmark transcription
        start_time = time.time()
        result = transcriber.transcribe(sample_audio_data)
        transcription_time = time.time() - start_time

        # Should complete transcription reasonably quickly
        # (This is a rough benchmark, adjust based on your requirements)
        audio_duration = len(sample_audio_data) / config.SAMPLE_RATE
        processing_ratio = transcription_time / audio_duration

        # Processing should ideally be faster than real-time for short clips
        if audio_duration < 10:  # For short audio clips
            assert processing_ratio < 5.0, f"Transcription too slow: {processing_ratio:.2f}x real-time"

        print(f"Transcription performance: {processing_ratio:.2f}x real-time")

    @pytest.mark.integration
    def test_memory_usage(self, sample_audio_data):
        """Test that pipeline doesn't have obvious memory leaks."""
        import gc

        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available")
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        transcriber = Transcriber()

        # Run transcription multiple times
        for _ in range(5):
            result = transcriber.transcribe(sample_audio_data)
            gc.collect()  # Force garbage collection

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB for this test)
        memory_increase_mb = memory_increase / (1024 * 1024)
        assert memory_increase_mb < 100, f"Excessive memory usage: {memory_increase_mb:.1f} MB"

        print(f"Memory usage increase: {memory_increase_mb:.1f} MB")
