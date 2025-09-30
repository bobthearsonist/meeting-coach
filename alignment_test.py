#!/usr/bin/env python3
"""
Test alignment with different emotional state lengths
"""
import time
from dashboard import LiveDashboard
from timeline import EmotionalTimeline

def alignment_test():
    dashboard = LiveDashboard()
    timeline = EmotionalTimeline()

    # Add entries with different state lengths to test alignment
    test_states = [
        ("calm", "Short state"),
        ("overwhelmed", "Longest state name"),
        ("engaged", "Medium length"),
        ("intense", "Another medium"),
        ("elevated", "Yet another one")
    ]

    for state, description in test_states:
        timeline.add_entry(state, "appropriate", 0.8, f"{description} - this is a longer text that should wrap properly and align with the start of the text content after the pipes", False)

    # Update current status
    dashboard.update_current_status(
        emotional_state="overwhelmed",
        social_cue="dominating",
        confidence=0.9,
        text="This current text should also align properly when it wraps to the next line",
        coaching="",
        alert=False,
        wpm=120
    )

    # Render to see alignment
    dashboard._render_dashboard(timeline)

if __name__ == "__main__":
    alignment_test()
