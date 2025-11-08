"""
Base model provider interface for Meeting Coach.
Phase 1: Abstract interface for different model backends.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseModelProvider(ABC):
    """Abstract base class for model providers."""
    
    @abstractmethod
    async def initialize(self):
        """Initialize the provider (connect to service, load model, etc.)."""
        pass
    
    @abstractmethod
    async def analyze_emotion(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze emotional state and social cues in text.
        
        Args:
            text: Text to analyze
            context: Optional context from previous analysis
        
        Returns:
            Dictionary containing:
                - emotional_state: str
                - social_cue: str
                - speech_pace: str
                - confidence: float (0.0-1.0)
                - key_indicators: list of str
                - filler_words: list of str
                - overly_critical: bool
                - coaching: str
        """
        pass
    
    @abstractmethod
    async def dispose(self):
        """Cleanup resources."""
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this provider.
        
        Returns:
            Dictionary with provider metadata
        """
        pass
