"""
Factory for creating model provider instances based on configuration.
"""
from typing import Dict, Any
from src.config import ModelConfig
from .model_provider import BaseModelProvider


class ModelProviderFactory:
    """Factory for creating model providers based on configuration."""
    
    @staticmethod
    async def create_provider(config: ModelConfig = None) -> BaseModelProvider:
        """
        Create a model provider based on configuration.
        
        Args:
            config: ModelConfig instance (creates new one if None)
        
        Returns:
            Initialized BaseModelProvider instance
        
        Raises:
            ValueError: If model mode is unknown or configuration is invalid
        """
        if config is None:
            config = ModelConfig()
        
        mode = config.get_mode()
        analysis_config = config.get_analysis_config()
        
        if mode == 'self_hosted':
            # Create Ollama provider (lazy import to avoid dependency issues)
            from .ollama_provider import SelfHostedOllamaProvider
            
            self_hosted_config = config.get_self_hosted_config()
            
            provider = SelfHostedOllamaProvider(
                endpoint=self_hosted_config.get('endpoint', 'http://localhost:11434'),
                model=self_hosted_config.get('model', 'gemma2:2b'),
                temperature=analysis_config.get('temperature', 0.3),
                timeout=self_hosted_config.get('timeout', 30)
            )
            
            # Initialize the provider
            await provider.initialize()
            return provider
        
        elif mode == 'local':
            # Create local model provider (stub for Phase 2, lazy import)
            from .local_provider import LocalModelProvider
            
            local_config = config.get_local_config()
            
            provider = LocalModelProvider(
                model_path=local_config.get('model_path', 'models/tinyllama.gguf'),
                threads=local_config.get('threads', 4),
                context_size=local_config.get('context_size', 2048)
            )
            
            # This will raise NotImplementedError for now
            await provider.initialize()
            return provider
        
        else:
            raise ValueError(
                f"Unknown model mode: {mode}. "
                f"Supported modes: 'self_hosted', 'local'"
            )
    
    @staticmethod
    def get_available_modes() -> Dict[str, Any]:
        """
        Get information about available model modes.
        
        Returns:
            Dictionary describing available modes
        """
        return {
            "modes": {
                "self_hosted": {
                    "description": "Use self-hosted Ollama (local or remote)",
                    "status": "available",
                    "requirements": ["Ollama installed and running"]
                },
                "local": {
                    "description": "Use local embedded model (TinyLlama, etc)",
                    "status": "coming_in_phase_2",
                    "requirements": ["GGUF model file", "llama-cpp-python"]
                }
            }
        }
