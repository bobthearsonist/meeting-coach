#!/usr/bin/env python3
"""
Demo script to demonstrate dashboard word wrapping and terminal resizing capabilities
"""
import time
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dashboard import LiveDashboard
from timeline import EmotionalTimeline

def demo_dashboard_text_wrapping():
    """Demonstrate the dashboard with long text entries to show word wrapping"""
    dashboard = LiveDashboard()
    timeline = EmotionalTimeline()

    print("🎯 Dashboard Text Wrapping & Resizing Demo")
    print("=" * 50)
    print("This demo shows how the dashboard handles:")
    print("- Long text with proper word wrapping")
    print("- Column alignment across different emotional states")
    print("- Dynamic terminal resizing")
    print("\nTry resizing your terminal window during the demo!")
    print("=" * 50)

    dashboard.initialize_display()
    time.sleep(2)

    # Demo scenarios with progressively longer text
    demo_scenarios = [
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

    for i, (state, cue, conf, text, coaching, alert) in enumerate(demo_scenarios):
        print(f"\n📝 Adding scenario {i+1}/5: {state.upper()} state...")
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

    print("\n🎉 Word wrapping demo complete!")
    print("\n💡 Key features demonstrated:")
    print("  ✅ Text wrapping with proper alignment")
    print("  ✅ Column alignment across different state names")
    print("  ✅ Full text visibility (no truncation)")
    print("  ✅ Dynamic terminal width adaptation")
    print("\n🔄 Now running continuous refresh to demo terminal resizing...")
    print("   Try resizing your terminal window!")
    print("   Press Ctrl+C to exit when ready.")

    # Keep running to allow manual terminal resizing tests
    try:
        refresh_count = 0
        while True:
            time.sleep(3)
            refresh_count += 1
            # Refresh the display to show any terminal size changes
            dashboard.update_live_display(timeline)
            if refresh_count % 5 == 0:
                print(f"\n📏 Refresh #{refresh_count} - Current terminal width: {dashboard.last_terminal_width} chars")
    except KeyboardInterrupt:
        print("\n👋 Demo ended by user")
    finally:
        dashboard.restore_display()

if __name__ == "__main__":
    demo_dashboard_text_wrapping()
