#!/usr/bin/env python3
"""
Test script specifically for emotionally flat content to validate improved accuracy
"""
from analyzer import CommunicationAnalyzer

def test_emotionally_flat_content():
    """Test analyzer with emotionally flat content that should NOT trigger alerts."""
    print("Testing analyzer with emotionally flat content...")
    
    analyzer = CommunicationAnalyzer()
    
    # Emotionally flat test cases that should be neutral
    flat_test_texts = [
        "The quarterly results show a 15% increase in revenue, which is in line with our projections.",
        "We need to review the budget for next quarter and allocate resources accordingly.",
        "The meeting is scheduled for 2 PM in conference room B.",
        "Please submit your reports by Friday so we can review them next week.",
        "The current process takes approximately 3 hours to complete.",
        "We have five team members working on this project.",
        "The deadline is set for March 15th, and we should plan accordingly.",
        "Let's discuss the implementation details during our next meeting.",
        "The client has requested some minor changes to the proposal.",
        "We will send the updated documentation by end of day."
    ]
    
    false_positives = 0
    total_tests = len(flat_test_texts)
    
    print(f"\nTesting {total_tests} emotionally flat statements:")
    print("=" * 70)
    
    for i, text in enumerate(flat_test_texts, 1):
        print(f"\nTest {i}: '{text}'")
        print("-" * 70)
        
        result = analyzer.analyze_tone(text)
        
        if 'error' in result:
            print(f"❌ Analysis failed: {result['error']}")
            continue
        
        emoji = analyzer.get_tone_emoji(result['tone'])
        print(f"Tone: {emoji} {result['tone']} (confidence: {result['confidence']:.2f})")
        print(f"Suggestions: {result['suggestions']}")
        
        if result.get('key_indicators'):
            print(f"Key indicators: {', '.join(result['key_indicators'])}")
        
        # Check if this should alert (it shouldn't for flat content)
        should_alert = analyzer.should_alert(result['tone'], result['confidence'])
        if should_alert:
            print("⚠️  ALERT: Potentially problematic tone detected")
            false_positives += 1
            print("❌ FALSE POSITIVE: This emotionally flat content should not trigger an alert")
        else:
            print("✅ CORRECT: No alert triggered for this emotionally flat content")
    
    print(f"\n{'='*70}")
    print(f"SUMMARY:")
    print(f"Total tests: {total_tests}")
    print(f"False positives: {false_positives}")
    print(f"Accuracy: {((total_tests - false_positives) / total_tests * 100):.1f}%")
    
    if false_positives == 0:
        print("🎉 EXCELLENT: No false positives detected!")
    elif false_positives <= 2:
        print("👍 GOOD: Very few false positives")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Too many false positives")
    
    return false_positives

def test_clearly_problematic_content():
    """Test that clearly problematic content still gets detected."""
    print("\n\nTesting clearly problematic content (should trigger alerts)...")
    
    analyzer = CommunicationAnalyzer()
    
    problematic_texts = [
        "Whatever, I don't care about that stupid idea.",
        "That's absolutely terrible and won't work at all.",
        "I guess maybe we could try it if you really want to.",
        "I really appreciate your thoughtful input on this project."  # This should NOT alert (positive)
    ]
    
    expected_alerts = [True, True, True, False]  # Last one is positive, shouldn't alert
    
    print(f"\nTesting {len(problematic_texts)} statements with known expected outcomes:")
    print("=" * 70)
    
    correct_predictions = 0
    
    for i, (text, expected_alert) in enumerate(zip(problematic_texts, expected_alerts), 1):
        print(f"\nTest {i}: '{text}'")
        print(f"Expected to alert: {expected_alert}")
        print("-" * 70)
        
        result = analyzer.analyze_tone(text)
        
        if 'error' in result:
            print(f"❌ Analysis failed: {result['error']}")
            continue
        
        emoji = analyzer.get_tone_emoji(result['tone'])
        print(f"Tone: {emoji} {result['tone']} (confidence: {result['confidence']:.2f})")
        
        actual_alert = analyzer.should_alert(result['tone'], result['confidence'])
        if actual_alert:
            print("⚠️  ALERT: Potentially problematic tone detected")
        else:
            print("✅ No alert triggered")
        
        if actual_alert == expected_alert:
            print("✅ CORRECT prediction")
            correct_predictions += 1
        else:
            print("❌ INCORRECT prediction")
    
    print(f"\n{'='*70}")
    print(f"Problematic content detection accuracy: {(correct_predictions / len(problematic_texts) * 100):.1f}%")
    
    return correct_predictions == len(problematic_texts)

if __name__ == "__main__":
    print("="*70)
    print("Testing Improved Emotion Analysis Accuracy")
    print("="*70)
    
    try:
        false_positives = test_emotionally_flat_content()
        problematic_accuracy = test_clearly_problematic_content()
        
        print(f"\n{'='*70}")
        print("FINAL RESULTS:")
        print(f"False positives on flat content: {false_positives}")
        print(f"Problematic content detection: {'✅ Accurate' if problematic_accuracy else '❌ Needs work'}")
        
        if false_positives <= 1 and problematic_accuracy:
            print("🎉 SUCCESS: Improved emotion analysis is working well!")
        else:
            print("⚠️  NEEDS MORE WORK: Analysis needs further refinement")
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()