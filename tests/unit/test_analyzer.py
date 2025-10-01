"""
Unit tests for the CommunicationAnalyzer module.
Tests the tone analysis, emoji mapping, alert logic, and summary generation.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

import analyzer
import config


class TestCommunicationAnalyzer:
    """Test suite for CommunicationAnalyzer class."""

    @pytest.fixture
    def mock_ollama_response(self):
        """Mock Ollama response for testing."""
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

    @pytest.fixture
    def mock_analyzer(self):
        """Create analyzer instance with mocked Ollama connection."""
        with patch('analyzer.ollama.list'):
            return analyzer.CommunicationAnalyzer(model="test-model")

    @pytest.fixture
    def sample_analysis_results(self):
        """Sample analysis results for testing summary generation."""
        return [
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
                'tone': 'engaged',
                'confidence': 0.9,
                'suggestions': 'Good enthusiasm',
                'key_indicators': ['excited', 'great']
            }
        ]

    def test_init_with_default_model(self):
        """Test analyzer initialization with default model."""
        with patch('analyzer.ollama.list'):
            analyzer_instance = analyzer.CommunicationAnalyzer()
            assert analyzer_instance.model == config.OLLAMA_MODEL

    def test_init_with_custom_model(self):
        """Test analyzer initialization with custom model."""
        custom_model = "custom-test-model"
        with patch('analyzer.ollama.list'):
            analyzer_instance = analyzer.CommunicationAnalyzer(model=custom_model)
            assert analyzer_instance.model == custom_model

    def test_init_ollama_connection_error(self, capsys):
        """Test initialization when Ollama is not available."""
        with patch('analyzer.ollama.list', side_effect=Exception("Connection failed")):
            analyzer_instance = analyzer.CommunicationAnalyzer()
            captured = capsys.readouterr()
            assert "Warning: Could not connect to Ollama" in captured.out
            assert "Make sure Ollama is running" in captured.out

    def test_analyze_tone_insufficient_text(self, mock_analyzer):
        """Test analysis with insufficient text returns appropriate error."""
        short_text = "Hello there"  # Less than MIN_WORDS_FOR_ANALYSIS

        result = mock_analyzer.analyze_tone(short_text)

        assert result['tone'] == 'unknown'
        assert result['confidence'] == 0.0
        assert result['error'] == 'insufficient_text'
        assert result['suggestions'] == 'Not enough content to analyze'

    def test_analyze_tone_successful_analysis(self, mock_analyzer):
        """Test successful tone analysis with valid response."""
        mock_ollama_response = {
            'response': json.dumps({
                'emotional_state': 'engaged',
                'social_cues': 'appropriate',
                'speech_pattern': 'normal',
                'confidence': 0.8,
                'key_indicators': ['appreciate', 'great point'],
                'coaching_feedback': 'Continue as you are'
            })
        }

        with patch('analyzer.ollama.generate', return_value=mock_ollama_response):
            text = "I really appreciate your input on this project. That's a great point you've made and I value your perspective."
            result = mock_analyzer.analyze_tone(text)

            assert result['emotional_state'] == 'engaged'
            assert result['social_cues'] == 'appropriate'
            assert result['speech_pattern'] == 'normal'
            assert result['confidence'] == 0.8
            assert 'appreciate' in result['key_indicators']
            assert result['coaching_feedback'] == 'Continue as you are'

            # Test backward compatibility
            assert result['tone'] == result['emotional_state']
            assert result['suggestions'] == result['coaching_feedback']

    def test_analyze_tone_markdown_wrapped_json(self, mock_analyzer):
        """Test parsing JSON response wrapped in markdown code blocks."""
        json_content = {
            'emotional_state': 'calm',
            'social_cues': 'appropriate',
            'speech_pattern': 'normal',
            'confidence': 0.7,
            'key_indicators': ['test'],
            'coaching_feedback': 'Good work'
        }

        mock_generate_response = {
            'response': f"```json\n{json.dumps(json_content)}\n```"
        }

        with patch('analyzer.ollama.generate', return_value=mock_generate_response):
            text = "This is a test message with enough words to trigger analysis and reach the JSON parsing code paths successfully."
            result = mock_analyzer.analyze_tone(text)

            assert result['emotional_state'] == 'calm'
            assert result['confidence'] == 0.7

    def test_analyze_tone_plain_code_blocks(self, mock_analyzer):
        """Test parsing JSON response wrapped in plain code blocks."""
        json_content = {
            'emotional_state': 'neutral',
            'social_cues': 'appropriate',
            'speech_pattern': 'normal',
            'confidence': 0.5,
            'key_indicators': [],
            'coaching_feedback': 'Continue'
        }

        mock_generate_response = {
            'response': f"```\n{json.dumps(json_content)}\n```"
        }

        with patch('analyzer.ollama.generate', return_value=mock_generate_response):
            text = "This is another test message with sufficient content for analysis and reaching the JSON parsing code paths."
            result = mock_analyzer.analyze_tone(text)

            assert result['emotional_state'] == 'neutral'
            assert result['confidence'] == 0.5

    def test_analyze_tone_json_parse_error(self, mock_analyzer, capsys):
        """Test handling of invalid JSON response."""
        mock_generate_response = {
            'response': "Invalid JSON response from LLM"
        }

        with patch('analyzer.ollama.generate', return_value=mock_generate_response):
            text = "This is a test message with enough words to trigger analysis and reach the error handling code paths successfully."
            result = mock_analyzer.analyze_tone(text)

            assert result['tone'] == 'neutral'
            assert result['confidence'] == 0.0
            assert result['error'] == 'parse_error'
            assert result['suggestions'] == 'Analysis error'

            captured = capsys.readouterr()
            assert "Error parsing LLM response" in captured.out

    def test_analyze_tone_ollama_exception(self, mock_analyzer, capsys):
        """Test handling of Ollama API exceptions."""
        with patch('analyzer.ollama.generate', side_effect=Exception("Ollama API error")):
            text = "This is a test message with enough words to trigger analysis and reach the error handling code paths successfully."
            result = mock_analyzer.analyze_tone(text)

            assert result['tone'] == 'neutral'
            assert result['confidence'] == 0.0
            assert 'Ollama API error' in result['error']
            assert result['suggestions'] == 'Analysis unavailable'

            captured = capsys.readouterr()
            assert "Error during analysis" in captured.out

    def test_get_tone_emoji_known_tones(self, mock_analyzer):
        """Test emoji mapping for known tones."""
        assert mock_analyzer.get_tone_emoji('supportive') == '🤝'
        assert mock_analyzer.get_tone_emoji('dismissive') == '🙄'
        assert mock_analyzer.get_tone_emoji('neutral') == '😐'
        assert mock_analyzer.get_tone_emoji('aggressive') == '😤'
        assert mock_analyzer.get_tone_emoji('elevated') == '⬆️'
        assert mock_analyzer.get_tone_emoji('calm') == '🧘'

    def test_get_tone_emoji_case_insensitive(self, mock_analyzer):
        """Test emoji mapping is case insensitive."""
        assert mock_analyzer.get_tone_emoji('SUPPORTIVE') == '🤝'
        assert mock_analyzer.get_tone_emoji('Dismissive') == '🙄'
        assert mock_analyzer.get_tone_emoji('ELEVATED') == '⬆️'

    def test_get_tone_emoji_unknown_tone(self, mock_analyzer):
        """Test emoji mapping for unknown tones returns default."""
        assert mock_analyzer.get_tone_emoji('unknown_tone') == '💬'
        assert mock_analyzer.get_tone_emoji('') == '💬'

    def test_get_social_cue_emoji_known_cues(self, mock_analyzer):
        """Test emoji mapping for known social cues."""
        assert mock_analyzer.get_social_cue_emoji('interrupting') == '✋'
        assert mock_analyzer.get_social_cue_emoji('dominating') == '🎤'
        assert mock_analyzer.get_social_cue_emoji('appropriate') == '👍'
        assert mock_analyzer.get_social_cue_emoji('off_topic') == '🔄'

    def test_get_social_cue_emoji_unknown_cue(self, mock_analyzer):
        """Test emoji mapping for unknown social cues returns default."""
        assert mock_analyzer.get_social_cue_emoji('unknown_cue') == '💬'

    def test_should_alert_elevated_states(self, mock_analyzer):
        """Test alert logic for elevated emotional states."""
        assert mock_analyzer.should_alert('elevated', 0.8) == True
        assert mock_analyzer.should_alert('intense', 0.9) == True
        assert mock_analyzer.should_alert('rapid', 0.7) == True
        assert mock_analyzer.should_alert('overwhelmed', 0.8) == True

    def test_should_alert_social_concerns(self, mock_analyzer):
        """Test alert logic for social concerns."""
        assert mock_analyzer.should_alert('dismissive', 0.8) == True
        assert mock_analyzer.should_alert('aggressive', 0.9) == True
        assert mock_analyzer.should_alert('interrupting', 0.7) == True
        assert mock_analyzer.should_alert('dominating', 0.8) == True

    def test_should_alert_low_confidence(self, mock_analyzer):
        """Test alert logic with low confidence scores."""
        assert mock_analyzer.should_alert('elevated', 0.5) == False
        assert mock_analyzer.should_alert('aggressive', 0.6) == False
        assert mock_analyzer.should_alert('intense', 0.69) == False

    def test_should_alert_normal_states(self, mock_analyzer):
        """Test alert logic for normal/positive states."""
        assert mock_analyzer.should_alert('calm', 0.9) == False
        assert mock_analyzer.should_alert('engaged', 0.8) == False
        assert mock_analyzer.should_alert('neutral', 0.7) == False

    def test_should_alert_custom_threshold(self, mock_analyzer):
        """Test alert logic with custom confidence threshold."""
        assert mock_analyzer.should_alert('elevated', 0.6, threshold=0.5) == True
        assert mock_analyzer.should_alert('elevated', 0.4, threshold=0.5) == False

    def test_should_social_cue_alert_concerning_cues(self, mock_analyzer):
        """Test social cue alert logic for concerning patterns."""
        assert mock_analyzer.should_social_cue_alert('interrupting', 0.8) == True
        assert mock_analyzer.should_social_cue_alert('dominating', 0.9) == True
        assert mock_analyzer.should_social_cue_alert('too_quiet', 0.7) == True
        assert mock_analyzer.should_social_cue_alert('off_topic', 0.8) == True
        assert mock_analyzer.should_social_cue_alert('repetitive', 0.75) == True

    def test_should_social_cue_alert_appropriate_behavior(self, mock_analyzer):
        """Test social cue alert logic for appropriate behavior."""
        assert mock_analyzer.should_social_cue_alert('appropriate', 0.9) == False
        assert mock_analyzer.should_social_cue_alert('normal', 0.8) == False

    def test_should_social_cue_alert_low_confidence(self, mock_analyzer):
        """Test social cue alert logic with low confidence."""
        assert mock_analyzer.should_social_cue_alert('interrupting', 0.5) == False
        assert mock_analyzer.should_social_cue_alert('dominating', 0.6) == False

    def test_generate_summary_empty_analyses(self, mock_analyzer):
        """Test summary generation with empty analysis list."""
        result = mock_analyzer.generate_summary([])
        assert 'error' in result
        assert result['error'] == 'No analyses to summarize'

    def test_generate_summary_single_analysis(self, mock_analyzer):
        """Test summary generation with single analysis."""
        analyses = [{
            'tone': 'engaged',
            'confidence': 0.8,
            'suggestions': 'Keep up the good work'
        }]

        result = mock_analyzer.generate_summary(analyses)

        assert result['dominant_tone'] == 'engaged'
        assert result['tone_distribution'] == {'engaged': 1}
        assert result['average_confidence'] == 0.8
        assert 'Keep up the good work' in result['key_suggestions']
        assert result['total_analyses'] == 1

    def test_generate_summary_multiple_analyses(self, mock_analyzer, sample_analysis_results):
        """Test summary generation with multiple analyses."""
        result = mock_analyzer.generate_summary(sample_analysis_results)

        assert result['dominant_tone'] == 'engaged'  # Most frequent
        assert result['tone_distribution']['engaged'] == 2
        assert result['tone_distribution']['neutral'] == 1
        assert result['average_confidence'] == (0.8 + 0.6 + 0.9) / 3
        assert len(result['key_suggestions']) <= 3
        assert result['total_analyses'] == 3

    def test_generate_summary_confidence_calculation(self, mock_analyzer):
        """Test summary confidence calculation with missing confidence values."""
        analyses = [
            {'tone': 'calm', 'confidence': 0.7, 'suggestions': 'Good'},
            {'tone': 'neutral', 'suggestions': 'Okay'},  # Missing confidence
            {'tone': 'engaged', 'confidence': 0.9, 'suggestions': 'Great'}
        ]

        result = mock_analyzer.generate_summary(analyses)

        # Should handle missing confidence as 0
        expected_avg = (0.7 + 0 + 0.9) / 3
        assert abs(result['average_confidence'] - expected_avg) < 0.001

    def test_generate_summary_duplicate_suggestions(self, mock_analyzer):
        """Test summary generation removes duplicate suggestions."""
        analyses = [
            {'tone': 'engaged', 'confidence': 0.8, 'suggestions': 'Keep going'},
            {'tone': 'engaged', 'confidence': 0.7, 'suggestions': 'Keep going'},  # Duplicate
            {'tone': 'neutral', 'confidence': 0.6, 'suggestions': 'Try harder'}
        ]

        result = mock_analyzer.generate_summary(analyses)

        # Should only include unique suggestions
        assert len(result['key_suggestions']) == 2
        assert 'Keep going' in result['key_suggestions']
        assert 'Try harder' in result['key_suggestions']

    @pytest.mark.parametrize("tone,expected_emoji", [
        ('supportive', '🤝'),
        ('dismissive', '🙄'),
        ('neutral', '😐'),
        ('aggressive', '😤'),
        ('elevated', '⬆️'),
        ('calm', '🧘'),
        ('overly_critical', '👎'),
        ('unknown', '❓'),
        ('nonexistent', '💬')
    ])
    def test_tone_emoji_parametrized(self, mock_analyzer, tone, expected_emoji):
        """Parametrized test for tone emoji mapping."""
        assert mock_analyzer.get_tone_emoji(tone) == expected_emoji

    @pytest.mark.parametrize("confidence,threshold,expected", [
        (0.8, 0.7, True),   # Above threshold
        (0.6, 0.7, False),  # Below threshold
        (0.7, 0.7, True),   # At threshold
        (0.9, 0.5, True),   # Well above threshold
        (0.4, 0.5, False)   # Below threshold
    ])
    def test_alert_threshold_parametrized(self, mock_analyzer, confidence, threshold, expected):
        """Parametrized test for alert threshold logic."""
        result = mock_analyzer.should_alert('elevated', confidence, threshold)
        assert result == expected

    @pytest.mark.unit
    def test_get_tone_emoji_overly_critical(self, mock_analyzer):
        """Test emoji mapping for overly critical tone."""
        assert mock_analyzer.get_tone_emoji('overly_critical') == '👎'

    @pytest.mark.unit  
    def test_should_alert_overly_critical(self, mock_analyzer):
        """Test alert logic for overly critical emotional state."""
        assert mock_analyzer.should_alert('overly_critical', 0.8) == True
        assert mock_analyzer.should_alert('overly_critical', 0.6) == False  # Below threshold

    @pytest.mark.unit
    def test_analyze_tone_overly_critical_response(self, mock_analyzer):
        """Test successful analysis of overly critical language."""
        mock_response = {
            'response': json.dumps({
                'emotional_state': 'overly_critical',
                'social_cues': 'inappropriate',
                'speech_pattern': 'harsh',
                'confidence': 0.85,
                'key_indicators': ['harsh language', 'personal attack', 'dismissive tone'],
                'coaching_feedback': 'Consider using more constructive language when providing feedback.'
            })
        }

        with patch('analyzer.ollama.generate', return_value=mock_response):
            text = "That's a terrible idea and won't work at all. You clearly haven't thought this through properly and should reconsider."
            result = mock_analyzer.analyze_tone(text)

            assert result['emotional_state'] == 'overly_critical'
            assert result['social_cues'] == 'inappropriate'
            assert result['confidence'] == 0.85
            assert 'harsh language' in result['key_indicators']
            assert 'constructive language' in result['coaching_feedback']

            # Test backward compatibility
            assert result['tone'] == result['emotional_state']
