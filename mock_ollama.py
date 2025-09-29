"""
Mock ollama module for testing without actual ollama installation
"""
import json

def list():
    """Mock list function"""
    return ["llama3:8b"]

def generate(model, prompt, options=None):
    """Mock generate function that simulates improved, more conservative emotion detection"""
    # Parse the text from the prompt
    text_start = prompt.find('"') + 1
    text_end = prompt.find('"', text_start)
    text = prompt[text_start:text_end]
    
    # Improved logic: be more conservative and accurate
    text_lower = text.lower()
    
    # Clear positive indicators
    positive_indicators = ['appreciate', 'great', 'excellent', 'thank you', 'good job', 'well done', 'love', 'fantastic']
    if any(indicator in text_lower for indicator in positive_indicators):
        response = {
            'tone': 'supportive',
            'confidence': 0.80,
            'key_indicators': [indicator for indicator in positive_indicators if indicator in text_lower],
            'suggestions': 'Great positive communication style'
        }
    
    # Clear dismissive indicators - must be explicit
    elif any(phrase in text_lower for phrase in ['whatever', "don't care", "doesn't matter", "forget it", "ignore"]):
        response = {
            'tone': 'dismissive',
            'confidence': 0.85,
            'key_indicators': ['dismissive language'],
            'suggestions': 'Consider being more open and engaged'
        }
    
    # Clear aggressive indicators - hostile language
    elif any(phrase in text_lower for phrase in ['terrible', 'stupid', 'ridiculous', 'idiot', 'shut up']):
        response = {
            'tone': 'aggressive',
            'confidence': 0.80,
            'key_indicators': ['hostile language'],
            'suggestions': 'Try using more constructive language'
        }
    
    # Clear passive indicators - avoiding engagement
    elif any(phrase in text_lower for phrase in ['i guess', 'maybe', 'i suppose', 'if you say so']):
        response = {
            'tone': 'passive',
            'confidence': 0.70,
            'key_indicators': ['tentative language'],
            'suggestions': 'Consider being more direct and confident'
        }
    
    # Default to neutral for everything else (factual, data, brief responses)
    else:
        response = {
            'tone': 'neutral',
            'confidence': 0.50,  # Conservative confidence for neutral
            'key_indicators': [],
            'suggestions': 'No specific feedback needed'
        }
    
    return {
        'response': json.dumps(response)
    }