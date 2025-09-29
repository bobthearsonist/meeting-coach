"""
In-place updating dashboard for autism/ADHD coaching
"""
import os
import sys
import time
import shutil
from typing import Dict, Optional, List
from datetime import datetime
from colors import Colors, colorize_emotional_state, colorize_social_cue, colorize_alert
from timeline import EmotionalTimeline


class LiveDashboard:
    """Live updating dashboard that refreshes in place"""

    def __init__(self):
        self.current_state = "neutral"
        self.current_social_cue = "unknown"
        self.current_confidence = 0.0
        self.current_wpm = 0
        self.current_text = ""
        self.current_coaching = ""
        self.alert_active = False
        self.filler_counts = {}
        self.session_start = time.time()

        # Terminal control
        self.supports_ansi = self._supports_ansi()
        # No fixed height; we fully redraw the screen each update
        self.dashboard_height = None
        self._alt_screen_active = False

    def _supports_ansi(self) -> bool:
        """Check if terminal supports ANSI escape codes"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def clear_screen(self):
        """Clear the entire screen, scrollback, and move cursor to home"""
        if self.supports_ansi:
            # Clear scrollback (3J), clear screen (2J), move home (H)
            sys.stdout.write("\033[3J\033[2J\033[H")
            sys.stdout.flush()
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

    def enter_alt_screen(self):
        """Switch to the terminal's alternate screen buffer (no scrollback)."""
        if self.supports_ansi and not self._alt_screen_active:
            # Enter alternate screen, hide cursor
            sys.stdout.write("\033[?1049h\033[?25l")
            sys.stdout.flush()
            self._alt_screen_active = True

    def exit_alt_screen(self):
        """Return to the normal screen buffer and show cursor."""
        if self.supports_ansi and self._alt_screen_active:
            # Ensure we clear before exiting to avoid residual artifacts
            sys.stdout.write("\033[?25h\033[?1049l")
            sys.stdout.flush()
            self._alt_screen_active = False

    def move_cursor_up(self, lines: int):
        """Move cursor up by specified lines"""
        if self.supports_ansi:
            print(f"\033[{lines}A", end="", flush=True)

    def clear_lines(self, lines: int):
        """Clear specified number of lines from current position"""
        if self.supports_ansi:
            for _ in range(lines):
                print("\033[2K", end="")  # Clear current line
                if _ < lines - 1:
                    print("\033[B", end="")  # Move down one line
            print(f"\033[{lines}A", end="", flush=True)  # Move back up

    def update_live_display(self, timeline: EmotionalTimeline):
        """Update the live dashboard display without causing scroll"""
        if not self.supports_ansi:
            # Fallback for terminals without ANSI support
            self._print_simple_update()
            return

        # Fully clear and redraw to avoid perpetual scroll
        self.clear_screen()
        self._render_dashboard(timeline)

    def _render_dashboard(self, timeline: EmotionalTimeline):
        """Render the complete dashboard"""
        width = self._get_terminal_width(default=80)
        
        # Header (left-aligned to avoid emoji/centering width issues)
        print("=" * width)
        print("🧠 AUTISM/ADHD MEETING COACH - LIVE EMOTIONAL MONITORING")
        print("=" * width)

        # Current status section
        self._render_current_status(width)

        # Timeline section
        self._render_timeline_section(timeline, width)

        # Recent activity section
        self._render_recent_activity(timeline, width)

        # Stats section
        self._render_session_stats(timeline, width)

        # Footer
        print("-" * width)
        session_duration = (time.time() - self.session_start) / 60
        print(f"Session: {session_duration:.1f}min | Press Ctrl+C to stop and see summary")
        print("=" * width)

    def _render_current_status(self, width: int):
        """Render current emotional state and status"""
        print("\n📊 CURRENT STATUS")
        print("-" * 20)

        # Emotional state with color
        state_colored = colorize_emotional_state(self.current_state)
        cue_colored = colorize_social_cue(self.current_social_cue)

        # Build status line
        status_parts = [
            f"State: {state_colored}",
            f"Social: {cue_colored}",
            f"Confidence: {self.current_confidence:.1f}",
        ]

        if self.current_wpm > 0:
            wpm_color = Colors.GREEN if 100 <= self.current_wpm <= 180 else Colors.YELLOW
            wpm_colored = Colors.colorize(f"{self.current_wpm:.0f} WPM", wpm_color)
            status_parts.append(f"Pace: {wpm_colored}")

        print(" | ".join(status_parts))

        # Alert section
        if self.alert_active:
            alert_text = colorize_alert("🚨 COACHING ALERT ACTIVE", True)
            print(f"\n{alert_text}")
            if self.current_coaching:
                coaching_colored = Colors.colorize(self.current_coaching, Colors.BRIGHT_CYAN)
                print(f"💡 {coaching_colored}")
        else:
            calm_text = Colors.colorize("✅ All good - no alerts", Colors.GREEN)
            print(f"\n{calm_text}")

        # Current speech
        if self.current_text:
            print(f"\n🗣️  Recent: \"{self.current_text[:60]}{'...' if len(self.current_text) > 60 else ''}\"")

        # Filler words
        if self.filler_counts:
            filler_text = ", ".join([f"{word}:{count}" for word, count in self.filler_counts.items()])
            print(f"🔄 Filler words: {filler_text}")

        print()

    def _render_timeline_section(self, timeline: EmotionalTimeline, width: int):
        """Render the timeline visualization"""
        print("📈 EMOTIONAL TIMELINE (Last 5 minutes)")
        print("-" * 40)

        recent_entries = timeline.get_recent_entries(5)
        if recent_entries:
            # Get dominant state
            dominant_state, confidence = timeline.get_dominant_state(5)
            alert_count = timeline.get_alert_count(5)

            # Status line
            emoji_map = {
                'calm': '🧘', 'engaged': '✨', 'elevated': '⬆️',
                'intense': '🔥', 'overwhelmed': '😵‍💫', 'unknown': '❓'
            }
            state_emoji = emoji_map.get(dominant_state, '💬')
            dominant_colored = colorize_emotional_state(dominant_state.upper())

            print(f"Dominant: {state_emoji} {dominant_colored} ({confidence:.1f})")

            if alert_count > 0:
                alert_text = colorize_alert(f"🚨 {alert_count} alerts", True)
                print(f"Alerts: {alert_text}")

            # Mini timeline
            self._render_mini_timeline(recent_entries, width - 10)
        else:
            print("No recent activity to display")

        print()

    def _render_mini_timeline(self, entries: List, width: int):
        """Render a compact timeline bar"""
        if not entries:
            return

        # Create time buckets
        buckets = self._create_mini_buckets(entries, min(width, 50))

        # Render timeline
        bar_chars = {
            'calm': '▁', 'engaged': '▃', 'elevated': '▅',
            'intense': '▆', 'overwhelmed': '▇', 'unknown': '▄'
        }

        timeline_str = ""
        for state in buckets:
            char = bar_chars.get(state, '▄')
            color = self._get_state_color(state)
            colored_char = Colors.colorize(char, color)
            timeline_str += colored_char

        print(f"Timeline: {timeline_str}")

        # Time range
        if len(entries) > 1:
            start_time = datetime.fromtimestamp(entries[0].timestamp)
            end_time = datetime.fromtimestamp(entries[-1].timestamp)
            print(f"Range: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")

    def _render_recent_activity(self, timeline: EmotionalTimeline, width: int):
        """Render recent activity log"""
        print("📋 RECENT ACTIVITY (Last 3 entries)")
        print("-" * 35)

        recent_entries = timeline.get_recent_entries(5)
        if recent_entries:
            # Show last 3 entries
            for entry in recent_entries[-3:]:
                timestamp = datetime.fromtimestamp(entry.timestamp).strftime("%H:%M:%S")
                state_colored = colorize_emotional_state(entry.emotional_state)

                alert_indicator = "🚨" if entry.alert else "  "
                print(f"{alert_indicator} {timestamp} | {state_colored} | {entry.text[:30]}")
        else:
            print("  No activity yet - start speaking!")

        print()

    def _render_session_stats(self, timeline: EmotionalTimeline, width: int):
        """Render session statistics"""
        print("📊 SESSION STATS")
        print("-" * 16)

        summary = timeline.get_session_summary()
        duration = summary.get('session_duration_minutes', 0)
        total_analyses = summary.get('total_entries', 0)
        alert_count = summary.get('alert_count', 0)

        stats_line = f"Duration: {duration:.1f}min | Analyses: {total_analyses} | Alerts: {alert_count}"
        print(stats_line)

        # State distribution (top 3)
        state_dist = summary.get('state_distribution', {})
        if state_dist:
            top_states = sorted(state_dist.items(), key=lambda x: x[1], reverse=True)[:3]
            dist_parts = []
            for state, count in top_states:
                percentage = (count / total_analyses) * 100 if total_analyses > 0 else 0
                state_colored = colorize_emotional_state(state)
                dist_parts.append(f"{state_colored}:{percentage:.0f}%")
            print(f"Top states: {' | '.join(dist_parts)}")

    def _print_simple_update(self):
        """Simple update for terminals without ANSI support"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        state_text = self.current_state.upper()

        if self.alert_active:
            print(f"[{timestamp}] 🚨 ALERT: {state_text} | {self.current_coaching}")
        else:
            print(f"[{timestamp}] Status: {state_text} | Confidence: {self.current_confidence:.1f}")

    def _create_mini_buckets(self, entries, bucket_count: int) -> List[str]:
        """Create time buckets for mini timeline"""
        if not entries or bucket_count <= 0:
            return []

        if len(entries) == 1:
            return [entries[0].emotional_state]

        # Simple approach: divide entries into buckets
        entries_per_bucket = max(1, len(entries) // bucket_count)
        buckets = []

        for i in range(0, len(entries), entries_per_bucket):
            bucket_entries = entries[i:i + entries_per_bucket]
            if bucket_entries:
                # Use the most confident entry in the bucket
                best_entry = max(bucket_entries, key=lambda e: e.confidence)
                buckets.append(best_entry.emotional_state)

        # Pad or trim to exact bucket count
        while len(buckets) < bucket_count:
            buckets.append(buckets[-1] if buckets else 'neutral')

        return buckets[:bucket_count]

    def _get_state_color(self, state: str) -> str:
        """Get color for emotional state"""
        from colors import get_emotional_state_color
        return get_emotional_state_color(state)

    def update_current_status(self, emotional_state: str, social_cue: str, confidence: float,
                            text: str = "", coaching: str = "", alert: bool = False,
                            wpm: float = 0, filler_counts: Dict = None):
        """Update current status information"""
        self.current_state = emotional_state
        self.current_social_cue = social_cue
        self.current_confidence = confidence
        self.current_text = text
        self.current_coaching = coaching
        self.alert_active = alert
        self.current_wpm = wpm
        self.filler_counts = filler_counts or {}

    def initialize_display(self):
        """Initialize the dashboard display"""
        self.enter_alt_screen()
        self.clear_screen()

        width = self._get_terminal_width(default=80)
        print("=" * width)
        print("🧠 AUTISM/ADHD MEETING COACH - INITIALIZING")
        print("=" * width)
        print()
        print("🎯 Ready to start monitoring your emotional state...")
        print("💡 The display will update in real-time as you speak")
        print("=" * width)

    def restore_display(self):
        """Restore terminal to its normal state (called on exit)."""
        # Clear dashboard and exit alternate screen
        self.clear_screen()
        self.exit_alt_screen()

    def _get_terminal_width(self, default: int = 80) -> int:
        """Safely determine terminal width for clean layout"""
        try:
            cols = shutil.get_terminal_size((default, 24)).columns
            return max(60, min(cols, 140))
        except Exception:
            return default


if __name__ == "__main__":
    # Test the live dashboard
    dashboard = LiveDashboard()
    timeline = EmotionalTimeline()

    print("Testing live dashboard...")
    dashboard.initialize_display()

    time.sleep(2)

    # Simulate updates
    test_scenarios = [
        ("calm", "appropriate", 0.8, "Starting the meeting", "", False),
        ("engaged", "appropriate", 0.8, "Good point about the project", "", False),
        ("elevated", "interrupting", 0.8, "Oh I have an idea!", "Try pausing before speaking", True),
        ("intense", "dominating", 0.9, "We could do this and that", "Take a breath", True),
        ("calm", "appropriate", 0.7, "Let me think about that", "", False),
    ]

    for i, (state, cue, conf, text, coaching, alert) in enumerate(test_scenarios):
        time.sleep(1)

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
            wpm=150 + i * 10
        )

        dashboard.update_live_display(timeline)

    print("\nLive dashboard test complete!")
