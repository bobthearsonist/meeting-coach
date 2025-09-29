"""
Mock ollama module for testing without actual ollama installation
"""
import json

def list():
    """Mock list function"""
    return ["llama3:8b"]

def generate(model, prompt, options=None):
    """Mock generate function that simulates overly sensitive emotion detection"""
    # Parse the text from the prompt
    text_start = prompt.find('"') + 1
    text_end = prompt.find('"', text_start)
    text = prompt[text_start:text_end]
    
    # Simulate the current problem: overly sensitive detection
    # Let's analyze some patterns that might be causing false positives
    
    if any(word in text.lower() for word in ['no', 'not', 'stop', 'can\'t', 'won\'t', 'don\'t']):
        # Current system might be too sensitive to negatives
        response = {
            'tone': 'dismissive',
            'confidence': 0.85,
            'key_indicators': ['negative language'],
            'suggestions': 'Consider using more positive language'
        }
    elif any(word in text.lower() for word in ['need', 'should', 'must', 'have to']):
        # Too sensitive to directive language
        response = {
            'tone': 'aggressive', 
            'confidence': 0.75,
            'key_indicators': ['directive language'],
            'suggestions': 'Try using softer language'
        }
    elif len(text.split()) < 15:
        # Short texts being flagged
        response = {
            'tone': 'passive',
            'confidence': 0.70,
            'key_indicators': ['brief response'],
            'suggestions': 'Provide more detailed feedback'
        }
    else:
        # Even neutral content getting flagged
        response = {
            'tone': 'neutral',
            'confidence': 0.45,  # Lower confidence for neutral
            'key_indicators': [],
            'suggestions': 'Communication seems clear'
        }
    
    return {
        'response': json.dumps(response)
    }