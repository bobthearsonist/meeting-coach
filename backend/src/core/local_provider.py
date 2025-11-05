"""
Local embedded model provider (future implementation).
Placeholder for Phase 2.
"""
from typing import Dict, Any
from .model_provider import BaseModelProvider


class LocalModelProvider(BaseModelProvider):
    """Provider for local embedded models (TinyLlama, etc). Coming in Phase 2."""
    
    def __init__(self, model_path: str, threads: int = 4, context_size: int = 2048):
        """
        Initialize local model provider.
        
        Args:
            model_path: Path to GGUF model file
            threads: Number of CPU threads
            context_size: Context window size
        """
        self.model_path = model_path
        self.threads = threads
        self.context_size = context_size
    
    async def initialize(self) -> None:
        """Initialize local model."""
        raise NotImplementedError(
            "Local embedded model support coming in Phase 2. "
            "Please use 'self_hosted' mode with Ollama for now."
        )
    
    async def analyze_emotion(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze emotion using local model."""
        raise NotImplementedError("Coming in Phase 2")
    
    async def dispose(self) -> None:
        """Cleanup resources."""
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information."""
        return {
            "name": "LocalModel",
            "version": "0.0.1-stub",
            "model_path": self.model_path,
            "status": "not_implemented"
        }
