#!/usr/bin/env python3
"""
Demo of the color-coded visual interface for autism/ADHD coaching
"""
from colors import Colors, colorize_emotional_state, colorize_social_cue
from timeline import EmotionalTimeline
from analyzer import CommunicationAnalyzer
import time

def demo_color_system():
    """Demonstrate the complete color-coded system"""
    print("🌈 COLOR-CODED AUTISM/ADHD COACHING DEMO")
    print("="*60)

    # Show color support status
    if Colors.is_supported():
        print("✅ Your terminal supports colors - full visual experience!")
    else:
        print("ℹ️  Colors not supported in this terminal, but system works without them")

    print(f"\n🎨 EMOTIONAL STATE COLORS:")
    emotional_states = [
        ('calm', 'Safe, regulated state - no coaching needed'),
        ('engaged', 'Positive engagement - good focus'),
        ('elevated', 'Getting excited - watch for escalation'),
        ('intense', 'High energy - may need regulation'),
        ('overwhelmed', 'Overloaded - needs immediate attention'),
        ('rapid', 'Speaking quickly - may indicate pressure'),
        ('distracted', 'Focus drifting - gentle redirection needed')
    ]

    for state, description in emotional_states:
        colored_state = colorize_emotional_state(state)
        analyzer = CommunicationAnalyzer()
        emoji = analyzer.get_tone_emoji(state)
        print(f"  {emoji} {colored_state:12} - {description}")

    print(f"\n🤝 SOCIAL CUE COLORS:")
    social_cues = [
        ('appropriate', 'Good social engagement'),
        ('interrupting', 'May be cutting others off'),
        ('dominating', 'Taking up too much conversation space'),
        ('too_quiet', 'Not participating enough'),
        ('repetitive', 'Speech patterns may indicate stimming'),
        ('off_topic', 'Focus has shifted away from discussion')
    ]

    for cue, description in social_cues:
        colored_cue = colorize_social_cue(cue)
        analyzer = CommunicationAnalyzer()
        emoji = analyzer.get_social_cue_emoji(cue)
        print(f"  {emoji} {colored_cue:12} - {description}")

    # Demo timeline with color-coded bars
    print(f"\n📊 TIMELINE VISUALIZATION:")
    timeline = EmotionalTimeline(window_minutes=5)

    # Create a realistic autism/ADHD coaching scenario
    scenario = [
        ("Starting meeting calmly", "calm", "appropriate", 0.8, False),
        ("Getting interested in topic", "engaged", "appropriate", 0.8, False),
        ("Idea sparks excitement", "elevated", "interrupting", 0.8, True),
        ("Hyperfocus kicks in", "intense", "dominating", 0.9, True),
        ("Realizes oversharing", "overwhelmed", "repetitive", 0.7, True),
        ("Takes a breath", "calm", "appropriate", 0.8, False),
        ("Back to productive discussion", "engaged", "appropriate", 0.8, False)
    ]

    for i, (desc, state, cue, conf, alert) in enumerate(scenario):
        timeline.add_entry(state, cue, conf, desc, alert)
        time.sleep(0.05)  # Small delay for realistic timestamps

    timeline.display_timeline(minutes=5, width=60)

    print(f"\n🧠 AUTISM/ADHD COACHING BENEFITS:")
    benefits = [
        "🎯 Visual feedback helps recognize emotional patterns",
        "⏰ Timeline shows regulation progress over time",
        "🚨 Alerts catch escalation before it becomes overwhelming",
        "📊 Session summaries build self-awareness",
        "🌈 Colors provide instant visual cues for emotional states",
        "💡 Coaching prompts are supportive, not judgmental"
    ]

    for benefit in benefits:
        print(f"  {benefit}")

    print(f"\n" + "="*60)
    print("🎉 Ready to start your autism/ADHD coaching session!")
    print("Run: ./run_with_venv.sh --device 5")
    print("="*60)

if __name__ == "__main__":
    demo_color_system()