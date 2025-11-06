"""Tests for Ollama provider."""
import pytest
from unittest.mock import patch, MagicMock
import sys


def test_fix_malformed_json():
    """Test JSON fixing utility."""
    # Mock ollama before importing
    with patch.dict('sys.modules', {'ollama': MagicMock()}):
        from src.core.ollama_provider import fix_malformed_json
        
        malformed = '{"key1": "value1"\n"key2": "value2"}'
        fixed = fix_malformed_json(malformed)
        # Should add comma between properties
        assert ',' in fixed


@pytest.mark.asyncio
async def test_ollama_provider_creation():
    """Test creating an Ollama provider."""
    # Mock ollama module
    mock_ollama = MagicMock()
    mock_ollama.list.return_value = []
    
    with patch.dict('sys.modules', {'ollama': mock_ollama}):
        from src.core.ollama_provider import SelfHostedOllamaProvider
        
        provider = SelfHostedOllamaProvider(
            endpoint="http://localhost:11434",
            model="gemma2:2b",
            temperature=0.3
        )
        
        info = provider.get_provider_info()
        assert info["name"] == "SelfHostedOllama"
        assert info["model"] == "gemma2:2b"
        
        # Test initialization
        await provider.initialize()
        assert provider._initialized is True
        mock_ollama.list.assert_called_once()


@pytest.mark.asyncio
async def test_ollama_provider_analyze_emotion():
    """Test emotion analysis with Ollama provider."""
    # Mock ollama module
    mock_ollama = MagicMock()
    mock_ollama.list.return_value = []
    mock_ollama.generate.return_value = {
        'response': '{"emotional_state": "calm", "confidence": 0.8, "social_cue": "appropriate", "speech_pace": "normal", "word_count": 10, "filler_words": [], "overly_critical": false, "coaching": "Continue as you are"}'
    }
    
    with patch.dict('sys.modules', {'ollama': mock_ollama}):
        from src.core.ollama_provider import SelfHostedOllamaProvider
        
        provider = SelfHostedOllamaProvider(
            endpoint="http://localhost:11434",
            model="gemma2:2b",
            temperature=0.3
        )
        
        await provider.initialize()
        
        result = await provider.analyze_emotion("This is a test text")
        
        assert result["emotional_state"] == "calm"
        assert result["confidence"] == 0.8
        assert result["social_cue"] == "appropriate"
        mock_ollama.generate.assert_called_once()


@pytest.mark.asyncio
async def test_ollama_provider_handles_markdown_json():
    """Test that provider handles JSON wrapped in markdown code blocks."""
    # Mock ollama module
    mock_ollama = MagicMock()
    mock_ollama.list.return_value = []
    mock_ollama.generate.return_value = {
        'response': '```json\n{"emotional_state": "engaged", "confidence": 0.9, "social_cue": "appropriate", "speech_pace": "normal", "word_count": 15, "filler_words": ["um"], "overly_critical": false, "coaching": "Good engagement"}\n```'
    }
    
    with patch.dict('sys.modules', {'ollama': mock_ollama}):
        from src.core.ollama_provider import SelfHostedOllamaProvider
        
        provider = SelfHostedOllamaProvider(
            endpoint="http://localhost:11434",
            model="gemma2:2b",
            temperature=0.3
        )
        
        await provider.initialize()
        result = await provider.analyze_emotion("Test with markdown")
        
        assert result["emotional_state"] == "engaged"
        assert result["confidence"] == 0.9


@pytest.mark.asyncio
async def test_ollama_provider_handles_json_parse_error():
    """Test that provider returns safe defaults on JSON parse error."""
    # Mock ollama module
    mock_ollama = MagicMock()
    mock_ollama.list.return_value = []
    mock_ollama.generate.return_value = {
        'response': 'This is not valid JSON'
    }
    
    with patch.dict('sys.modules', {'ollama': mock_ollama}):
        from src.core.ollama_provider import SelfHostedOllamaProvider
        
        provider = SelfHostedOllamaProvider(
            endpoint="http://localhost:11434",
            model="gemma2:2b",
            temperature=0.3
        )
        
        await provider.initialize()
        result = await provider.analyze_emotion("Test error handling")
        
        # Should return safe defaults
        assert result["emotional_state"] == "unknown"
        assert result["confidence"] == 0.0
        assert result["social_cue"] == "appropriate"
        assert "error" in result
