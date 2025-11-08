"""
Communication analysis using configurable model providers.
"""

import json
import re
from typing import Dict, Optional

import ollama
from src import config


class CommunicationAnalyzer:
    """Analyzes communication patterns using configurable model providers."""
    
    def __init__(self, model_provider: 'BaseModelProvider' = None):
        """
        Initialize the analyzer with a model provider.
        
        Args:
            model_provider: Optional pre-configured provider. If None, will create from config.
        """
        self.model_provider = model_provider
        self._initialized = False
        self.config = config.ModelConfig()
        self.min_words = self.config.get_analysis_config().get('min_words', 15)
    
    async def initialize(self):
        """Initialize with configured model provider."""
        if self.model_provider is None:
            # Create provider from configuration
            from .model_factory import ModelProviderFactory
            self.model_provider = await ModelProviderFactory.create_provider(self.config)
        
        self._initialized = True
        print(f"✓ Communication analyzer initialized")
        print(f"  Provider: {self.model_provider.get_provider_info()['name']}")
        print(f"  Min words: {self.min_words}")
    
    async def analyze_tone_async(self, text: str, context: dict = None) -> Dict[str, any]:
        """
        Analyze the tone and communication style of text asynchronously.
        
        Args:
            text: Text to analyze
            context: Optional previous analysis context
        
        Returns:
            Analysis results dictionary
        """
        if not self._initialized:
            await self.initialize()
        
        # Check minimum word requirement
        word_count = len(text.split())
        if word_count < self.min_words:
            return {
                "emotional_state": "insufficient_data",
                "confidence": 0.0,
                "social_cue": "appropriate",
                "speech_pace": "unknown",
                "word_count": word_count,
                "filler_words": [],
                "overly_critical": False,
                "coaching": f"Need at least {self.min_words} words for analysis (got {word_count})"
            }
        
        # Delegate to configured provider
        return await self.model_provider.analyze_emotion(text, context)
    
    def analyze_tone(self, text: str) -> Dict[str, any]:
        """
        Synchronous wrapper for analyze_tone_async.
        Maintained for backward compatibility.
        
        Args:
            text: Text to analyze
        
        Returns:
            Analysis results dictionary
        """
        if len(text.split()) < config.MIN_WORDS_FOR_ANALYSIS:
            return {
                "emotional_state": "unknown",
                "social_cues": "unknown",
                "speech_pattern": "unknown",
                "confidence": 0.0,
                "key_indicators": [],
                "coaching_feedback": "Not enough content to analyze",
                "error": "insufficient_text",
            }

        try:
            prompt = config.ANALYSIS_PROMPT.format(text=text)

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.3,  # Lower temperature for more consistent analysis
                },
            )

            # Parse JSON response
            response_text = response["response"].strip()

            # Debug: print the raw response to understand what we're getting
            if config.DEBUG_ANALYSIS:
                print(f"Raw LLM response: {response_text}")

            # Try to extract JSON if it's wrapped in markdown
            if "```json" in response_text:
                response_text = (
                    response_text.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            # Try to fix common JSON formatting issues
            response_text = fix_malformed_json(response_text)

            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError as e:
                # If still fails, try one more aggressive fix
                print(f"First parse attempt failed: {e}")
                print(f"Attempting to fix JSON...")

                # Try to fix trailing commas
                response_text = re.sub(r",(\s*[}\]])", r"\1", response_text)
                analysis = json.loads(response_text)

            # Ensure all required fields exist with sensible defaults
            analysis.setdefault("emotional_state", "unknown")
            analysis.setdefault("social_cues", "appropriate")
            analysis.setdefault("speech_pattern", "normal")
            analysis.setdefault("confidence", 0.5)
            analysis.setdefault("key_indicators", [])
            analysis.setdefault("coaching_feedback", "No specific suggestions")

            return analysis

        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response was: {response_text}")
            return {
                "emotional_state": "error",
                "social_cues": "error",
                "speech_pattern": "error",
                "confidence": 0.0,
                "key_indicators": [],
                "coaching_feedback": "Analysis error - could not parse response",
                "error": "parse_error",
            }
        except Exception as e:
            print(f"Error during analysis: {e}")
            return {
                "emotional_state": "error",
                "social_cues": "error",
                "speech_pattern": "error",
                "confidence": 0.0,
                "key_indicators": [],
                "coaching_feedback": "Analysis unavailable",
                "error": str(e),
            }

    def get_emotional_state_emoji(self, emotional_state: str) -> str:
        """Get emoji representation of emotional state."""
        emoji_map = {
            # Communication/Social Tones
            "supportive": "🤝",
            "dismissive": "🙄",
            "aggressive": "😤",
            "passive": "😶",
            "positive": "😊",
            "negative": "😕",
            "neutral": "😐",
            # Emotional Regulation States
            "elevated": "⬆️",
            "intense": "🔥",
            "rapid": "⚡",
            "calm": "🧘",
            "engaged": "✨",
            "distracted": "🤔",
            "overwhelmed": "😵‍💫",
            "overly_critical": "👎",
            # System States
            "unknown": "❓",
            "error": "❌",
        }
        return emoji_map.get(emotional_state.lower(), "💬")

    def get_social_cue_emoji(self, social_cue: str) -> str:
        """Get emoji for social cue indicators."""
        emoji_map = {
            "interrupting": "✋",
            "dominating": "🎤",
            "monotone": "📢",
            "too_quiet": "🤐",
            "appropriate": "👍",
            "off_topic": "🔄",
            "repetitive": "🔁",
            "unknown": "❓",
            "error": "❌",
        }
        return emoji_map.get(social_cue.lower(), "💬")

    def should_alert(
        self, emotional_state: str, confidence: float, threshold: float = 0.7
    ) -> bool:
        """
        Determine if emotional state should trigger an alert.
        Higher threshold for autism/ADHD coaching to reduce false positives.

        Args:
            emotional_state: detected emotional state
            confidence: confidence level (0-1)
            threshold: minimum confidence to alert (default 0.7 for more conservative alerting)

        Returns:
            True if alert should be shown
        """
        # Alert on emotional regulation concerns
        emotional_concerns = ["elevated", "intense", "rapid", "overwhelmed"]

        # Alert on potentially problematic communication patterns
        social_concerns = [
            "dismissive",
            "aggressive",
            "interrupting",
            "dominating",
            "off_topic",
            "repetitive",
            "overly_critical",
        ]

        concerning_states = emotional_concerns + social_concerns
        return emotional_state.lower() in concerning_states and confidence >= threshold

    def should_social_cue_alert(
        self, social_cue: str, confidence: float, threshold: float = 0.7
    ) -> bool:
        """
        Check specifically for social cue alerts.

        Args:
            social_cue: detected social cue pattern
            confidence: confidence level (0-1)
            threshold: minimum confidence to alert (default 0.7 for conservative alerting)

        Returns:
            True if social cue alert should be shown
        """
        concerning_social_cues = [
            "interrupting",
            "dominating",
            "too_quiet",
            "off_topic",
            "repetitive",
        ]
        return social_cue.lower() in concerning_social_cues and confidence >= threshold

    def generate_summary(self, analyses: list) -> Dict[str, any]:
        """
        Generate summary from multiple analysis results.

        Args:
            analyses: list of analysis results

        Returns:
            Summary dictionary with trends and insights
        """
        if not analyses:
            return {"error": "No analyses to summarize"}

        # Count emotional state occurrences
        state_counts = {}
        total_confidence = 0
        all_feedback = []

        for analysis in analyses:
            state = analysis.get("emotional_state", "unknown")
            state_counts[state] = state_counts.get(state, 0) + 1
            total_confidence += analysis.get("confidence", 0)

            feedback = analysis.get("coaching_feedback", "")
            if feedback and feedback not in all_feedback:
                all_feedback.append(feedback)

        # Find dominant emotional state
        dominant_state = max(state_counts, key=state_counts.get)
        avg_confidence = total_confidence / len(analyses)

        return {
            "dominant_emotional_state": dominant_state,
            "state_distribution": state_counts,
            "average_confidence": avg_confidence,
            "key_feedback": all_feedback[:3],  # Top 3 feedback items
            "total_analyses": len(analyses),
        }


if __name__ == "__main__":
    # Test the analyzer
    analyzer = CommunicationAnalyzer()

    # Test with sample texts
    test_texts = [
        "I really appreciate your input on this. That's a great point you've made.",
        "Whatever, I don't really care about that. Let's just move on.",
        "The quarterly results show a 15% increase in revenue, which is in line with our projections.",
    ]

    print("Testing Communication Analyzer\n")

    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: {text}")
        print("-" * 60)

        result = analyzer.analyze_tone(text)

        emoji = analyzer.get_emotional_state_emoji(result["emotional_state"])
        print(
            f"Emotional State: {emoji} {result['emotional_state']} (confidence: {result['confidence']:.2f})"
        )
        print(
            f"Social Cues: {analyzer.get_social_cue_emoji(result['social_cues'])} {result['social_cues']}"
        )
        print(f"Coaching: {result['coaching_feedback']}")

        if result.get("key_indicators"):
            print(f"Key indicators: {', '.join(result['key_indicators'])}")

        if analyzer.should_alert(result["emotional_state"], result["confidence"]):
            print("⚠️  Alert: Potentially concerning emotional state detected")

        if analyzer.should_social_cue_alert(
            result["social_cues"], result["confidence"]
        ):
            print("⚠️  Social Alert: Concerning social pattern detected")
