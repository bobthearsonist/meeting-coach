"""Tests for configuration loading."""
import pytest
from pathlib import Path
from src.config import ModelConfig


def test_model_config_loads():
    """Test that ModelConfig loads successfully."""
    config = ModelConfig()
    assert config.get_mode() in ['self_hosted', 'local']


def test_model_config_get_self_hosted():
    """Test getting self-hosted configuration."""
    config = ModelConfig()
    self_hosted = config.get_self_hosted_config()
    assert 'endpoint' in self_hosted
    assert 'model' in self_hosted


def test_model_config_get_analysis():
    """Test getting analysis configuration."""
    config = ModelConfig()
    analysis = config.get_analysis_config()
    assert 'min_words' in analysis
    assert 'temperature' in analysis
