"""
Base interface for model providers.
Implements factory/strategy pattern for different model backends.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseModelProvider(ABC):
    """Abstract base class for model providers."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the provider and any necessary resources.
        
        Raises:
            Exception: If initialization fails
        """
        pass
    
    @abstractmethod
    async def analyze_emotion(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze emotion and communication patterns from text.
        
        Args:
            text: The transcript text to analyze
            context: Optional context from previous analyses
        
        Returns:
            Analysis results dictionary with keys:
                - emotional_state: str
                - confidence: float
                - social_cue: str
                - speech_pace: str
                - word_count: int
                - filler_words: list
                - overly_critical: bool
                - coaching: str
        
        Raises:
            Exception: If analysis fails
        """
        pass
    
    @abstractmethod
    async def dispose(self) -> None:
        """
        Cleanup resources and close connections.
        """
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this provider.
        
        Returns:
            Dictionary with provider metadata (name, version, config)
        """
        pass
