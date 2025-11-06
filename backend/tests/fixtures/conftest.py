"""
Test fixtures and utilities for the meeting coach tests
"""

from typing import Any, Dict

import numpy as np
import pytest
from src import config


@pytest.fixture
def sample_audio_data():
    """Generate synthetic audio data for testing."""
    duration = 3.0
    sample_rate = config.SAMPLE_RATE
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create speech-like audio with multiple frequency components
    audio = (
        np.sin(2 * np.pi * 200 * t) * 0.1  # Low frequency
        + np.sin(2 * np.pi * 800 * t) * 0.05  # Mid frequency
        + np.random.normal(0, 0.01, len(t))  # Noise
    )

    # Apply envelope to simulate speech patterns
    envelope = np.concatenate(
        [
            np.linspace(0, 1, len(t) // 4),  # fade in
            np.ones(len(t) // 2),  # sustained
            np.linspace(1, 0, len(t) // 4),  # fade out
        ]
    )
    audio = audio * envelope

    return audio.astype(np.float32)


@pytest.fixture
def sample_transcription_results():
    """Sample transcription results for testing."""
    return [
        {
            "text": "I really appreciate your input on this project. That's a great point.",
            "word_count": 12,
            "duration": 5.0,
            "expected_tone": "supportive",
        },
        {
            "text": "Whatever, I don't really care about that. Let's just move on.",
            "word_count": 11,
            "duration": 4.0,
            "expected_tone": "dismissive",
        },
        {
            "text": "The quarterly results show a 15% increase in revenue.",
            "word_count": 9,
            "duration": 6.0,
            "expected_tone": "neutral",
        },
        {
            "text": "That's a terrible idea and won't work at all.",
            "word_count": 9,
            "duration": 3.0,
            "expected_tone": "aggressive",
        },
    ]


@pytest.fixture
def communication_analysis_test_cases():
    """Test cases for communication analysis."""
    return [
        {
            "tone": "supportive",
            "confidence": 0.8,
            "should_alert": False,
            "expected_emoji": "🤝",
        },
        {
            "tone": "dismissive",
            "confidence": 0.8,
            "should_alert": True,
            "expected_emoji": "🙄",
        },
        {
            "tone": "aggressive",
            "confidence": 0.9,
            "should_alert": True,
            "expected_emoji": "😤",
        },
        {
            "tone": "dismissive",
            "confidence": 0.5,  # Low confidence
            "should_alert": False,
            "expected_emoji": "🙄",
        },
        {
            "tone": "neutral",
            "confidence": 0.9,
            "should_alert": False,
            "expected_emoji": "😐",
        },
        {
            "tone": "overly_critical",
            "confidence": 0.8,
            "should_alert": True,
            "expected_emoji": "👎",
        },
        {
            "tone": "overly_critical",
            "confidence": 0.6,  # Low confidence
            "should_alert": False,
            "expected_emoji": "👎",
        },
    ]


@pytest.fixture
def dashboard_scenarios():
    """Scenarios for dashboard testing."""
    return [
        {
            "desc": "Starting meeting calmly",
            "state": "calm",
            "cue": "appropriate",
            "confidence": 0.8,
            "text": "Good morning everyone, thanks for joining",
            "coaching": "",
            "alert": False,
            "wpm": 140,
        },
        {
            "desc": "Getting interested",
            "state": "engaged",
            "cue": "appropriate",
            "confidence": 0.8,
            "text": "That's a really interesting point about the project",
            "coaching": "",
            "alert": False,
            "wpm": 150,
        },
        {
            "desc": "Excitement building",
            "state": "elevated",
            "cue": "interrupting",
            "confidence": 0.8,
            "text": "Oh wait, I just had this amazing idea we could implement!",
            "coaching": "You seem excited! Try taking a breath before sharing your idea.",
            "alert": True,
            "wpm": 170,
        },
    ]


class MockOllamaResponse:
    """Mock response for Ollama API calls."""

    def __init__(self, tone: str, confidence: float, reasoning: str = "Test reasoning"):
        self.tone = tone
        self.confidence = confidence
        self.reasoning = reasoning

    def to_dict(self):
        return {
            "tone": self.tone,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
        }
