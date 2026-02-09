"""
Pydantic response models for LLM analysis responses.
Used with the instructor library for type-safe, validated LLM outputs.
"""

from typing import List, Literal

from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    """Validated response model for communication tone analysis."""

    emotional_state: Literal[
        "calm",
        "engaged",
        "elevated",
        "intense",
        "rapid",
        "distracted",
        "overwhelmed",
        "overly_critical",
        "unknown",
    ] = Field(default="unknown")

    social_cues: Literal[
        "appropriate",
        "interrupting",
        "dominating",
        "monotone",
        "too_quiet",
        "off_topic",
        "repetitive",
        "unknown",
    ] = Field(default="appropriate")

    speech_pattern: Literal[
        "normal",
        "rushed",
        "rambling",
        "clear",
        "hesitant",
        "loud",
        "quiet",
        "unknown",
    ] = Field(default="normal")

    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    key_indicators: List[str] = Field(default_factory=list)
    coaching_feedback: str = Field(default="No specific suggestions")

    model_config = {"extra": "ignore"}
