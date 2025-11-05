"""Tests for model provider base class."""
import pytest
from src.core.model_provider import BaseModelProvider


def test_base_provider_is_abstract():
    """Test that BaseModelProvider cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseModelProvider()
