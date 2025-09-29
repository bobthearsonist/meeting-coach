"""
Unit tests for the Transcriber class
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from transcriber import Transcriber
import config

class TestTranscriber:
    """Test cases for Transcriber"""
    
    @pytest.fixture
    def transcriber(self):
        """Create transcriber instance for testing."""
        return Transcriber()
    
    @pytest.mark.unit
    def test_calculate_wpm_basic(self, transcriber):
        """Test basic WPM calculation."""
        # 60 words in 1 minute = 60 WPM
        wpm = transcriber.calculate_wpm(60, 60.0)
        assert wpm == 60.0
        
        # 30 words in 30 seconds = 60 WPM  
        wpm = transcriber.calculate_wpm(30, 30.0)
        assert wpm == 60.0
        
        # 120 words in 1 minute = 120 WPM
        wpm = transcriber.calculate_wpm(120, 60.0)
        assert wpm == 120.0
    
    @pytest.mark.unit
    def test_calculate_wpm_edge_cases(self, transcriber):
        """Test WPM calculation edge cases."""
        # Zero words
        wpm = transcriber.calculate_wpm(0, 60.0)
        assert wpm == 0.0
        
        # Zero duration (should not divide by zero)
        wpm = transcriber.calculate_wpm(60, 0.0)
        assert wpm == 0.0
        
        # Very short duration
        wpm = transcriber.calculate_wpm(1, 0.1)
        assert wpm == 600.0  # 1 word in 0.1 minutes = 600 WPM
    
    @pytest.mark.unit
    def test_calculate_wpm_precision(self, transcriber):
        """Test WPM calculation precision."""
        # Test with fractional values
        wpm = transcriber.calculate_wpm(7, 3.5)  # 7 words in 3.5 seconds
        expected = (7 / 3.5) * 60  # Convert to per minute
        assert abs(wpm - expected) < 0.001
    
    @pytest.mark.unit
    def test_preprocess_audio_basic(self, transcriber, sample_audio_data):
        """Test basic audio preprocessing."""
        processed = transcriber.preprocess_audio(sample_audio_data)
        
        # Should return numpy array
        assert isinstance(processed, np.ndarray)
        
        # Should be float32
        assert processed.dtype == np.float32
        
        # Should have same length as input
        assert len(processed) == len(sample_audio_data)
    
    @pytest.mark.unit
    def test_preprocess_audio_normalization(self, transcriber):
        """Test audio normalization in preprocessing."""
        # Create audio with high amplitude
        loud_audio = np.array([2.0, -2.0, 1.5, -1.5], dtype=np.float32)
        processed = transcriber.preprocess_audio(loud_audio)
        
        # Should be normalized to [-1, 1] range
        assert np.max(processed) <= 1.0
        assert np.min(processed) >= -1.0
        
        # Should maintain relative amplitudes
        assert processed[0] > processed[2]  # 2.0 > 1.5 relationship maintained
    
    @pytest.mark.unit
    def test_preprocess_audio_empty(self, transcriber):
        """Test preprocessing with empty audio."""
        empty_audio = np.array([], dtype=np.float32)
        processed = transcriber.preprocess_audio(empty_audio)
        
        assert isinstance(processed, np.ndarray)
        assert len(processed) == 0
        assert processed.dtype == np.float32
    
    @pytest.mark.unit
    def test_preprocess_audio_different_dtypes(self, transcriber):
        """Test preprocessing with different input data types."""
        # Test with int16 (common audio format)
        int16_audio = np.array([100, -100, 50, -50], dtype=np.int16)
        processed = transcriber.preprocess_audio(int16_audio)
        
        assert processed.dtype == np.float32
        assert np.max(processed) <= 1.0
        assert np.min(processed) >= -1.0
    
    @pytest.mark.unit
    @patch('transcriber.whisper.load_model')
    def test_transcribe_with_mock_whisper(self, mock_load_model, transcriber, sample_audio_data):
        """Test transcription with mocked Whisper model."""
        # Mock the Whisper model
        mock_model = Mock()
        mock_result = {
            'text': 'This is a test transcription',
            'segments': []
        }
        mock_model.transcribe.return_value = mock_result
        mock_load_model.return_value = mock_model
        
        # Force reload of model to use mock
        transcriber.model = None
        
        result = transcriber.transcribe(sample_audio_data)
        
        assert result['text'] == 'This is a test transcription'
        assert result['word_count'] == 5  # "This is a test transcription"
        assert result['duration'] > 0
        assert 'wpm' in result
    
    @pytest.mark.unit
    def test_transcribe_result_structure(self, transcriber):
        """Test that transcribe returns the expected result structure."""
        # Use minimal audio data to avoid long processing
        minimal_audio = np.array([0.1, -0.1, 0.05, -0.05], dtype=np.float32)
        
        with patch.object(transcriber, '_get_model') as mock_get_model:
            mock_model = Mock()
            mock_model.transcribe.return_value = {
                'text': 'test',
                'segments': []
            }
            mock_get_model.return_value = mock_model
            
            result = transcriber.transcribe(minimal_audio)
            
            # Check required keys
            required_keys = ['text', 'word_count', 'duration', 'wpm']
            for key in required_keys:
                assert key in result, f"Missing required key: {key}"
            
            # Check data types
            assert isinstance(result['text'], str)
            assert isinstance(result['word_count'], int)
            assert isinstance(result['duration'], (int, float))
            assert isinstance(result['wpm'], (int, float))
    
    @pytest.mark.unit
    def test_word_count_calculation(self, transcriber):
        """Test word counting logic."""
        test_cases = [
            ("", 0),
            ("word", 1),
            ("two words", 2),
            ("  spaced   words  ", 2),
            ("one,two,three", 1),  # No spaces, counts as one
            ("one two three", 3),
            ("hello world!", 2),
            ("testing, one, two, three words", 5)
        ]
        
        for text, expected_count in test_cases:
            # Mock transcribe to return specific text
            with patch.object(transcriber, '_get_model') as mock_get_model:
                mock_model = Mock()
                mock_model.transcribe.return_value = {
                    'text': text,
                    'segments': []
                }
                mock_get_model.return_value = mock_model
                
                result = transcriber.transcribe(np.array([0.1], dtype=np.float32))
                assert result['word_count'] == expected_count, f"Text '{text}' should have {expected_count} words, got {result['word_count']}"