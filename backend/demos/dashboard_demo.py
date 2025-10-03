#!/usr/bin/env python3
"""
Demo of the complete in-place updating dashboard
"""
import time
from dashboard import LiveDashboard
from timeline import EmotionalTimeline

def demo_live_dashboard():
    """Demonstrate the live updating dashboard"""
    dashboard = LiveDashboard()
    timeline = EmotionalTimeline()

    print("🚀 LIVE DASHBOARD DEMO")
    print("This will show the in-place updating interface...")
    print("Watch as the dashboard updates without scrolling!")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    # Initialize dashboard
    dashboard.initialize_display()
    time.sleep(2)

    # Simulate a realistic autism/ADHD coaching session
    scenarios = [
        {
            'desc': 'Starting meeting calmly',
            'state': 'calm', 'cue': 'appropriate', 'conf': 0.8,
            'text': 'Good morning everyone, thanks for joining',
            'coaching': '', 'alert': False, 'wpm': 140
        },
        {
            'desc': 'Getting interested',
            'state': 'engaged', 'cue': 'appropriate', 'conf': 0.8,
            'text': 'That\'s a really interesting point about the project',
            'coaching': '', 'alert': False, 'wpm': 150
        },
        {
            'desc': 'Excitement building',
            'state': 'elevated', 'cue': 'interrupting', 'conf': 0.8,
            'text': 'Oh wait, I just had this amazing idea we could implement!',
            'coaching': 'You seem excited! Try taking a breath before sharing your idea.',
            'alert': True, 'wpm': 170
        },
        {
            'desc': 'Hyperfocus activated',
            'state': 'intense', 'cue': 'dominating', 'conf': 0.9,
            'text': 'We could build this feature and integrate with that system and maybe also add analytics',
            'coaching': 'Lots of great ideas! Consider pausing to let others respond.',
            'alert': True, 'wpm': 190
        },
        {
            'desc': 'Using filler words',
            'state': 'rapid', 'cue': 'repetitive', 'conf': 0.8,
            'text': 'Like, um, I think we should, like, maybe consider the alternatives, you know?',
            'coaching': 'Notice the repeated filler words - try slowing down your speech.',
            'alert': True, 'wpm': 200,
            'filler': {'like': 2, 'um': 1, 'you know': 1}
        },
        {
            'desc': 'Becoming overwhelmed',
            'state': 'overwhelmed', 'cue': 'off_topic', 'conf': 0.7,
            'text': 'There\'s just so many options and I don\'t know which one is best',
            'coaching': 'Feeling overwhelmed is normal. Take a deep breath and focus on one thing.',
            'alert': True, 'wpm': 180
        },
        {
            'desc': 'Taking a breath',
            'state': 'calm', 'cue': 'appropriate', 'conf': 0.8,
            'text': 'Let me step back and think about this more clearly',
            'coaching': '', 'alert': False, 'wpm': 130
        },
        {
            'desc': 'Back on track',
            'state': 'engaged', 'cue': 'appropriate', 'conf': 0.8,
            'text': 'I think the main priority should be user experience',
            'coaching': '', 'alert': False, 'wpm': 140
        },
        {
            'desc': 'Productive discussion',
            'state': 'engaged', 'cue': 'appropriate', 'conf': 0.9,
            'text': 'What do you think about that approach?',
            'coaching': '', 'alert': False, 'wpm': 135
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        # Add to timeline
        timeline.add_entry(
            emotional_state=scenario['state'],
            social_cue=scenario['cue'],
            confidence=scenario['conf'],
            text=scenario['text'],
            alert=scenario['alert']
        )

        # Update dashboard
        dashboard.update_current_status(
            emotional_state=scenario['state'],
            social_cue=scenario['cue'],
            confidence=scenario['conf'],
            text=scenario['text'],
            coaching=scenario['coaching'],
            alert=scenario['alert'],
            wpm=scenario['wpm'],
            filler_counts=scenario.get('filler', {})
        )

        # Update live display
        dashboard.update_live_display(timeline)

        # Pause to show the update
        time.sleep(2 if scenario['alert'] else 1.5)

    # Final pause to review
    print("\nDemo complete! This is how the live dashboard will work during your meetings.")
    print("✅ No more scrolling - everything updates in place!")
    print("🧠 Perfect for autism/ADHD emotional regulation coaching")

if __name__ == "__main__":
    demo_live_dashboard()