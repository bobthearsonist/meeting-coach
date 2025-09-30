#!/usr/bin/env python3
"""
Quick test of the dashboard formatting
"""
import time
from dashboard import LiveDashboard
from timeline import EmotionalTimeline

def quick_test():
    dashboard = LiveDashboard()
    timeline = EmotionalTimeline()

    # Add some test entries with varying text lengths
    timeline.add_entry("calm", "appropriate", 0.8, "Starting the meeting with a brief agenda overview", False)
    timeline.add_entry("engaged", "appropriate", 0.8, "That's a really interesting point about the project timeline and how we can optimize the delivery schedule to meet our client's expectations while maintaining quality standards", False)
    timeline.add_entry("elevated", "interrupting", 0.8, "Oh wait, I just thought of something really important that we should consider - what if we approach this problem from a completely different angle", True)

    # Update current status with long text
    dashboard.update_current_status(
        emotional_state="elevated",
        social_cue="interrupting",
        confidence=0.8,
        text="This is a long piece of current text that should wrap properly and align nicely with the start of the sentence when it continues on the next line",
        coaching="Try pausing before speaking",
        alert=True,
        wpm=140,
        filler_counts={"um": 3, "uh": 1}
    )

    # Render once to see the format
    dashboard._render_dashboard(timeline)

if __name__ == "__main__":
    quick_test()
