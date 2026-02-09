"""
Unit tests for the CommunicationAnalyzer module.
Tests the tone analysis, emoji mapping, alert logic, and summary generation.
"""

import json
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from src import config
from src.core import analyzer
from src.core.response_models import AnalysisResponse


class TestCommunicationAnalyzer:
    """Test suite for CommunicationAnalyzer class."""

    @pytest.fixture
    def mock_analysis_response(self):
        """Mock AnalysisResponse for testing."""
        return AnalysisResponse(
            emotional_state="engaged",
            social_cues="appropriate",
            speech_pattern="normal",
            confidence=0.8,
            key_indicators=["appreciate", "great point"],
            coaching_feedback="Continue as you are",
        )

    @pytest.fixture
    def mock_analyzer(self):
        """Create analyzer instance with mocked Ollama connection and instructor client."""
        with (
            patch("src.core.analyzer.ollama.list"),
            patch("src.core.analyzer.instructor.from_openai") as mock_from_openai,
            patch("src.core.analyzer.OpenAI"),
        ):
            mock_client = MagicMock()
            mock_from_openai.return_value = mock_client
            instance = analyzer.CommunicationAnalyzer(model="test-model")
            return instance

    @pytest.fixture
    def sample_analysis_results(self):
        """Sample analysis results for testing summary generation."""
        return [
            {
                "emotional_state": "engaged",
                "confidence": 0.8,
                "coaching_feedback": "Continue as you are",
                "key_indicators": ["appreciate", "input"],
            },
            {
                "emotional_state": "neutral",
                "confidence": 0.6,
                "coaching_feedback": "Try to be more expressive",
                "key_indicators": ["results", "data"],
            },
            {
                "emotional_state": "engaged",
                "confidence": 0.9,
                "coaching_feedback": "Good enthusiasm",
                "key_indicators": ["excited", "great"],
            },
        ]

    def test_init_with_default_model(self):
        """Test analyzer initialization with default model."""
        with (
            patch("src.core.analyzer.ollama.list"),
            patch("src.core.analyzer.instructor.from_openai"),
            patch("src.core.analyzer.OpenAI"),
        ):
            analyzer_instance = analyzer.CommunicationAnalyzer()
            assert analyzer_instance.model == config.OLLAMA_MODEL

    def test_init_with_custom_model(self):
        """Test analyzer initialization with custom model."""
        custom_model = "custom-test-model"
        with (
            patch("src.core.analyzer.ollama.list"),
            patch("src.core.analyzer.instructor.from_openai"),
            patch("src.core.analyzer.OpenAI"),
        ):
            analyzer_instance = analyzer.CommunicationAnalyzer(model=custom_model)
            assert analyzer_instance.model == custom_model

    def test_init_ollama_connection_error(self, capsys):
        """Test initialization when Ollama is not available."""
        with (
            patch(
                "src.core.analyzer.ollama.list",
                side_effect=Exception("Connection failed"),
            ),
            patch("src.core.analyzer.instructor.from_openai"),
            patch("src.core.analyzer.OpenAI"),
        ):
            analyzer_instance = analyzer.CommunicationAnalyzer()
            captured = capsys.readouterr()
            assert "Warning: Could not connect to Ollama" in captured.out
            assert "Make sure Ollama is running" in captured.out

    def test_analyze_tone_insufficient_text(self, mock_analyzer):
        """Test analysis with insufficient text returns appropriate error."""
        short_text = "Hello there"  # Less than MIN_WORDS_FOR_ANALYSIS

        result = mock_analyzer.analyze_tone(short_text)

        assert result["emotional_state"] == "unknown"
        assert result["confidence"] == 0.0
        assert result["error"] == "insufficient_text"
        assert result["coaching_feedback"] == "Not enough content to analyze"

    def test_analyze_tone_successful_analysis(self, mock_analyzer):
        """Test successful tone analysis with instructor response."""
        mock_response = AnalysisResponse(
            emotional_state="engaged",
            social_cues="appropriate",
            speech_pattern="normal",
            confidence=0.8,
            key_indicators=["appreciate", "great point"],
            coaching_feedback="Continue as you are",
        )

        mock_analyzer.client.chat.completions.create.return_value = mock_response

        text = "I really appreciate your input on this project. That's a great point you've made and I value your perspective."
        result = mock_analyzer.analyze_tone(text)

        assert result["emotional_state"] == "engaged"
        assert result["social_cues"] == "appropriate"
        assert result["speech_pattern"] == "normal"
        assert result["confidence"] == 0.8
        assert "appreciate" in result["key_indicators"]
        assert result["coaching_feedback"] == "Continue as you are"

    def test_analyze_tone_uses_response_model(self, mock_analyzer):
        """Test that analyze_tone passes AnalysisResponse as the response_model."""
        mock_response = AnalysisResponse(
            emotional_state="calm",
            social_cues="appropriate",
            speech_pattern="normal",
            confidence=0.7,
            key_indicators=["test"],
            coaching_feedback="Good work",
        )
        mock_analyzer.client.chat.completions.create.return_value = mock_response

        text = "This is a test message with enough words to trigger analysis and reach the instructor code paths successfully."
        mock_analyzer.analyze_tone(text)

        call_kwargs = mock_analyzer.client.chat.completions.create.call_args
        assert call_kwargs.kwargs["response_model"] == AnalysisResponse

    def test_analyze_tone_returns_dict(self, mock_analyzer):
        """Test that analyze_tone returns a plain dict via model_dump."""
        mock_response = AnalysisResponse(
            emotional_state="calm",
            social_cues="appropriate",
            speech_pattern="normal",
            confidence=0.5,
            key_indicators=[],
            coaching_feedback="Continue",
        )
        mock_analyzer.client.chat.completions.create.return_value = mock_response

        text = "This is another test message with sufficient content for analysis and reaching the code paths."
        result = mock_analyzer.analyze_tone(text)

        assert isinstance(result, dict)
        assert result["emotional_state"] == "calm"
        assert result["confidence"] == 0.5

    def test_analyze_tone_instructor_exception(self, mock_analyzer, capsys):
        """Test handling of instructor/API exceptions."""
        mock_analyzer.client.chat.completions.create.side_effect = Exception(
            "API error"
        )

        text = "This is a test message with enough words to trigger analysis and reach the error handling code paths successfully."
        result = mock_analyzer.analyze_tone(text)

        assert result["emotional_state"] == "error"
        assert result["confidence"] == 0.0
        assert "API error" in result["error"]
        assert result["coaching_feedback"] == "Analysis unavailable"

        captured = capsys.readouterr()
        assert "Error during analysis" in captured.out

    def test_get_emotional_state_emoji_known_states(self, mock_analyzer):
        """Test emoji mapping for known emotional states."""
        assert mock_analyzer.get_emotional_state_emoji("supportive") == "\U0001f91d"
        assert mock_analyzer.get_emotional_state_emoji("dismissive") == "\U0001f644"
        assert mock_analyzer.get_emotional_state_emoji("neutral") == "\U0001f610"
        assert mock_analyzer.get_emotional_state_emoji("aggressive") == "\U0001f624"
        assert mock_analyzer.get_emotional_state_emoji("elevated") == "\u2b06\ufe0f"
        assert mock_analyzer.get_emotional_state_emoji("calm") == "\U0001f9d8"

    def test_get_emotional_state_emoji_case_insensitive(self, mock_analyzer):
        """Test emoji mapping is case insensitive."""
        assert mock_analyzer.get_emotional_state_emoji("SUPPORTIVE") == "\U0001f91d"
        assert mock_analyzer.get_emotional_state_emoji("Dismissive") == "\U0001f644"
        assert mock_analyzer.get_emotional_state_emoji("ELEVATED") == "\u2b06\ufe0f"

    def test_get_emotional_state_emoji_unknown_state(self, mock_analyzer):
        """Test emoji mapping for unknown states returns default."""
        assert mock_analyzer.get_emotional_state_emoji("unknown_state") == "\U0001f4ac"
        assert mock_analyzer.get_emotional_state_emoji("") == "\U0001f4ac"

    def test_get_social_cue_emoji_known_cues(self, mock_analyzer):
        """Test emoji mapping for known social cues."""
        assert mock_analyzer.get_social_cue_emoji("interrupting") == "\u270b"
        assert mock_analyzer.get_social_cue_emoji("dominating") == "\U0001f3a4"
        assert mock_analyzer.get_social_cue_emoji("appropriate") == "\U0001f44d"
        assert mock_analyzer.get_social_cue_emoji("off_topic") == "\U0001f504"

    def test_get_social_cue_emoji_unknown_cue(self, mock_analyzer):
        """Test emoji mapping for unknown social cues returns default."""
        assert mock_analyzer.get_social_cue_emoji("unknown_cue") == "\U0001f4ac"

    def test_should_alert_elevated_states(self, mock_analyzer):
        """Test alert logic for elevated emotional states."""
        assert mock_analyzer.should_alert("elevated", 0.8) == True
        assert mock_analyzer.should_alert("intense", 0.9) == True
        assert mock_analyzer.should_alert("rapid", 0.7) == True
        assert mock_analyzer.should_alert("overwhelmed", 0.8) == True

    def test_should_alert_social_concerns(self, mock_analyzer):
        """Test alert logic for social concerns."""
        assert mock_analyzer.should_alert("dismissive", 0.8) == True
        assert mock_analyzer.should_alert("aggressive", 0.9) == True
        # Social cues are now handled by should_social_cue_alert
        assert mock_analyzer.should_social_cue_alert("interrupting", 0.7) == True

    def test_should_alert_low_confidence(self, mock_analyzer):
        """Test alert logic with low confidence scores."""
        assert mock_analyzer.should_alert("elevated", 0.5) == False
        assert mock_analyzer.should_alert("aggressive", 0.6) == False
        assert mock_analyzer.should_alert("intense", 0.69) == False

    def test_should_alert_normal_states(self, mock_analyzer):
        """Test alert logic for normal/positive states."""
        assert mock_analyzer.should_alert("calm", 0.9) == False
        assert mock_analyzer.should_alert("engaged", 0.8) == False
        assert mock_analyzer.should_alert("neutral", 0.7) == False

    def test_should_alert_custom_threshold(self, mock_analyzer):
        """Test alert logic with custom confidence threshold."""
        assert mock_analyzer.should_alert("elevated", 0.6, threshold=0.5) == True
        assert mock_analyzer.should_alert("elevated", 0.4, threshold=0.5) == False

    def test_should_social_cue_alert_concerning_cues(self, mock_analyzer):
        """Test social cue alert logic for concerning patterns."""
        assert mock_analyzer.should_social_cue_alert("interrupting", 0.8) == True
        assert mock_analyzer.should_social_cue_alert("dominating", 0.9) == True
        assert mock_analyzer.should_social_cue_alert("too_quiet", 0.7) == True
        assert mock_analyzer.should_social_cue_alert("off_topic", 0.8) == True
        assert mock_analyzer.should_social_cue_alert("repetitive", 0.75) == True

    def test_should_social_cue_alert_appropriate_behavior(self, mock_analyzer):
        """Test social cue alert logic for appropriate behavior."""
        assert mock_analyzer.should_social_cue_alert("appropriate", 0.9) == False
        assert mock_analyzer.should_social_cue_alert("normal", 0.8) == False

    def test_should_social_cue_alert_low_confidence(self, mock_analyzer):
        """Test social cue alert logic with low confidence."""
        assert mock_analyzer.should_social_cue_alert("interrupting", 0.5) == False
        assert mock_analyzer.should_social_cue_alert("dominating", 0.6) == False

    def test_generate_summary_empty_analyses(self, mock_analyzer):
        """Test summary generation with empty analysis list."""
        result = mock_analyzer.generate_summary([])
        assert "error" in result
        assert result["error"] == "No analyses to summarize"

    def test_generate_summary_single_analysis(self, mock_analyzer):
        """Test summary generation with single analysis."""
        analyses = [
            {
                "emotional_state": "engaged",
                "confidence": 0.8,
                "coaching_feedback": "Keep up the good work",
            }
        ]

        result = mock_analyzer.generate_summary(analyses)

        assert result["dominant_emotional_state"] == "engaged"
        assert result["state_distribution"] == {"engaged": 1}
        assert result["average_confidence"] == 0.8
        assert "Keep up the good work" in result["key_feedback"]
        assert result["total_analyses"] == 1

    def test_generate_summary_multiple_analyses(
        self, mock_analyzer, sample_analysis_results
    ):
        """Test summary generation with multiple analyses."""
        result = mock_analyzer.generate_summary(sample_analysis_results)

        assert result["dominant_emotional_state"] == "engaged"  # Most frequent
        assert result["state_distribution"]["engaged"] == 2
        assert result["state_distribution"]["neutral"] == 1
        assert result["average_confidence"] == (0.8 + 0.6 + 0.9) / 3
        assert len(result["key_feedback"]) <= 3
        assert result["total_analyses"] == 3

    def test_generate_summary_confidence_calculation(self, mock_analyzer):
        """Test summary confidence calculation with missing confidence values."""
        analyses = [
            {"tone": "calm", "confidence": 0.7, "suggestions": "Good"},
            {"tone": "neutral", "suggestions": "Okay"},  # Missing confidence
            {"tone": "engaged", "confidence": 0.9, "suggestions": "Great"},
        ]

        result = mock_analyzer.generate_summary(analyses)

        # Should handle missing confidence as 0
        expected_avg = (0.7 + 0 + 0.9) / 3
        assert abs(result["average_confidence"] - expected_avg) < 0.001

    def test_generate_summary_duplicate_suggestions(self, mock_analyzer):
        """Test summary generation removes duplicate suggestions."""
        analyses = [
            {
                "emotional_state": "engaged",
                "confidence": 0.8,
                "coaching_feedback": "Keep going",
            },
            {
                "emotional_state": "engaged",
                "confidence": 0.7,
                "coaching_feedback": "Keep going",
            },  # Duplicate
            {
                "emotional_state": "neutral",
                "confidence": 0.6,
                "coaching_feedback": "Try harder",
            },
        ]

        result = mock_analyzer.generate_summary(analyses)

        # Should only include unique suggestions
        assert len(result["key_feedback"]) == 2
        assert "Keep going" in result["key_feedback"]
        assert "Try harder" in result["key_feedback"]

    @pytest.mark.parametrize(
        "emotional_state,expected_emoji",
        [
            ("supportive", "\U0001f91d"),
            ("dismissive", "\U0001f644"),
            ("neutral", "\U0001f610"),
            ("aggressive", "\U0001f624"),
            ("elevated", "\u2b06\ufe0f"),
            ("calm", "\U0001f9d8"),
            ("unknown", "\u2753"),
            ("nonexistent", "\U0001f4ac"),
        ],
    )
    def test_emotional_state_emoji_parametrized(
        self, mock_analyzer, emotional_state, expected_emoji
    ):
        """Parametrized test for emotional state emoji mapping."""
        assert (
            mock_analyzer.get_emotional_state_emoji(emotional_state) == expected_emoji
        )

    @pytest.mark.parametrize(
        "confidence,threshold,expected",
        [
            (0.8, 0.7, True),  # Above threshold
            (0.6, 0.7, False),  # Below threshold
            (0.7, 0.7, True),  # At threshold
            (0.9, 0.5, True),  # Well above threshold
            (0.4, 0.5, False),  # Below threshold
        ],
    )
    def test_alert_threshold_parametrized(
        self, mock_analyzer, confidence, threshold, expected
    ):
        """Parametrized test for alert threshold logic."""
        result = mock_analyzer.should_alert("elevated", confidence, threshold)
        assert result == expected

    @pytest.mark.unit
    def test_get_tone_emoji_overly_critical(self, mock_analyzer):
        """Test emoji mapping for overly critical tone."""
        assert (
            mock_analyzer.get_emotional_state_emoji("overly_critical") == "\U0001f44e"
        )

    @pytest.mark.unit
    def test_should_alert_overly_critical(self, mock_analyzer):
        """Test that overly critical behavior triggers alerts appropriately."""
        # High confidence should trigger alert
        assert mock_analyzer.should_alert("overly_critical", 0.8) == True
        assert mock_analyzer.should_alert("overly_critical", 0.9) == True

        # Low confidence should not trigger alert
        assert mock_analyzer.should_alert("overly_critical", 0.6) == False
        assert mock_analyzer.should_alert("overly_critical", 0.5) == False

        # Boundary case - exactly at threshold
        assert mock_analyzer.should_alert("overly_critical", 0.7) == True


