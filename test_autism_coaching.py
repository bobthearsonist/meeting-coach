#!/usr/bin/env python3
"""
Test autism/ADHD coaching scenarios
"""
from analyzer import CommunicationAnalyzer

def test_autism_adhd_scenarios():
    analyzer = CommunicationAnalyzer()

    # Test scenarios specifically relevant to autism/ADHD challenges
    test_scenarios = [
        # Elevated/excited state (common with ADHD)
        "Oh my god, that's exactly what I was thinking! This is so cool, we could totally do this and that and maybe also this other thing I just thought of!",

        # Interrupting pattern
        "Yeah but wait, before you finish, I just had this idea that's really important and I don't want to forget it",

        # Dominating conversation (autism special interests)
        "Actually, that reminds me of this really interesting thing about neural networks that I've been researching. So there are these different architectures and the transformer model is particularly fascinating because...",

        # Overwhelmed/shutdown
        "I... I don't know. There's too much going on. Can we just... I need a minute.",

        # Repetitive/stimming speech
        "So like, the thing is, like, we need to, like, figure out the best way to, like, implement this properly.",

        # Too quiet/masking
        "I guess that's fine. Whatever works for everyone else.",

        # Rapid/pressured speech
        "We need to fix this immediately because if we don't then the whole system will break and then we'll have to start over and that would be terrible and waste so much time"
    ]

    scenario_names = [
        "Elevated/Excited State",
        "Interrupting Pattern",
        "Special Interest Dominating",
        "Overwhelmed/Shutdown",
        "Repetitive Speech",
        "Too Quiet/Masking",
        "Rapid/Pressured Speech"
    ]

    print("🧠 AUTISM/ADHD COACHING SCENARIOS TEST")
    print("=" * 50)

    for i, (scenario, name) in enumerate(zip(test_scenarios, scenario_names), 1):
        print(f"\n{i}. {name}")
        print("-" * 30)
        print(f"Text: \"{scenario[:60]}...\"")

        result = analyzer.analyze_tone(scenario)

        emotional_state = result.get('emotional_state', 'unknown')
        social_cues = result.get('social_cues', 'unknown')
        speech_pattern = result.get('speech_pattern', 'unknown')
        confidence = result.get('confidence', 0.0)
        coaching = result.get('coaching_feedback', 'No coaching')
        indicators = result.get('key_indicators', [])

        emotion_emoji = analyzer.get_tone_emoji(emotional_state)
        social_emoji = analyzer.get_social_cue_emoji(social_cues)

        print(f"Emotional State: {emotion_emoji} {emotional_state} ({confidence:.1f})")
        print(f"Social Cues: {social_emoji} {social_cues}")
        print(f"Speech Pattern: {speech_pattern}")
        print(f"Coaching: {coaching}")

        if indicators:
            print(f"Key Indicators: {', '.join(indicators[:3])}")

        # Check if alerts would trigger
        emotional_alert = analyzer.should_alert(emotional_state, confidence)
        social_alert = analyzer.should_social_cue_alert(social_cues, confidence)

        if emotional_alert or social_alert:
            print("🚨 WOULD TRIGGER ALERT")

        print()

if __name__ == "__main__":
    test_autism_adhd_scenarios()