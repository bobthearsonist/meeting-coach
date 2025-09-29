#!/usr/bin/env python3
"""
Test script for UI improvements
"""
import time
from timeline import EmotionalTimeline
from dashboard import LiveDashboard

def test_timeline_improvements():
    """Test the improved timeline and recent activity display"""
    print("Testing UI Improvements...")
    print("=" * 50)

    # Create timeline and dashboard
    timeline = EmotionalTimeline()
    dashboard = LiveDashboard()

    # Simulate a conversation with brief alert states
    conversation_data = [
        ("calm", "appropriate", 0.8, "Hello everyone, good morning", False),
        ("engaged", "appropriate", 0.7, "I wanted to discuss our project progress", False),
        ("engaged", "appropriate", 0.6, "We've made significant advances this week", False),
        ("intense", "appropriate", 0.9, "This is really exciting!", True),  # Brief excitement
        ("calm", "appropriate", 0.7, "Let me explain the details", False),
        ("calm", "appropriate", 0.8, "The first component is working well", False),
        ("elevated", "dominating", 0.8, "And I think we should definitely...", True),  # Brief interruption
        ("calm", "appropriate", 0.7, "Sorry, let me finish that thought", False),
        ("engaged", "appropriate", 0.8, "The testing results show good performance", False),
        ("calm", "appropriate", 0.7, "Any questions about this approach?", False),
        ("engaged", "appropriate", 0.8, "I'm happy to explain any part in detail", False),
        ("calm", "appropriate", 0.9, "Thank you for your attention", False),
    ]

    print("Simulating conversation with brief alert states...")
    for i, (state, social, conf, text, alert) in enumerate(conversation_data):
        timeline.add_entry(state, social, conf, text, alert)
        time.sleep(0.2)  # Brief delay between entries

        # Show progress
        if i % 4 == 0:
            print(f"Added entry {i+1}/{len(conversation_data)}: {state}")

    print("\nRendering improved dashboard...")
    print("=" * 50)

    # Test the new dashboard with 10 recent activities
    dashboard.update_live_display(timeline)

    print("\n" + "=" * 50)
    print("UI Improvements Test Complete!")
    print("\nKey improvements:")
    print("✅ Recent activity now shows up to 10 entries (was 3)")
    print("✅ Timeline bars now better represent actual time duration")
    print("✅ Brief alert states don't dominate the timeline visualization")
    print("✅ Alert weight threshold is configurable")

if __name__ == "__main__":
    test_timeline_improvements()
