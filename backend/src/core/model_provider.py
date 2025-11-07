"""
Base interface for model providers.
Abstract interface for LLM providers (Ollama, local models, etc).
Implements factory/strategy pattern for different model backends.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseModelProvider(ABC):
    """Abstract base class for LLM model providers."""

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the model provider and any necessary resources.

        Raises:
            ConnectionError: If connection to model fails
            ValueError: If configuration is invalid
            Exception: If initialization fails
        """
        pass

    @abstractmethod
    async def analyze_emotion(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze emotion and communication patterns in text.

        Args:
            text: Text to analyze
            context: Optional previous analysis context

        Returns:
            Dictionary containing analysis results with keys:
                - emotional_state: str
                - confidence: float (0.0-1.0)
                - social_cue: str
                - speech_pace: str
                - word_count: int
                - filler_words: list
                - overly_critical: bool
                - coaching: str

        Raises:
            RuntimeError: If provider not initialized
            ValueError: If text is invalid
            Exception: If analysis fails
        """
        pass

    @abstractmethod
    async def dispose(self) -> None:
        """
        Cleanup resources and connections.
        Should be called when provider is no longer needed.
        """
        pass

    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this provider.

        Returns:
            Dictionary with provider metadata (name, version, model, config)
        """
        pass
