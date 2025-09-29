#!/usr/bin/env python3
"""
Test the enhanced visual interface with colors and timeline
"""
import time
from main import MeetingCoach
from analyzer import CommunicationAnalyzer
from timeline import EmotionalTimeline
from colors import Colors, colorize_emotional_state, colorize_social_cue

def test_visual_components():
    """Test individual visual components"""
    print("🧪 TESTING VISUAL INTERFACE COMPONENTS")
    print("="*50)

    # Test colors
    print("\n🎨 Color Test:")
    if Colors.is_supported():
        print("Colors are supported in your terminal!")
    else:
        print("Colors are not supported, but interface will still work")

    states = ['calm', 'engaged', 'elevated', 'intense', 'overwhelmed']
    for state in states:
        colored = colorize_emotional_state(state)
        print(f"  {state:12} -> {colored}")

    # Test timeline
    print("\n📊 Timeline Test:")
    timeline = EmotionalTimeline(window_minutes=5)

    # Add some test entries
    test_scenarios = [
        ('calm', 'appropriate', 0.8, False),
        ('engaged', 'appropriate', 0.7, False),
        ('elevated', 'interrupting', 0.8, True),
        ('intense', 'dominating', 0.9, True),
        ('overwhelmed', 'off_topic', 0.7, True),
        ('calm', 'appropriate', 0.6, False),
    ]

    for i, (state, cue, conf, alert) in enumerate(test_scenarios):
        timeline.add_entry(state, cue, conf, f"Test scenario {i+1}", alert)
        time.sleep(0.1)  # Small delay

    timeline.display_timeline(minutes=5, width=60)

    print("\n✅ Visual interface components working!")

def test_analyzer_output():
    """Test the analyzer with visual output"""
    print("\n🧠 TESTING ANALYZER WITH VISUAL OUTPUT")
    print("="*50)

    analyzer = CommunicationAnalyzer()

    test_texts = [
        "I'm really excited about this project, we could do so many things!",
        "Um, like, I think we should, like, maybe consider the alternatives",
        "I don't really have anything to add to this discussion"
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}: \"{text[:50]}...\"")
        print("-" * 30)

        result = analyzer.analyze_tone(text)
        emotional_state = result.get('emotional_state', 'unknown')
        social_cues = result.get('social_cues', 'unknown')
        confidence = result.get('confidence', 0.0)

        # Test colorized output
        state_colored = colorize_emotional_state(emotional_state)
        cue_colored = colorize_social_cue(social_cues)

        print(f"Emotional State: {state_colored}")
        print(f"Social Cues: {cue_colored}")
        print(f"Confidence: {confidence:.1f}")

        if result.get('coaching_feedback'):
            coaching = Colors.colorize(result['coaching_feedback'], Colors.BOLD + Colors.BRIGHT_YELLOW)
            print(f"Coaching: {coaching}")

def test_mock_session():
    """Test a mock coaching session"""
    print("\n🎭 MOCK COACHING SESSION")
    print("="*50)

    timeline = EmotionalTimeline(window_minutes=10)

    # Simulate a meeting progression
    session_data = [
        ("Hi everyone, good morning!", "calm", "appropriate", 0.8, False),
        ("Oh wait, I just had this amazing idea about the project!", "elevated", "interrupting", 0.8, True),
        ("So we could implement this feature and that feature and maybe also...", "intense", "dominating", 0.9, True),
        ("Um, sorry, I got a bit carried away there", "overwhelmed", "repetitive", 0.7, True),
        ("Let me take a breath and focus on the main point", "calm", "appropriate", 0.8, False),
        ("I think the key issue is the user experience", "engaged", "appropriate", 0.8, False),
    ]

    for i, (text, state, cue, conf, alert) in enumerate(session_data):
        print(f"\n--- Analysis {i+1} ---")
        print(f"Text: \"{text}\"")

        # Add to timeline
        timeline.add_entry(state, cue, conf, text, alert)

        # Show colorized feedback
        state_colored = colorize_emotional_state(state)
        cue_colored = colorize_social_cue(cue)

        if alert:
            print(Colors.colorize("🚨 COACHING ALERT:", Colors.BRIGHT_RED))
            print(f"   Emotional State: {state_colored} ({conf:.1f})")
            print(f"   Social Cue: {cue_colored}")
        else:
            print(f"Status: {state_colored} | {cue_colored} | Confidence: {conf:.1f}")

        time.sleep(0.2)

    # Show final timeline
    print("\n" + "="*60)
    timeline.display_timeline(minutes=10, width=60)

    # Show session summary
    summary = timeline.get_session_summary()
    print(f"\n📊 Session Summary:")
    print(f"  Total analyses: {summary['total_entries']}")
    print(f"  Alerts: {summary['alert_count']}")
    print(f"  Dominant state: {colorize_emotional_state(summary['dominant_state'])}")

if __name__ == "__main__":
    test_visual_components()
    test_analyzer_output()
    test_mock_session()

    print("\n" + "="*60)
    print("✅ VISUAL INTERFACE TEST COMPLETE")
    print("Enhanced interface is ready for autism/ADHD coaching!")
    print("="*60)