class TestAnalysisResponse:
    """Test suite for the AnalysisResponse Pydantic model."""

    def test_defaults(self):
        """Test AnalysisResponse default values."""
        response = AnalysisResponse()
        assert response.emotional_state == "unknown"
        assert response.social_cues == "appropriate"
        assert response.speech_pattern == "normal"
        assert response.confidence == 0.5
        assert response.key_indicators == []
        assert response.coaching_feedback == "No specific suggestions"

    def test_custom_values(self):
        """Test AnalysisResponse with custom values."""
        response = AnalysisResponse(
            emotional_state="calm",
            social_cues="interrupting",
            speech_pattern="rushed",
            confidence=0.9,
            key_indicators=["fast", "urgent"],
            coaching_feedback="Slow down",
        )
        assert response.emotional_state == "calm"
        assert response.social_cues == "interrupting"
        assert response.confidence == 0.9

    def test_confidence_clamped(self):
        """Test that confidence outside 0-1 range raises validation error."""
        with pytest.raises(Exception):
            AnalysisResponse(confidence=1.5)
        with pytest.raises(Exception):
            AnalysisResponse(confidence=-0.1)

    def test_extra_fields_ignored(self):
        """Test that extra fields from LLM are silently ignored."""
        response = AnalysisResponse(
            emotional_state="calm",
            extra_field="should be ignored",
            another_extra=42,
        )
        assert response.emotional_state == "calm"
        assert not hasattr(response, "extra_field")

    def test_model_dump(self):
        """Test model_dump produces correct dict."""
        response = AnalysisResponse(
            emotional_state="engaged",
            confidence=0.8,
        )
        d = response.model_dump()
        assert isinstance(d, dict)
        assert d["emotional_state"] == "engaged"
        assert d["confidence"] == 0.8

    def test_invalid_emotional_state(self):
        """Test that invalid emotional state raises validation error."""
        with pytest.raises(Exception):
            AnalysisResponse(emotional_state="nonexistent_state")
