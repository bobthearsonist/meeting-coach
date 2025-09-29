#!/usr/bin/env python3
"""
Test script for communication analyzer functionality
"""
from analyzer import CommunicationAnalyzer

def test_analyzer_without_ollama():
    """Test analyzer methods that don't require Ollama."""
    print("Testing analyzer utility methods...")

    analyzer = CommunicationAnalyzer()

    # Test emoji mapping
    test_tones = ['supportive', 'dismissive', 'neutral', 'aggressive', 'passive', 'unknown']
    print("\nTone emoji mapping:")
    for tone in test_tones:
        emoji = analyzer.get_tone_emoji(tone)
        print(f"  {tone}: {emoji}")

    # Test alert logic
    print("\nAlert logic tests:")
    test_cases = [
        ('supportive', 0.8, False),
        ('dismissive', 0.8, True),
        ('aggressive', 0.9, True),
        ('dismissive', 0.5, False),  # Low confidence
        ('neutral', 0.9, False),
    ]

    for tone, confidence, expected in test_cases:
        result = analyzer.should_alert(tone, confidence)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {tone} ({confidence:.1f}) -> Alert: {result} (expected: {expected})")

def test_analyzer_with_ollama():
    """Test analyzer with Ollama if available."""
    print("\nTesting analyzer with Ollama...")

    analyzer = CommunicationAnalyzer()

    test_texts = [
        "I really appreciate your input on this project. That's a great point you've made.",
        "Whatever, I don't really care about that. Let's just move on.",
        "The quarterly results show a 15% increase in revenue, which is in line with our projections.",
        "That's a terrible idea and won't work at all."
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: '{text}'")
        print("-" * 60)

        try:
            result = analyzer.analyze_tone(text)

            if 'error' in result:
                print(f"❌ Analysis failed: {result['error']}")
                continue

            emoji = analyzer.get_tone_emoji(result['tone'])
            print(f"Tone: {emoji} {result['tone']} (confidence: {result['confidence']:.2f})")
            print(f"Suggestions: {result['suggestions']}")

            if result.get('key_indicators'):
                print(f"Key indicators: {', '.join(result['key_indicators'])}")

            if analyzer.should_alert(result['tone'], result['confidence']):
                print("⚠️  Alert: Potentially problematic tone detected")

        except Exception as e:
            print(f"❌ Analysis failed with exception: {e}")

if __name__ == "__main__":
    print("="*60)
    print("Testing Communication Analyzer")
    print("="*60)

    try:
        test_analyzer_without_ollama()
        test_analyzer_with_ollama()
        print("\n✅ Analyzer tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()