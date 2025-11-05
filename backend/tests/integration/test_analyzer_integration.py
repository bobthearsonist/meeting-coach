"""Integration tests for analyzer with new provider system."""
import pytest
from src.core.analyzer import CommunicationAnalyzer


@pytest.mark.asyncio
async def test_analyzer_initializes():
    """Test that analyzer initializes with provider."""
    analyzer = CommunicationAnalyzer()
    await analyzer.initialize()
    
    assert analyzer._initialized
    assert analyzer.model_provider is not None
    
    # Cleanup
    await analyzer.dispose()


@pytest.mark.asyncio
async def test_analyzer_minimum_words():
    """Test that analyzer respects minimum word count."""
    analyzer = CommunicationAnalyzer()
    await analyzer.initialize()
    
    # Test with insufficient words
    result = await analyzer.analyze_tone_async("short")
    assert result["emotional_state"] == "insufficient_data"
    
    # Cleanup
    await analyzer.dispose()
