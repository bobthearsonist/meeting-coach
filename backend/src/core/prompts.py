"""
Centralized prompt engineering for Meeting Coach.
All prompts defined here for easy inspection and updates.
"""

import json
from typing import Any, Dict, Optional

VERSION = "1.0.0"


def get_emotion_analysis_prompt(text: str, context: Dict[str, Any] = None) -> str:
    """
    Generate prompt for emotion and communication analysis.

    Args:
        text: Text to analyze
        context: Optional previous context/history

    Returns:
        Formatted prompt string
    """
    base_prompt = """Analyze this meeting transcript for social cues and emotional regulation patterns.
Focus on objective assessment to help someone with autism and ADHD understand their communication.

Text: "{text}"

Provide a VALID JSON response with properly formatted arrays (use commas between array elements):
1. emotional_state: "calm", "engaged", "elevated", "intense", "rapid", "distracted", "overwhelmed", or "overly_critical"
2. social_cue: "appropriate", "interrupting", "dominating", "monotone", "too_quiet", "off_topic", or "repetitive"
3. speech_pace: "normal", "rushed", "rambling", "clear", "hesitant", "loud", or "quiet"
4. confidence: 0.0-1.0 (how certain you are of the assessment)
5. word_count: integer (number of words in the text)
6. filler_words: array of filler words found (use commas between items: ["um", "uh", "like"])
7. overly_critical: true or false (whether language is harsh or judgmental)
8. coaching: practical, supportive suggestion if needed (one sentence, or "Continue as you are" if appropriate)

Assessment guidelines:
- Default to "calm" and "appropriate" for normal conversational speech
- Only flag "intense" or "elevated" if there are clear indicators like excitement, urgency, or emotional language
- Flag "overly_critical" for harsh, judgmental, or excessively negative language toward others or ideas
- Consider context - sharing accomplishments or explaining technical topics is often normal enthusiasm
- "engaged" is positive - someone actively participating in discussion
- Focus on patterns, not single words or phrases

Be conservative in flagging issues - most conversation should be assessed as appropriate."""

    # Format with text
    prompt = base_prompt.format(text=text)

    # Add context if provided
    if context:
        prev_state = context.get("emotional_state", "unknown")
        prev_cue = context.get("social_cue", "unknown")
        prompt += (
            f"\n\nPrevious context: emotional_state={prev_state}, social_cue={prev_cue}"
        )

    return prompt


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
                    "emotional_state": "string (enum: calm|engaged|elevated|intense|rapid|distracted|overwhelmed|overly_critical)",
                    "confidence": "float (0.0-1.0)",
                    "social_cue": "string (enum: appropriate|interrupting|dominating|monotone|too_quiet|off_topic|repetitive)",
                    "speech_pace": "string (enum: normal|rushed|rambling|clear|hesitant|loud|quiet)",
                    "word_count": "integer",
                    "filler_words": "array of strings",
                    "overly_critical": "boolean",
                    "coaching": "string",
                },
            },
            "system_prompt": {
                "description": "System-level instructions for the AI model",
                "template": get_system_prompt(),
            },
        },
    }
