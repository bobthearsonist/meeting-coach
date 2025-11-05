"""Tests for model factory."""
import pytest
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
    # This will use model_config.yaml
    provider = await ModelProviderFactory.create_provider()
    assert isinstance(provider, BaseModelProvider)
    
    # Clean up
    await provider.dispose()
