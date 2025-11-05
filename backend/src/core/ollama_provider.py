"""
Self-hosted Ollama model provider implementation.
"""
import ollama
import json
import re
from typing import Dict, Any, Optional
from .model_provider import BaseModelProvider
from . import prompts


def fix_malformed_json(text: str) -> str:
    """
    Attempt to fix common JSON formatting errors from LLM responses.
    
    Args:
        text: Potentially malformed JSON string
    
    Returns:
        Fixed JSON string
    """
    # Fix missing commas between array elements on different lines
    text = re.sub(r'"\s*\n\s*"', '",\n    "', text)
    
    # Fix missing commas between object properties
    text = re.sub(r'"\s*\n\s*"([a-z_]+)":', '",\n  "\\1":', text)
    
    return text


class SelfHostedOllamaProvider(BaseModelProvider):
    """Provider for self-hosted Ollama instances (local or remote)."""
    
    def __init__(self, endpoint: str, model: str, temperature: float = 0.3, timeout: int = 30):
        """
        Initialize Ollama provider.
        
        Args:
            endpoint: Ollama API endpoint (e.g., http://localhost:11434)
            model: Model name (e.g., gemma2:2b)
            temperature: Sampling temperature
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize connection to Ollama."""
        try:
            # Test connection
            ollama.list()
            self._initialized = True
            print(f"✓ Connected to Ollama at {self.endpoint}")
            print(f"✓ Using model: {self.model}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Ollama at {self.endpoint}: {e}")
    
    async def analyze_emotion(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze emotion using Ollama.
        
        Args:
            text: Text to analyze
            context: Optional previous context
        
        Returns:
            Analysis results dictionary
        """
        if not self._initialized:
            await self.initialize()
        
        # Build prompt using centralized prompt engine
        prompt = prompts.get_emotion_analysis_prompt(text, context)
        
        try:
            # Call Ollama
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': self.temperature,
                    'num_predict': 512,
                }
            )
            
            # Extract and parse response
            response_text = response.get('response', '').strip()
            
            # Try to extract JSON from markdown code blocks
            if '```json' in response_text:
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            elif '```' in response_text:
                json_match = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            
            # Try to fix common JSON issues
            response_text = fix_malformed_json(response_text)
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['emotional_state', 'confidence', 'social_cue']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Raw response: {response_text}")
            # Return safe default
            return {
                "emotional_state": "unknown",
                "confidence": 0.0,
                "social_cue": "appropriate",
                "speech_pace": "normal",
                "word_count": len(text.split()),
                "filler_words": [],
                "overly_critical": False,
                "coaching": "Unable to analyze at this time.",
                "error": str(e)
            }
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            raise
    
    async def dispose(self) -> None:
        """Cleanup resources."""
        self._initialized = False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information."""
        return {
            "name": "SelfHostedOllama",
            "version": "1.0.0",
            "model": self.model,
            "endpoint": self.endpoint,
            "temperature": self.temperature,
            "initialized": self._initialized
        }
