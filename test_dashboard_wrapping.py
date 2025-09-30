#!/usr/bin/env python3
"""
Test script to demonstrate dashboard word wrapping and resizing capabilities
"""
import time
from dashboard import LiveDashboard
from timeline import EmotionalTimeline

def test_dashboard_with_long_text():
    """Test the dashboard with long text entries to verify word wrapping"""
    dashboard = LiveDashboard()
    timeline = EmotionalTimeline()

    print("Testing dashboard with long text and word wrapping...")
    dashboard.initialize_display()

    time.sleep(1)

    # Test scenarios with progressively longer text
    test_scenarios = [
        ("calm", "appropriate", 0.8,
         "Starting the meeting with a brief agenda overview",
         "", False),

        ("engaged", "appropriate", 0.8,
         "That's a really interesting point about the project timeline and how we can optimize the delivery schedule to meet our client's expectations while maintaining quality standards",
         "", False),

        ("elevated", "interrupting", 0.8,
         "Oh wait, I just thought of something really important that we should consider - what if we approach this problem from a completely different angle and instead of focusing on the technical implementation details, we first establish a clear understanding of the user requirements and business objectives that drive this initiative",
         "Try pausing before speaking", True),

        ("intense", "dominating", 0.9,
         "Actually, you know what, I think there's a fundamental issue with our entire approach here and we need to step back and reconsider the architectural decisions we've made because they're going to create scalability problems down the road and we should really be thinking about microservices architecture with proper API design patterns and maybe consider implementing event-driven architecture with message queues for better decoupling of services",
         "Take a breath and let others speak", True),

        ("calm", "appropriate", 0.7,
         "Let me take a moment to process all of this information and think about the best path forward",
         "", False),
    ]

    for i, (state, cue, conf, text, coaching, alert) in enumerate(test_scenarios):
        time.sleep(2)

        # Add to timeline
        timeline.add_entry(state, cue, conf, text, alert)

        # Update dashboard
        dashboard.update_current_status(
            emotional_state=state,
            social_cue=cue,
            confidence=conf,
            text=text,
            coaching=coaching,
            alert=alert,
            wpm=120 + i * 20,
            filler_counts={"um": i, "uh": i//2, "like": i//3} if i > 0 else {}
        )

        dashboard.update_live_display(timeline)

    print("\nWord wrapping test complete! Try resizing your terminal window and the display should adapt.")
    print("Press Ctrl+C to exit when ready.")

    # Keep running to allow manual terminal resizing tests
    try:
        while True:
            time.sleep(3)
            # Refresh the display to show any terminal size changes
            dashboard.update_live_display(timeline)
    except KeyboardInterrupt:
        pass
    finally:
        dashboard.restore_display()

if __name__ == "__main__":
    test_dashboard_with_long_text()
