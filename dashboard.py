"""
In-place updating dashboard for autism/ADHD coaching
"""
import os
import sys
import time
import shutil
import textwrap
from typing import Dict, Optional, List
from datetime import datetime
from colors import Colors, colorize_emotional_state, colorize_social_cue, colorize_alert
from timeline import EmotionalTimeline


class LiveDashboard:
    """Live updating dashboard that refreshes in place"""

    def __init__(self):
        self.current_state = {
            'emotional_state': "neutral",
            'social_cue': "unknown",
            'confidence': 0.0,
            'wpm': 0,
            'text': "",
            'coaching': "",
            'alert': False
        }
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
        # Width will be recalculated on each render to handle window resizing
        self.last_terminal_width = 80
        # No fixed height; we fully redraw the screen each update
        self.dashboard_height = None
        self._alt_screen_active = False

    def _supports_ansi(self) -> bool:
        """Check if terminal supports ANSI escape codes"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def _wrap_text(self, text: str, width: int, indent: str = "    ") -> List[str]:
        """Wrap text to fit within specified width with optional indentation"""
        if not text:
            return []

        # Account for indent in width calculation
        available_width = max(20, width - len(indent))

        # Use textwrap to handle the wrapping
        wrapped_lines = textwrap.wrap(text, width=available_width)

        # Add indentation to all lines except the first (if needed)
        if wrapped_lines:
            return [wrapped_lines[0]] + [indent + line for line in wrapped_lines[1:]]
        return []

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
        # Always get fresh terminal width to handle window resizing
        width = self._get_terminal_width(default=80)
        self.last_terminal_width = width

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
        state_colored = colorize_emotional_state(self.current_state['emotional_state'])
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
                coaching_colored = Colors.colorize(self.current_coaching, Colors.BOLD + Colors.BRIGHT_YELLOW)
                print(f"💡 {coaching_colored}")
        else:
            calm_text = Colors.colorize("✅ All good - no alerts", Colors.GREEN)
            print(f"\n{calm_text}")

        # Current speech
        if self.current_text:
            prefix = "🗣️  Recent: \""
            continuation_indent = " " * len("🗣️  Recent: ")

            # Wrap the text to fit within available width
            available_width = width - len(prefix) - 1  # -1 for closing quote
            wrapped_lines = textwrap.wrap(self.current_text, width=max(20, available_width))

            if wrapped_lines:
                # Print first line with prefix and opening quote
                print(f"\n{prefix}{wrapped_lines[0]}{'\"' if len(wrapped_lines) == 1 else ''}")
                # Print continuation lines with proper alignment
                for i, line in enumerate(wrapped_lines[1:]):
                    is_last = i == len(wrapped_lines) - 2
                    print(f"{continuation_indent}{line}{'\"' if is_last else ''}")

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
            # Show last 3 entries with proper column alignment
            for entry in recent_entries[-3:]:
                timestamp = datetime.fromtimestamp(entry.timestamp).strftime("%H:%M:%S")
                state_colored = colorize_emotional_state(entry.emotional_state)

                alert_indicator = "🚨" if entry.alert else "  "

                # Create fixed-width columns for consistent alignment
                # Format: "🚨 HH:MM:SS | state     | text..."
                state_width = 12  # Fixed width for emotional state column to fit "OVERWHELMED"

                # Build the template without colors for precise alignment calculation
                state_plain = entry.emotional_state.upper()
                template_prefix = f"{alert_indicator}{timestamp} | {state_plain:<{state_width}} | "

                # Build the display version with colors, ensuring same width
                # We need to pad the colored state to the same visual width
                state_colored_padded = state_colored + " " * (state_width - len(state_plain))
                display_prefix = f"{alert_indicator}{timestamp} | {state_colored_padded} | "

                if entry.text:
                    # Use the template length for continuation indent
                    continuation_indent = " " * len(template_prefix)

                    # Wrap the text to fit within the available width
                    available_width = width - len(template_prefix)
                    wrapped_lines = textwrap.wrap(entry.text, width=max(20, available_width))

                    if wrapped_lines:
                        # Print first line with colored prefix
                        print(f"{display_prefix}{wrapped_lines[0]}")
                        # Print continuation lines with proper alignment
                        for line in wrapped_lines[1:]:
                            print(f"{continuation_indent}{line}")
                else:
                    print(f"{display_prefix}(No text)")
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
        state_text = self.current_state['emotional_state'].upper()

        if self.alert_active:
            print(f"[{timestamp}] 🚨 ALERT: {state_text} | {self.current_coaching}")
        else:
            print(f"[{timestamp}] Status: {state_text} | Confidence: {self.current_confidence:.1f}")

    def _create_mini_buckets(self, entries, bucket_count: int) -> List[str]:
        """Create time buckets for mini timeline, proportional to flagged segments
        
        This method gives flagged (alert) segments more visual representation in the mini timeline
        by allocating bucket space with a 3:1 weight ratio (flagged:unflagged).
        This ensures consistency with the main timeline display.
        """
        if not entries or bucket_count <= 0:
            return []

        if len(entries) == 1:
            return [entries[0].emotional_state]

        # Count flagged vs unflagged entries
        flagged_entries = [e for e in entries if e.alert]
        unflagged_entries = [e for e in entries if not e.alert]
        
        total_flagged = len(flagged_entries)
        total_unflagged = len(unflagged_entries)
        
        # If no flagged entries, use simple entry-based approach
        if total_flagged == 0:
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
        
        # Calculate proportional bucket allocation
        # Give flagged segments more visual weight (3:1 ratio)
        flagged_weight = 3
        unflagged_weight = 1
        
        total_weight = (total_flagged * flagged_weight) + (total_unflagged * unflagged_weight)
        
        # Calculate bucket allocation
        flagged_buckets = int((total_flagged * flagged_weight / total_weight) * bucket_count)
        unflagged_buckets = bucket_count - flagged_buckets
        
        # Ensure at least one bucket for each type if they exist
        if total_flagged > 0 and flagged_buckets == 0:
            flagged_buckets = 1
            unflagged_buckets = bucket_count - 1
        if total_unflagged > 0 and unflagged_buckets == 0:
            unflagged_buckets = 1
            flagged_buckets = bucket_count - 1
            
        buckets = []
        
        # Fill buckets with flagged entries first
        if flagged_buckets > 0:
            for i in range(flagged_buckets):
                entry_index = int(i * len(flagged_entries) / flagged_buckets)
                if entry_index < len(flagged_entries):
                    buckets.append(flagged_entries[entry_index].emotional_state)
                else:
                    buckets.append(flagged_entries[-1].emotional_state)
        
        # Fill remaining buckets with unflagged entries
        if unflagged_buckets > 0:
            for i in range(unflagged_buckets):
                entry_index = int(i * len(unflagged_entries) / unflagged_buckets)
                if entry_index < len(unflagged_entries):
                    buckets.append(unflagged_entries[entry_index].emotional_state)
                else:
                    buckets.append(unflagged_entries[-1].emotional_state)
        
        return buckets[:bucket_count]

    def _get_state_color(self, state: str) -> str:
        """Get color for emotional state"""
        from colors import get_emotional_state_color
        return get_emotional_state_color(state)

    def update_current_status(self, emotional_state: str, social_cue: str, confidence: float,
                            text: str = "", coaching: str = "", alert: bool = False,
                            wpm: float = 0, filler_counts: Dict = None):
        """Update current status information"""
        self.current_state = {
            'emotional_state': emotional_state,
            'social_cue': social_cue,
            'confidence': confidence,
            'text': text,
            'coaching': coaching,
            'alert': alert,
            'wpm': wpm
        }
        self.current_social_cue = social_cue
        self.current_confidence = confidence
        self.current_text = text
        self.current_coaching = coaching
        self.alert_active = alert
        self.current_wpm = wpm
        self.filler_counts = filler_counts or {}

    def initialize_display(self, initialization_info=None):
        """Initialize the dashboard display"""
        self.enter_alt_screen()
        self.clear_screen()

        # Get fresh terminal width for initialization
        width = self._get_terminal_width(default=80)
        self.last_terminal_width = width

        print("=" * width)
        print("🧠 AUTISM/ADHD MEETING COACH - INITIALIZING")
        print("=" * width)
        print()

        # Display initialization information if provided
        if initialization_info:
            print("Initializing Teams Meeting Coach...")
            if initialization_info.get('audio_device'):
                print(f"Using audio device: {initialization_info['audio_device']}")
            if initialization_info.get('whisper_model'):
                print(f"Loading Whisper model: {initialization_info['whisper_model']}")
                print("Whisper model loaded successfully")
            if initialization_info.get('ollama_model'):
                print(f"Connected to Ollama. Using model: {initialization_info['ollama_model']}")
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
            # Ensure minimum width for readability, maximum for performance
            return max(60, min(cols, 140))
        except Exception:
            # Fallback to last known width or default
            return getattr(self, 'last_terminal_width', default)


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
