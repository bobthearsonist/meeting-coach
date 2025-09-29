"""
Integration tests for the complete meeting coach pipeline
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch
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
        assert 'wpm' in result
        
        # Verify data types
        assert isinstance(result['text'], str)
        assert isinstance(result['word_count'], int)
        assert isinstance(result['duration'], (int, float))
        assert isinstance(result['wpm'], (int, float))
        
        # Verify reasonable values
        assert result['duration'] > 0
        assert result['word_count'] >= 0
        assert result['wpm'] >= 0
    
    @pytest.mark.integration
    @pytest.mark.requires_ollama
    def test_transcription_to_analysis_pipeline(self, sample_transcription_results):
        """Test the pipeline from transcription to analysis."""
        analyzer = CommunicationAnalyzer()
        
        for sample in sample_transcription_results:
            result = analyzer.analyze(sample['text'])
            
            # Verify result structure
            assert 'tone' in result
            assert 'confidence' in result
            assert 'reasoning' in result
            
            # Verify data types
            assert isinstance(result['tone'], str)
            assert isinstance(result['confidence'], (int, float))
            assert isinstance(result['reasoning'], str)
            
            # Verify reasonable values
            assert 0 <= result['confidence'] <= 1
            assert result['tone'] in ['supportive', 'dismissive', 'neutral', 'aggressive', 'passive', 'unknown']
    
    @pytest.mark.integration
    def test_analysis_to_dashboard_pipeline(self, dashboard_scenarios):
        """Test the pipeline from analysis to dashboard display."""
        dashboard = LiveDashboard()
        
        for scenario in dashboard_scenarios:
            dashboard.update(
                emotional_state=scenario['state'],
                social_cue=scenario['cue'],
                confidence=scenario['confidence'],
                transcript=scenario['text'],
                coaching_tip=scenario['coaching'],
                alert=scenario['alert'],
                wpm=scenario['wpm']
            )
            
            # Verify dashboard state updated
            assert dashboard.current_state['emotional_state'] == scenario['state']
            assert dashboard.current_state['social_cue'] == scenario['cue']
            assert dashboard.alert_active == scenario['alert']
    
    @pytest.mark.integration
    @pytest.mark.slow
    @patch('analyzer.ollama.chat')
    def test_complete_pipeline_mock_ollama(self, mock_chat, sample_audio_data):
        """Test the complete pipeline with mocked Ollama."""
        # Mock Ollama response
        mock_response = {
            'message': {
                'content': '{"tone": "supportive", "confidence": 0.8, "reasoning": "Positive language"}'
            }
        }
        mock_chat.return_value = mock_response
        
        # Initialize components
        transcriber = Transcriber()
        analyzer = CommunicationAnalyzer()
        dashboard = LiveDashboard()
        
        # Run pipeline
        # 1. Transcribe audio
        transcription_result = transcriber.transcribe(sample_audio_data)
        
        # 2. Analyze transcription
        analysis_result = analyzer.analyze(transcription_result['text'])
        
        # 3. Update dashboard
        dashboard.update(
            emotional_state='calm',  # Would come from additional analysis
            social_cue='appropriate',
            confidence=analysis_result['confidence'],
            transcript=transcription_result['text'],
            coaching_tip='',
            alert=analyzer.should_alert(analysis_result['tone'], analysis_result['confidence']),
            wpm=transcription_result['wpm']
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
        
        # 1. Empty audio
        empty_audio = np.array([], dtype=np.float32)
        with patch.object(transcriber, '_get_model') as mock_get_model:
            mock_model = Mock()
            mock_model.transcribe.return_value = {'text': '', 'segments': []}
            mock_get_model.return_value = mock_model
            
            result = transcriber.transcribe(empty_audio)
            assert result['word_count'] == 0
        
        # 2. Empty text analysis
        with patch('analyzer.ollama.chat') as mock_chat:
            mock_chat.side_effect = Exception("Connection failed")
            result = analyzer.analyze("")
            assert result['tone'] == 'unknown'
            assert result['confidence'] == 0.0
        
        # 3. Dashboard with None values
        dashboard.update(
            emotional_state=None,
            social_cue=None,
            confidence=None,
            transcript=None,
            coaching_tip=None,
            alert=False,
            wpm=None
        )
        # Should not crash
        assert dashboard.current_state is not None
    
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
        import psutil
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