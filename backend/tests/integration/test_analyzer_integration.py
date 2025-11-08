"""Integration tests for analyzer with new provider system."""
import pytest
from unittest.mock import AsyncMock, Mock
from src.core.analyzer import CommunicationAnalyzer
from src.core.base_provider import BaseModelProvider


class MockProvider(BaseModelProvider):
    """Mock provider for testing."""
    
    async def initialize(self):
        """Mock initialize."""
        pass
    
    async def analyze_emotion(self, text: str, context: dict = None):
        """Mock analyze_emotion."""
        return {
            "emotional_state": "calm",
            "social_cue": "appropriate",
            "speech_pace": "normal",
            "confidence": 0.8,
            "key_indicators": ["test"],
            "filler_words": [],
            "overly_critical": False,
            "coaching": "Test coaching"
        }
    
    async def dispose(self):
        """Mock dispose."""
        pass
    
    def get_provider_info(self):
        """Mock get_provider_info."""
        return {
            'name': 'Mock Provider',
            'type': 'mock'
        }


@pytest.mark.asyncio
async def test_analyzer_initializes():
    """Test that analyzer initializes with provider."""
    mock_provider = MockProvider()
    analyzer = CommunicationAnalyzer(model_provider=mock_provider)
    await analyzer.initialize()
    
    assert analyzer._initialized
    assert analyzer.model_provider is not None
    
    # Cleanup
    await analyzer.dispose()


@pytest.mark.asyncio
async def test_analyzer_minimum_words():
    """Test that analyzer respects minimum word count."""
    mock_provider = MockProvider()
    analyzer = CommunicationAnalyzer(model_provider=mock_provider)
    await analyzer.initialize()
    
    # Test with insufficient words
    result = await analyzer.analyze_tone_async("short")
    assert result["emotional_state"] == "insufficient_data"
    
    # Cleanup
    await analyzer.dispose()


@pytest.mark.asyncio
async def test_analyzer_with_sufficient_words():
    """Test analyzer with sufficient words."""
    mock_provider = MockProvider()
    analyzer = CommunicationAnalyzer(model_provider=mock_provider)
    await analyzer.initialize()
    
    # Test with sufficient words (15+ words)
    text = "This is a test message with more than fifteen words to trigger the analysis properly and test the provider"
    result = await analyzer.analyze_tone_async(text)
    
    assert result["emotional_state"] == "calm"
    assert result["confidence"] == 0.8
    
    # Cleanup
    await analyzer.dispose()
