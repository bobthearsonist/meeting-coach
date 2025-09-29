"""
Test cases specifically for overly critical speech detection
"""
import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from analyzer import CommunicationAnalyzer


class TestOverlyCriticalDetection:
    """Test cases for detecting overly critical speech patterns"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing."""
        return CommunicationAnalyzer()
    
    @pytest.fixture
    def overly_critical_examples(self):
        """Examples of overly critical speech patterns."""
        return [
            {
                'text': "That's a terrible idea and won't work at all. You clearly haven't thought this through properly and should reconsider this approach.",
                'expected_tone': 'overly_critical',
                'description': 'Direct harsh criticism'
            },
            {
                'text': "This code is absolute garbage and completely unworkable. Whoever wrote this obviously doesn't know what they're doing and should not be programming.",
                'expected_tone': 'overly_critical', 
                'description': 'Personal attack on competence'
            },
            {
                'text': "I can't believe you would suggest something so incredibly stupid and wrong. That's completely incorrect and shows poor judgment on your part.",
                'expected_tone': 'overly_critical',
                'description': 'Insulting language'
            },
            {
                'text': "No, that's not right at all. You never understand these technical things properly and always make these kinds of basic mistakes.",
                'expected_tone': 'overly_critical',
                'description': 'Dismissive with personal judgment'
            },
            {
                'text': "That approach is fundamentally flawed and will cause serious problems down the line. This shows a complete lack of understanding of basic principles.",
                'expected_tone': 'overly_critical',
                'description': 'Overly harsh technical criticism'
            }
        ]
    
    @pytest.fixture 
    def constructive_criticism_examples(self):
        """Examples that should NOT be flagged as overly critical."""
        return [
            {
                'text': "I have some concerns about this approach and would like to discuss potential alternative solutions. Could we consider other options together?",
                'expected_tone': 'calm',
                'description': 'Constructive feedback'
            },
            {
                'text': "I think there might be some issues with this implementation that we should address. Let me explain my reasoning and we can work together.",
                'expected_tone': 'engaged',
                'description': 'Thoughtful critique'
            },
            {
                'text': "I respectfully disagree with this approach, but I understand your perspective completely. Would you be open to considering an alternative solution?",
                'expected_tone': 'calm',
                'description': 'Respectful disagreement'
            },
            {
                'text': "This won't work as expected due to the following technical limitations that we need to consider. Let's explore some different approaches.",
                'expected_tone': 'calm',
                'description': 'Technical objection'
            }
        ]
    
    @pytest.mark.unit
    def test_overly_critical_emoji_mapping(self, analyzer):
        """Test that overly critical has the correct emoji."""
        emoji = analyzer.get_tone_emoji('overly_critical')
        assert emoji == '👎', f"Expected 👎 for overly_critical, got {emoji}"
    
    @pytest.mark.unit
    def test_overly_critical_triggers_alert(self, analyzer):
        """Test that overly critical behavior triggers alerts with sufficient confidence."""
        # Should trigger alerts with high confidence
        assert analyzer.should_alert('overly_critical', 0.8) == True
        assert analyzer.should_alert('overly_critical', 0.9) == True
        assert analyzer.should_alert('overly_critical', 1.0) == True
        
        # Should not trigger with low confidence
        assert analyzer.should_alert('overly_critical', 0.6) == False
        assert analyzer.should_alert('overly_critical', 0.5) == False
        
        # Boundary test - exactly at threshold
        assert analyzer.should_alert('overly_critical', 0.7) == True
    
    @pytest.mark.unit
    @pytest.mark.requires_ollama
    @patch('analyzer.ollama.generate')
    def test_analyze_overly_critical_patterns(self, mock_generate, analyzer, overly_critical_examples):
        """Test that overly critical patterns are detected correctly."""
        
        for example in overly_critical_examples:
            # Mock Ollama to return overly critical analysis
            mock_response = {
                'response': json.dumps({
                    "emotional_state": "overly_critical",
                    "social_cues": "inappropriate", 
                    "speech_pattern": "harsh",
                    "confidence": 0.85,
                    "key_indicators": ["harsh language", "personal attack", "dismissive"],
                    "coaching_feedback": "Consider using more constructive language when providing feedback"
                })
            }
            mock_generate.return_value = mock_response
            
            result = analyzer.analyze_tone(example['text'])
            
            # Check that the result identifies overly critical behavior
            assert result['emotional_state'] == 'overly_critical' or result['tone'] == 'overly_critical', \
                f"Failed to detect overly critical pattern in: {example['description']}"
            
            # Should trigger an alert
            assert analyzer.should_alert(result.get('emotional_state', result.get('tone')), result['confidence']), \
                f"Should trigger alert for: {example['description']}"
    
    @pytest.mark.unit
    @pytest.mark.requires_ollama
    @patch('analyzer.ollama.generate') 
    def test_constructive_criticism_not_flagged(self, mock_generate, analyzer, constructive_criticism_examples):
        """Test that constructive criticism is not flagged as overly critical."""
        
        for example in constructive_criticism_examples:
            # Mock Ollama to return calm/engaged analysis
            mock_response = {
                'response': json.dumps({
                    "emotional_state": example['expected_tone'],
                    "social_cues": "appropriate",
                    "speech_pattern": "clear", 
                    "confidence": 0.8,
                    "key_indicators": ["respectful", "constructive"],
                    "coaching_feedback": "Continue as you are"
                })
            }
            mock_generate.return_value = mock_response
            
            result = analyzer.analyze_tone(example['text'])
            
            # Should not be flagged as overly critical
            emotional_state = result.get('emotional_state', result.get('tone'))
            assert emotional_state != 'overly_critical', \
                f"Incorrectly flagged constructive criticism as overly critical: {example['description']}"
            
            # Should not trigger an alert  
            assert not analyzer.should_alert(emotional_state, result['confidence']), \
                f"Should not trigger alert for constructive criticism: {example['description']}"
    
    @pytest.mark.unit
    def test_overly_critical_in_concerning_patterns(self, analyzer):
        """Test that overly_critical is included in concerning patterns list."""
        # This tests the internal logic by checking that it triggers alerts
        # which confirms it's in the concerning_patterns list
        result = analyzer.should_alert('overly_critical', 0.8)
        assert result == True, "overly_critical should be in concerning patterns and trigger alerts"