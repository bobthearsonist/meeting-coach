"""Tests for prompt engine."""
import pytest
from src.core import prompts


def test_emotion_analysis_prompt():
    """Test emotion analysis prompt generation."""
    prompt = prompts.get_emotion_analysis_prompt("This is a test")
    assert "This is a test" in prompt
    assert "emotional_state" in prompt


def test_get_all_prompts():
    """Test getting all prompts."""
    all_prompts = prompts.get_all_prompts()
    assert "version" in all_prompts
    assert "prompts" in all_prompts
    assert "emotion_analysis" in all_prompts["prompts"]


def test_system_prompt():
    """Test system prompt."""
    system = prompts.get_system_prompt()
    assert len(system) > 0
    assert "supportive" in system.lower()
