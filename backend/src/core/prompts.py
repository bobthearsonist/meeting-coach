"""
Centralized prompt engineering for Meeting Coach.
All prompts defined here for easy inspection and updates.
"""
from typing import Dict, Any
import json

VERSION = "1.0.0"

def get_emotion_analysis_prompt(text: str, context: Dict[str, Any] = None) -> str:
    """
    Build prompt for emotional state and communication analysis.
    
    Args:
        text: The transcript text to analyze
        context: Optional context (previous emotions, session data)
    
    Returns:
        Formatted prompt string
    """
    context_str = json.dumps(context) if context else "None"
    
    return f"""You are analyzing communication patterns for neurodivergent individuals to provide supportive coaching.

Text to analyze: "{text}"

Previous context: {context_str}

Analyze the emotional tone and communication style. Respond in JSON format:
{{
  "emotional_state": "calm|engaged|elevated|intense|overwhelmed",
  "confidence": 0.0-1.0,
  "social_cue": "appropriate|watch carefully|concerning",
  "speech_pace": "slow|normal|fast|very_fast",
  "word_count": <number>,
  "filler_words": ["um", "uh", "like"],
  "overly_critical": true|false,
  "coaching": "Brief, supportive feedback (1 sentence)"
}}

Important:
- Be supportive and non-judgmental
- Focus on actionable insights
- Respect neurodivergent communication styles
- Provide gentle guidance, not criticism
- Flag "overly_critical" as true if the person is being harsh or judgmental toward others"""


def get_system_prompt() -> str:
    """
    System prompt for models that support it (for future use with Anthropic/OpenAI).
    
    Returns:
        System prompt string
    """
    return """You are a supportive communication coach specializing in helping neurodivergent individuals.
You provide non-judgmental, actionable feedback about communication patterns.
Always be encouraging and focus on strengths while gently suggesting improvements."""


def get_all_prompts() -> Dict[str, Any]:
    """
    Return all prompts for API transparency.
    
    Returns:
        Dictionary containing all prompt information
    """
    return {
        "version": VERSION,
        "prompts": {
            "emotion_analysis": {
                "description": "Analyzes emotional state and communication patterns",
                "template": get_emotion_analysis_prompt("{{text}}", None),
                "variables": ["text", "context"],
                "output_schema": {
                    "emotional_state": "string (enum: calm|engaged|elevated|intense|overwhelmed)",
                    "confidence": "float (0.0-1.0)",
                    "social_cue": "string (enum: appropriate|watch carefully|concerning)",
                    "speech_pace": "string (enum: slow|normal|fast|very_fast)",
                    "word_count": "integer",
                    "filler_words": "array of strings",
                    "overly_critical": "boolean",
                    "coaching": "string"
                }
            },
            "system_prompt": {
                "description": "System-level instructions for the AI model",
                "template": get_system_prompt()
            }
        }
    }
