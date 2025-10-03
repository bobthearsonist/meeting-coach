"""
Communication analysis using local LLM (Ollama)
"""
import ollama
import json
from typing import Dict, Optional
import config


class CommunicationAnalyzer:
    def __init__(self, model: str = None):
        """
        Initialize the analyzer with Ollama LLM.

        Args:
            model: Ollama model name (default from config)
        """
        self.model = model or config.OLLAMA_MODEL

        # Test Ollama connection
        try:
            ollama.list()
            print(f"Connected to Ollama. Using model: {self.model}")
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {e}")
            print("Make sure Ollama is running: brew install ollama && ollama serve")

    def analyze_tone(self, text: str) -> Dict[str, any]:
        """
        Analyze the tone and communication style of text.

        Args:
            text: transcribed text to analyze

        Returns:
            Dictionary containing tone analysis and suggestions
        """
        if len(text.split()) < config.MIN_WORDS_FOR_ANALYSIS:
            return {
                'emotional_state': 'unknown',
                'social_cues': 'unknown',
                'speech_pattern': 'unknown',
                'confidence': 0.0,
                'key_indicators': [],
                'coaching_feedback': 'Not enough content to analyze',
                'error': 'insufficient_text'
            }

        try:
            prompt = config.ANALYSIS_PROMPT.format(text=text)

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.3,  # Lower temperature for more consistent analysis
                }
            )

            # Parse JSON response
            response_text = response['response'].strip()

            # Debug: print the raw response to understand what we're getting
            if config.DEBUG_ANALYSIS:
                print(f"Raw LLM response: {response_text}")

            # Try to extract JSON if it's wrapped in markdown
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()

            analysis = json.loads(response_text)

            # Ensure all required fields exist with sensible defaults
            analysis.setdefault('emotional_state', 'unknown')
            analysis.setdefault('social_cues', 'appropriate')
            analysis.setdefault('speech_pattern', 'normal')
            analysis.setdefault('confidence', 0.5)
            analysis.setdefault('key_indicators', [])
            analysis.setdefault('coaching_feedback', 'No specific suggestions')

            return analysis

        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response was: {response_text}")
            return {
                'emotional_state': 'error',
                'social_cues': 'error',
                'speech_pattern': 'error',
                'confidence': 0.0,
                'key_indicators': [],
                'coaching_feedback': 'Analysis error - could not parse response',
                'error': 'parse_error'
            }
        except Exception as e:
            print(f"Error during analysis: {e}")
            return {
                'emotional_state': 'error',
                'social_cues': 'error',
                'speech_pattern': 'error',
                'confidence': 0.0,
                'key_indicators': [],
                'coaching_feedback': 'Analysis unavailable',
                'error': str(e)
            }

    def get_emotional_state_emoji(self, emotional_state: str) -> str:
        """Get emoji representation of emotional state."""
        emoji_map = {
            # Communication/Social Tones
            'supportive': '🤝',
            'dismissive': '🙄',
            'aggressive': '😤',
            'passive': '😶',
            'positive': '😊',
            'negative': '😕',
            'neutral': '😐',
            # Emotional Regulation States
            'elevated': '⬆️',
            'intense': '🔥',
            'rapid': '⚡',
            'calm': '🧘',
            'engaged': '✨',
            'distracted': '🤔',
            'overwhelmed': '😵‍💫',
            'overly_critical': '👎',
            # System States
            'unknown': '❓',
            'error': '❌'
        }
        return emoji_map.get(emotional_state.lower(), '💬')

    def get_social_cue_emoji(self, social_cue: str) -> str:
        """Get emoji for social cue indicators."""
        emoji_map = {
            'interrupting': '✋',
            'dominating': '🎤',
            'monotone': '📢',
            'too_quiet': '🤐',
            'appropriate': '👍',
            'off_topic': '🔄',
            'repetitive': '🔁',
            'unknown': '❓',
            'error': '❌'
        }
        return emoji_map.get(social_cue.lower(), '💬')

    def should_alert(self, emotional_state: str, confidence: float, threshold: float = 0.7) -> bool:
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
        emotional_concerns = ['elevated', 'intense', 'rapid', 'overwhelmed']

        # Alert on potentially problematic communication patterns
        social_concerns = ['dismissive', 'aggressive', 'interrupting', 'dominating', 'off_topic', 'repetitive', 'overly_critical']

        concerning_states = emotional_concerns + social_concerns
        return emotional_state.lower() in concerning_states and confidence >= threshold

    def should_social_cue_alert(self, social_cue: str, confidence: float, threshold: float = 0.7) -> bool:
        """
        Check specifically for social cue alerts.

        Args:
            social_cue: detected social cue pattern
            confidence: confidence level (0-1)
            threshold: minimum confidence to alert (default 0.7 for conservative alerting)

        Returns:
            True if social cue alert should be shown
        """
        concerning_social_cues = ['interrupting', 'dominating', 'too_quiet', 'off_topic', 'repetitive']
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
            return {'error': 'No analyses to summarize'}

        # Count emotional state occurrences
        state_counts = {}
        total_confidence = 0
        all_feedback = []

        for analysis in analyses:
            state = analysis.get('emotional_state', 'unknown')
            state_counts[state] = state_counts.get(state, 0) + 1
            total_confidence += analysis.get('confidence', 0)

            feedback = analysis.get('coaching_feedback', '')
            if feedback and feedback not in all_feedback:
                all_feedback.append(feedback)

        # Find dominant emotional state
        dominant_state = max(state_counts, key=state_counts.get)
        avg_confidence = total_confidence / len(analyses)

        return {
            'dominant_emotional_state': dominant_state,
            'state_distribution': state_counts,
            'average_confidence': avg_confidence,
            'key_feedback': all_feedback[:3],  # Top 3 feedback items
            'total_analyses': len(analyses)
        }


if __name__ == "__main__":
    # Test the analyzer
    analyzer = CommunicationAnalyzer()

    # Test with sample texts
    test_texts = [
        "I really appreciate your input on this. That's a great point you've made.",
        "Whatever, I don't really care about that. Let's just move on.",
        "The quarterly results show a 15% increase in revenue, which is in line with our projections."
    ]

    print("Testing Communication Analyzer\n")

    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: {text}")
        print("-" * 60)

        result = analyzer.analyze_tone(text)

        emoji = analyzer.get_emotional_state_emoji(result['emotional_state'])
        print(f"Emotional State: {emoji} {result['emotional_state']} (confidence: {result['confidence']:.2f})")
        print(f"Social Cues: {analyzer.get_social_cue_emoji(result['social_cues'])} {result['social_cues']}")
        print(f"Coaching: {result['coaching_feedback']}")

        if result.get('key_indicators'):
            print(f"Key indicators: {', '.join(result['key_indicators'])}")

        if analyzer.should_alert(result['emotional_state'], result['confidence']):
            print("⚠️  Alert: Potentially concerning emotional state detected")

        if analyzer.should_social_cue_alert(result['social_cues'], result['confidence']):
            print("⚠️  Social Alert: Concerning social pattern detected")
