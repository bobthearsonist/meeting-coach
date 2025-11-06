"""Tests for model factory."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.core.model_factory import ModelProviderFactory
from src.core.model_provider import BaseModelProvider


def test_get_available_modes():
    """Test getting available modes."""
    modes = ModelProviderFactory.get_available_modes()
    assert "modes" in modes
    assert "self_hosted" in modes["modes"]
    assert "local" in modes["modes"]


@pytest.mark.asyncio
async def test_create_provider_default():
    """Test creating provider with default config."""
    # Mock ollama module
    mock_ollama = MagicMock()
    mock_ollama.list.return_value = []
    
    with patch.dict('sys.modules', {'ollama': mock_ollama}):
        # This will use default config
        provider = await ModelProviderFactory.create_provider()
        assert isinstance(provider, BaseModelProvider)
        
        # Verify ollama was called during initialization
        mock_ollama.list.assert_called()
        
        # Clean up
        await provider.dispose()


@pytest.mark.asyncio
async def test_create_provider_self_hosted():
    """Test creating self_hosted provider with custom config."""
    from src.config import ModelConfig
    
    # Mock ollama module
    mock_ollama = MagicMock()
    mock_ollama.list.return_value = []
    
    with patch.dict('sys.modules', {'ollama': mock_ollama}):
        config = ModelConfig(mode='self_hosted')
        provider = await ModelProviderFactory.create_provider(config)
        
        assert isinstance(provider, BaseModelProvider)
        info = provider.get_provider_info()
        assert info["name"] == "SelfHostedOllama"
        
        await provider.dispose()


@pytest.mark.asyncio
async def test_create_provider_local_raises_not_implemented():
    """Test that local provider raises NotImplementedError."""
    from src.config import ModelConfig
    
    config = ModelConfig(mode='local')
    
    with pytest.raises(NotImplementedError, match="Phase 2"):
        await ModelProviderFactory.create_provider(config)


@pytest.mark.asyncio
async def test_create_provider_unknown_mode_raises_error():
    """Test that unknown mode raises ValueError."""
    from src.config import ModelConfig
    
    # Create a mock config with unknown mode
    config = MagicMock()
    config.get_mode.return_value = 'unknown_mode'
    config.get_analysis_config.return_value = {'temperature': 0.3}
    
    with pytest.raises(ValueError, match="Unknown model mode"):
        await ModelProviderFactory.create_provider(config)
