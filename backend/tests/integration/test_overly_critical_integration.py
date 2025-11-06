"""
Integration test for overly critical speech analysis
"""

import json
import os
import sys
from unittest.mock import patch

import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.analyzer import CommunicationAnalyzer


class TestOverlyCriticalIntegration:
    """Integration tests for overly critical speech detection"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return CommunicationAnalyzer()

    @pytest.mark.integration
    def test_end_to_end_overly_critical_detection(self, analyzer):
        """Test complete flow: critical text → analysis → alert → emoji"""

        # Test cases with realistic overly critical speech (meeting the minimum word count)
        test_cases = [
            {
                "text": "This code is absolute garbage and completely unworkable. Whoever wrote this obviously has no idea what they're doing and should not be writing code.",
                "description": "Personal attack on competence",
            },
            {
                "text": "That's the stupidest suggestion I've ever heard in my entire career. You clearly don't understand the problem at all and are wasting everyone's valuable time here.",
                "description": "Insulting language with dismissal",
            },
            {
                "text": "I can't believe you would waste everyone's time with such a terrible and poorly thought out idea. This is completely wrong and shows poor judgment on your part.",
                "description": "Harsh criticism with personal judgment",
            },
        ]

        # Mock Ollama to simulate realistic overly critical detection
        with patch("src.core.analyzer.ollama.generate") as mock_generate:
            mock_generate.return_value = {
                "response": json.dumps(
                    {
                        "emotional_state": "overly_critical",
                        "social_cues": "inappropriate",
                        "speech_pattern": "harsh",
                        "confidence": 0.85,
                        "key_indicators": [
                            "harsh language",
                            "personal attack",
                            "dismissive tone",
                        ],
                        "coaching_feedback": "Consider using more constructive language when providing feedback. Focus on the work, not the person.",
                    }
                )
            }

            for case in test_cases:
                # Step 1: Analyze the text
                result = analyzer.analyze_tone(case["text"])

                # Step 2: Verify analysis detected overly critical behavior
                emotional_state = result.get("emotional_state", result.get("tone"))
                assert (
                    emotional_state == "overly_critical"
                ), f"Failed to detect overly critical pattern in: {case['description']}"

                # Step 3: Verify confidence is reasonable
                confidence = result.get("confidence", 0)
                assert (
                    confidence >= 0.7
                ), f"Confidence should be high for clear overly critical pattern: {case['description']}"

                # Step 4: Verify alert is triggered
                should_alert = analyzer.should_alert(emotional_state, confidence)
                assert (
                    should_alert == True
                ), f"Should trigger alert for overly critical behavior: {case['description']}"

                # Step 5: Verify correct emoji is returned
                emoji = analyzer.get_emotional_state_emoji(emotional_state)
                assert (
                    emoji == "👎"
                ), f"Should return thumbs down emoji for overly critical: {case['description']}"

                # Step 6: Verify coaching feedback is provided
                coaching = result.get(
                    "coaching_feedback", result.get("suggestions", "")
                )
                assert (
                    coaching and len(coaching) > 10
                ), f"Should provide meaningful coaching feedback: {case['description']}"

    @pytest.mark.integration
    def test_end_to_end_constructive_feedback_not_flagged(self, analyzer):
        """Test that constructive criticism doesn't get flagged as overly critical"""

        constructive_examples = [
            {
                "text": "I have some serious concerns about this technical approach and would like to explain the potential issues I see with this implementation.",
                "expected_state": "engaged",
            },
            {
                "text": "This implementation has some significant problems that need to be addressed, but I think we can work together to improve it substantially.",
                "expected_state": "calm",
            },
            {
                "text": "I respectfully disagree with this proposed solution, but I understand your reasoning completely. Here's an alternative approach that might work better.",
                "expected_state": "calm",
            },
        ]

        # Mock Ollama to simulate constructive feedback detection
        for case in constructive_examples:
            with patch("src.core.analyzer.ollama.generate") as mock_generate:
                mock_generate.return_value = {
                    "response": json.dumps(
                        {
                            "emotional_state": case["expected_state"],
                            "social_cues": "appropriate",
                            "speech_pattern": "clear",
                            "confidence": 0.8,
                            "key_indicators": [
                                "respectful",
                                "constructive",
                                "collaborative",
                            ],
                            "coaching_feedback": "Continue as you are - good constructive communication",
                        }
                    )
                }

                result = analyzer.analyze_tone(case["text"])

                # Should not be flagged as overly critical
                emotional_state = result.get("emotional_state", result.get("tone"))
                assert (
                    emotional_state != "overly_critical"
                ), f"Constructive feedback incorrectly flagged as overly critical: {case['text']}"

                # Should not trigger alert
                should_alert = analyzer.should_alert(
                    emotional_state, result.get("confidence", 0)
                )
                assert (
                    should_alert == False
                ), f"Constructive feedback should not trigger alert: {case['text']}"

    @pytest.mark.integration
    def test_overly_critical_with_different_confidence_levels(self, analyzer):
        """Test overly critical detection with various confidence levels"""

        test_text = "That's a horrible idea that will never work properly and shows a complete lack of understanding of the fundamental requirements we discussed."

        confidence_levels = [0.9, 0.8, 0.7, 0.6, 0.5]

        for confidence in confidence_levels:
            with patch("src.core.analyzer.ollama.generate") as mock_generate:
                mock_generate.return_value = {
                    "response": json.dumps(
                        {
                            "emotional_state": "overly_critical",
                            "social_cues": "inappropriate",
                            "speech_pattern": "harsh",
                            "confidence": confidence,
                            "key_indicators": ["harsh language"],
                            "coaching_feedback": "Consider more constructive language",
                        }
                    )
                }

                result = analyzer.analyze_tone(test_text)
                emotional_state = result.get("emotional_state", result.get("tone"))

                # Verify the analysis result
                assert emotional_state == "overly_critical"
                assert result.get("confidence") == confidence

                # Check alert logic based on confidence threshold
                should_alert = analyzer.should_alert(emotional_state, confidence)
                expected_alert = confidence >= 0.7  # Default threshold

                assert (
                    should_alert == expected_alert
                ), f"Alert logic incorrect for confidence {confidence}: expected {expected_alert}, got {should_alert}"

    @pytest.mark.integration
    def test_overly_critical_summary_generation(self, analyzer):
        """Test that overly critical behavior appears in analysis summaries"""

        # Simulate multiple analyses with overly critical patterns
        mock_analyses = [
            {
                "emotional_state": "overly_critical",
                "confidence": 0.8,
                "coaching_feedback": "Use more constructive language",
            },
            {
                "emotional_state": "calm",
                "confidence": 0.7,
                "coaching_feedback": "Continue as you are",
            },
            {
                "emotional_state": "overly_critical",
                "confidence": 0.9,
                "coaching_feedback": "Focus on the work, not the person",
            },
        ]

        summary = analyzer.generate_summary(mock_analyses)

        # Verify overly critical is captured in summary
        assert (
            summary["dominant_emotional_state"] == "overly_critical"
        ), "Overly critical should be dominant tone in summary"

        assert (
            "overly_critical" in summary["state_distribution"]
        ), "Overly critical should appear in state distribution"

        assert (
            summary["state_distribution"]["overly_critical"] == 2
        ), "Should count 2 overly critical instances"

        assert (
            len(summary["key_feedback"]) > 0
        ), "Should include suggestions for overly critical behavior"
