"""
Unit tests for the CommunicationAnalyzer class
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from analyzer import CommunicationAnalyzer
from tests.fixtures.conftest import MockOllamaResponse

class TestCommunicationAnalyzer:
    """Test cases for CommunicationAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return CommunicationAnalyzer()
    
    @pytest.mark.unit
    def test_get_tone_emoji_mapping(self, analyzer):
        """Test that tone emojis are correctly mapped."""
        expected_mappings = {
            'supportive': '💚',
            'dismissive': '⚠️',
            'neutral': '⚪',
            'aggressive': '🔴',
            'passive': '🔵',
            'unknown': '❓'
        }
        
        for tone, expected_emoji in expected_mappings.items():
            actual_emoji = analyzer.get_tone_emoji(tone)
            assert actual_emoji == expected_emoji, f"Expected {expected_emoji} for {tone}, got {actual_emoji}"
    
    @pytest.mark.unit
    def test_should_alert_logic(self, analyzer, communication_analysis_test_cases):
        """Test alert logic with various tone/confidence combinations."""
        for case in communication_analysis_test_cases:
            result = analyzer.should_alert(case['tone'], case['confidence'])
            assert result == case['should_alert'], (
                f"Alert logic failed for {case['tone']} with confidence {case['confidence']}: "
                f"expected {case['should_alert']}, got {result}"
            )
    
    @pytest.mark.unit 
    def test_should_alert_high_confidence_threshold(self, analyzer):
        """Test that alerts require high confidence."""
        # Test borderline confidence values
        assert not analyzer.should_alert('dismissive', 0.6)  # Below threshold
        assert analyzer.should_alert('dismissive', 0.7)      # At threshold
        assert analyzer.should_alert('dismissive', 0.8)      # Above threshold
    
    @pytest.mark.unit
    def test_should_alert_safe_tones_never_alert(self, analyzer):
        """Test that safe tones never trigger alerts regardless of confidence."""
        safe_tones = ['supportive', 'neutral', 'unknown']
        
        for tone in safe_tones:
            assert not analyzer.should_alert(tone, 1.0), f"{tone} should never alert"
            assert not analyzer.should_alert(tone, 0.9), f"{tone} should never alert"
    
    @pytest.mark.unit
    @pytest.mark.requires_ollama
    @patch('analyzer.ollama.chat')
    def test_analyze_with_mock_ollama(self, mock_chat, analyzer):
        """Test analysis with mocked Ollama response."""
        # Mock Ollama response
        mock_response = {
            'message': {
                'content': '{"tone": "supportive", "confidence": 0.8, "reasoning": "Positive language used"}'
            }
        }
        mock_chat.return_value = mock_response
        
        test_text = "I really appreciate your input on this project."
        result = analyzer.analyze(test_text)
        
        assert result['tone'] == 'supportive'
        assert result['confidence'] == 0.8
        assert 'reasoning' in result
        mock_chat.assert_called_once()
    
    @pytest.mark.unit
    @patch('analyzer.ollama.chat')
    def test_analyze_with_invalid_json_response(self, mock_chat, analyzer):
        """Test graceful handling of invalid JSON from Ollama."""
        # Mock invalid JSON response
        mock_response = {
            'message': {
                'content': 'This is not valid JSON'
            }
        }
        mock_chat.return_value = mock_response
        
        result = analyzer.analyze("Test text")
        
        # Should return default values when JSON parsing fails
        assert result['tone'] == 'unknown'
        assert result['confidence'] == 0.0
        assert 'error' in result['reasoning']
    
    @pytest.mark.unit
    @patch('analyzer.ollama.chat')
    def test_analyze_with_ollama_connection_error(self, mock_chat, analyzer):
        """Test handling of Ollama connection errors."""
        # Mock connection error
        mock_chat.side_effect = Exception("Connection failed")
        
        result = analyzer.analyze("Test text")
        
        assert result['tone'] == 'unknown'
        assert result['confidence'] == 0.0
        assert 'error' in result['reasoning'].lower()
    
    @pytest.mark.unit
    def test_analyze_empty_text(self, analyzer):
        """Test analysis with empty or whitespace-only text."""
        test_cases = ["", "   ", "\n\t   "]
        
        for text in test_cases:
            result = analyzer.analyze(text)
            assert result['tone'] == 'unknown'
            assert result['confidence'] == 0.0
    
    @pytest.mark.unit
    def test_get_tone_emoji_unknown_tone(self, analyzer):
        """Test emoji mapping for unknown/invalid tones."""
        unknown_tones = ['invalid', 'nonexistent', '', None]
        
        for tone in unknown_tones:
            emoji = analyzer.get_tone_emoji(tone)
            assert emoji == '❓', f"Unknown tone '{tone}' should return ❓"