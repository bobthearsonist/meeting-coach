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
                'tone': 'unknown',
                'confidence': 0.0,
                'key_indicators': [],
                'suggestions': 'Not enough content to analyze',
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
            
            # Try to extract JSON if it's wrapped in markdown
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(response_text)
            
            # Ensure all required fields exist (supporting both old and new format)
            analysis.setdefault('tone', analysis.get('emotional_state', 'neutral'))
            analysis.setdefault('emotional_state', analysis.get('tone', 'neutral'))
            analysis.setdefault('social_cues', 'unknown')
            analysis.setdefault('speech_pattern', 'normal')
            analysis.setdefault('confidence', 0.5)
            analysis.setdefault('key_indicators', [])
            analysis.setdefault('suggestions', analysis.get('coaching_feedback', 'No specific suggestions'))
            analysis.setdefault('coaching_feedback', analysis.get('suggestions', 'No coaching available'))

            return analysis
            
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response was: {response_text}")
            return {
                'tone': 'neutral',
                'confidence': 0.0,
                'key_indicators': [],
                'suggestions': 'Analysis error',
                'error': 'parse_error'
            }
        except Exception as e:
            print(f"Error during analysis: {e}")
            return {
                'tone': 'neutral',
                'confidence': 0.0,
                'key_indicators': [],
                'suggestions': 'Analysis unavailable',
                'error': str(e)
            }
    
    def get_tone_emoji(self, tone: str) -> str:
        """Get emoji representation of emotional state/tone."""
        emoji_map = {
            # Original tone mappings
            'supportive': '🤝',
            'dismissive': '🙄',
            'neutral': '😐',
            'aggressive': '😤',
            'passive': '😶',
            'positive': '😊',
            'negative': '😕',
            # New emotional state mappings
            'elevated': '⬆️',
            'intense': '🔥',
            'rapid': '⚡',
            'calm': '🧘',
            'engaged': '✨',
            'distracted': '🤔',
            'overwhelmed': '😵‍💫',
            'unknown': '❓'
        }
        return emoji_map.get(tone.lower(), '💬')

    def get_social_cue_emoji(self, social_cue: str) -> str:
        """Get emoji for social cue indicators."""
        emoji_map = {
            'interrupting': '✋',
            'dominating': '🎤',
            'monotone': '📢',
            'too_quiet': '🤐',
            'appropriate': '👍',
            'off_topic': '🔄',
            'repetitive': '🔁'
        }
        return emoji_map.get(social_cue.lower(), '💬')
    
    def should_alert(self, tone: str, confidence: float, threshold: float = 0.6) -> bool:
        """
        Determine if emotional state or social cue should trigger an alert.
        Lower threshold for autism/ADHD coaching to catch subtle patterns.

        Args:
            tone: detected emotional state or tone
            confidence: confidence level (0-1)
            threshold: minimum confidence to alert (default 0.6 for more sensitivity)

        Returns:
            True if alert should be shown
        """
        # Alert on elevated states that might indicate emotional dysregulation
        elevated_states = ['elevated', 'intense', 'rapid', 'overwhelmed']

        # Alert on problematic social patterns
        social_concerns = ['dismissive', 'aggressive', 'interrupting', 'dominating', 'off_topic', 'repetitive']

        concerning_patterns = elevated_states + social_concerns
        return tone.lower() in concerning_patterns and confidence >= threshold

    def should_social_cue_alert(self, social_cue: str, confidence: float, threshold: float = 0.6) -> bool:
        """
        Check specifically for social cue alerts.

        Args:
            social_cue: detected social cue pattern
            confidence: confidence level (0-1)
            threshold: minimum confidence to alert

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
        
        # Count tone occurrences
        tone_counts = {}
        total_confidence = 0
        all_suggestions = []
        
        for analysis in analyses:
            tone = analysis.get('tone', 'unknown')
            tone_counts[tone] = tone_counts.get(tone, 0) + 1
            total_confidence += analysis.get('confidence', 0)
            
            suggestion = analysis.get('suggestions', '')
            if suggestion and suggestion not in all_suggestions:
                all_suggestions.append(suggestion)
        
        # Find dominant tone
        dominant_tone = max(tone_counts, key=tone_counts.get)
        avg_confidence = total_confidence / len(analyses)
        
        return {
            'dominant_tone': dominant_tone,
            'tone_distribution': tone_counts,
            'average_confidence': avg_confidence,
            'key_suggestions': all_suggestions[:3],  # Top 3 suggestions
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
        
        emoji = analyzer.get_tone_emoji(result['tone'])
        print(f"Tone: {emoji} {result['tone']} (confidence: {result['confidence']:.2f})")
        print(f"Suggestions: {result['suggestions']}")
        
        if result.get('key_indicators'):
            print(f"Key indicators: {', '.join(result['key_indicators'])}")
        
        if analyzer.should_alert(result['tone'], result['confidence']):
            print("⚠️  Alert: Potentially problematic tone detected")
