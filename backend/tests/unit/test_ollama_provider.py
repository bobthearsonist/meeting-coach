"""Tests for Ollama provider."""
import pytest
from src.core.ollama_provider import SelfHostedOllamaProvider, fix_malformed_json


def test_fix_malformed_json():
    """Test JSON fixing utility."""
    malformed = '{"key1": "value1"\n"key2": "value2"}'
    fixed = fix_malformed_json(malformed)
    # Should add comma between properties
    assert ',' in fixed


@pytest.mark.asyncio
async def test_ollama_provider_creation():
    """Test creating an Ollama provider."""
    provider = SelfHostedOllamaProvider(
        endpoint="http://localhost:11434",
        model="gemma2:2b",
        temperature=0.3
    )
    
    info = provider.get_provider_info()
    assert info["name"] == "SelfHostedOllama"
    assert info["model"] == "gemma2:2b"
