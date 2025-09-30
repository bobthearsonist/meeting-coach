"""
Timeline tracking for emotional states and social cues over time
"""
import time
from collections import deque
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from colors import Colors, colorize_emotional_state, get_emotional_state_color


class TimelineEntry:
    """Single entry in the timeline"""
    def __init__(self, timestamp: float, emotional_state: str, social_cue: str,
                 confidence: float, text: str = "", alert: bool = False):
        self.timestamp = timestamp
        self.emotional_state = emotional_state
        self.social_cue = social_cue
        self.confidence = confidence
        self.text = text
        self.alert = alert

    @property
    def time_str(self) -> str:
        """Human readable time string"""
        dt = datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%H:%M:%S")

    def __repr__(self) -> str:
        return f"TimelineEntry({self.time_str}, {self.emotional_state}, {self.confidence:.1f})"


class EmotionalTimeline:
    """Tracks emotional states and social cues over time"""

    def __init__(self, window_minutes: int = 10, max_entries: int = 100):
        """
        Initialize timeline tracker

        Args:
            window_minutes: How many minutes to keep in the display window
            max_entries: Maximum number of entries to store
        """
        self.window_minutes = window_minutes
        self.max_entries = max_entries
        self.entries = deque(maxlen=max_entries)
        self.start_time = time.time()

    def add_entry(self, emotional_state: str, social_cue: str, confidence: float,
                  text: str = "", alert: bool = False) -> None:
        """Add a new timeline entry"""
        entry = TimelineEntry(
            timestamp=time.time(),
            emotional_state=emotional_state,
            social_cue=social_cue,
            confidence=confidence,
            text=text,
            alert=alert
        )
        self.entries.append(entry)

    def get_recent_entries(self, minutes: int = None) -> List[TimelineEntry]:
        """Get entries from the last N minutes"""
        if minutes is None:
            minutes = self.window_minutes

        cutoff_time = time.time() - (minutes * 60)
        return [entry for entry in self.entries if entry.timestamp >= cutoff_time]

    def get_dominant_state(self, minutes: int = None) -> Tuple[str, float]:
        """Get the most common emotional state in recent history"""
        recent_entries = self.get_recent_entries(minutes)

        if not recent_entries:
            return "unknown", 0.0

        # Count states weighted by confidence
        state_weights = {}
        total_weight = 0

        for entry in recent_entries:
            weight = entry.confidence
            state = entry.emotional_state
            state_weights[state] = state_weights.get(state, 0) + weight
            total_weight += weight

        if total_weight == 0:
            return "unknown", 0.0

        # Find dominant state
        dominant_state = max(state_weights.keys(), key=lambda k: state_weights[k])
        avg_confidence = state_weights[dominant_state] / len([e for e in recent_entries if e.emotional_state == dominant_state])

        return dominant_state, min(avg_confidence, 1.0)

    def get_alert_count(self, minutes: int = None) -> int:
        """Count alerts in recent history"""
        recent_entries = self.get_recent_entries(minutes)
        return sum(1 for entry in recent_entries if entry.alert)

    def display_timeline(self, minutes: int = None, width: int = 60) -> None:
        """Display visual timeline of emotional states"""
        recent_entries = self.get_recent_entries(minutes)

        if not recent_entries:
            print("📊 No recent activity to display")
            return

        print("\n" + "="*width)
        print("📊 EMOTIONAL TIMELINE (Last {} minutes)".format(minutes or self.window_minutes))
        print("="*width)

        # Display current state with enhanced formatting
        dominant_state, confidence = self.get_dominant_state(minutes)
        alert_count = self.get_alert_count(minutes)

        # Get emoji for the dominant state (use simple mapping to avoid analyzer overhead)
        emoji_map = {
            'calm': '🧘', 'neutral': '😐', 'engaged': '✨',
            'elevated': '⬆️', 'intense': '🔥', 'rapid': '⚡',
            'overwhelmed': '😵‍💫', 'distracted': '🤔', 'unknown': '❓'
        }
        state_emoji = emoji_map.get(dominant_state, '💬')

        state_color = get_emotional_state_color(dominant_state)
        dominant_colored = Colors.colorize(dominant_state.upper(), state_color)

        print(f"Current Dominant State: {state_emoji} {dominant_colored} (confidence: {confidence:.1f})")

        if alert_count > 0:
            alert_text = Colors.colorize(f"🚨 {alert_count} alerts", Colors.BRIGHT_RED)
            print(f"Recent Alerts: {alert_text}")
        else:
            calm_text = Colors.colorize("✅ No recent alerts", Colors.GREEN)
            print(f"Status: {calm_text}")
        print()

        # Display timeline bars
        self._display_timeline_bars(recent_entries, width-10)

        # Display recent entries
        print("\nRecent Entries:")
        print("-" * (width-20))

        for entry in recent_entries[-5:]:  # Last 5 entries
            state_colored = colorize_emotional_state(entry.emotional_state)
            alert_indicator = "🚨" if entry.alert else "  "
            confidence_bar = self._confidence_bar(entry.confidence)

            # Color-code the time if it's an alert
            time_str = entry.time_str
            if entry.alert:
                time_str = Colors.colorize(time_str, Colors.BRIGHT_RED)

            # Note: state_colored already includes color formatting, so we need to account for that
            # when calculating spacing. We'll just use a fixed width.
            print(f"{alert_indicator} {time_str} | {state_colored} | {confidence_bar} | {entry.text[:25]}")

    def _display_timeline_bars(self, entries: List[TimelineEntry], width: int) -> None:
        """Display visual timeline bars with color coding"""
        if not entries:
            return

        # Group entries into time buckets
        buckets = self._create_time_buckets(entries, width)

        # Create visual representation with color-coded bars
        bar_chars = {
            'calm': '▁', 'neutral': '▂', 'engaged': '▃',
            'elevated': '▅', 'intense': '▆', 'overwhelmed': '▇',
            'rapid': '▆', 'distracted': '▂', 'unknown': '▄'
        }

        print("Timeline (newest on right):")

        # Create the color-coded timeline bar
        timeline_str = ""
        for bucket_state in buckets:
            char = bar_chars.get(bucket_state, '▄')
            color = get_emotional_state_color(bucket_state)
            colored_char = Colors.colorize(char, color)
            timeline_str += colored_char

        print(timeline_str)

        # Add color legend if colors are supported
        if Colors.is_supported():
            legend_states = ['calm', 'engaged', 'elevated', 'intense', 'overwhelmed']
            legend_str = "Legend: "
            for state in legend_states:
                char = bar_chars.get(state, '▄')
                color = get_emotional_state_color(state)
                colored_char = Colors.colorize(char, color)
                legend_str += f"{colored_char}={state} "
            print(legend_str)

        # Add time labels
        start_time = entries[0].timestamp
        end_time = entries[-1].timestamp
        duration = end_time - start_time

        if duration > 0:
            start_dt = datetime.fromtimestamp(start_time)
            end_dt = datetime.fromtimestamp(end_time)
            print(f"{start_dt.strftime('%H:%M')}{' ' * (width-10)}{end_dt.strftime('%H:%M')}")

    def _create_time_buckets(self, entries: List[TimelineEntry], bucket_count: int) -> List[str]:
        """Create time buckets for timeline visualization, proportional to flagged segments"""
        if not entries:
            return []

        if len(entries) == 1:
            return [entries[0].emotional_state]

        # Count flagged vs unflagged entries
        flagged_entries = [e for e in entries if e.alert]
        unflagged_entries = [e for e in entries if not e.alert]
        
        total_flagged = len(flagged_entries)
        total_unflagged = len(unflagged_entries)
        
        # If no flagged entries, use simple time-based approach
        if total_flagged == 0:
            return self._create_simple_time_buckets(entries, bucket_count)
        
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
        
        return buckets
    
    def _create_simple_time_buckets(self, entries: List[TimelineEntry], bucket_count: int) -> List[str]:
        """Create simple time-based buckets (fallback method)"""
        start_time = entries[0].timestamp
        end_time = entries[-1].timestamp
        duration = end_time - start_time

        if duration == 0:
            return [entries[0].emotional_state]

        bucket_duration = duration / bucket_count
        buckets = []

        for i in range(bucket_count):
            bucket_start = start_time + (i * bucket_duration)
            bucket_end = bucket_start + bucket_duration

            # Find entries in this bucket
            bucket_entries = [
                entry for entry in entries
                if bucket_start <= entry.timestamp < bucket_end
            ]

            if bucket_entries:
                # Use the most confident entry in the bucket
                best_entry = max(bucket_entries, key=lambda e: e.confidence)
                buckets.append(best_entry.emotional_state)
            else:
                # Use previous bucket's state or neutral
                buckets.append(buckets[-1] if buckets else 'neutral')

        return buckets

    def _confidence_bar(self, confidence: float, width: int = 10) -> str:
        """Create a visual confidence bar"""
        filled = int(confidence * width)
        bar = "█" * filled + "░" * (width - filled)

        if confidence >= 0.7:
            color = Colors.GREEN
        elif confidence >= 0.4:
            color = Colors.YELLOW
        else:
            color = Colors.RED

        return Colors.colorize(bar, color)

    def get_session_summary(self) -> Dict:
        """Get summary of the entire session"""
        if not self.entries:
            return {"error": "No entries recorded"}

        # Calculate session duration
        session_duration = time.time() - self.start_time

        # Count states
        state_counts = {}
        alert_count = 0
        total_confidence = 0

        for entry in self.entries:
            state = entry.emotional_state
            state_counts[state] = state_counts.get(state, 0) + 1
            if entry.alert:
                alert_count += 1
            total_confidence += entry.confidence

        dominant_state = max(state_counts.keys(), key=lambda k: state_counts[k]) if state_counts else "unknown"
        avg_confidence = total_confidence / len(self.entries) if self.entries else 0.0

        return {
            "session_duration_minutes": session_duration / 60,
            "total_entries": len(self.entries),
            "dominant_state": dominant_state,
            "state_distribution": state_counts,
            "alert_count": alert_count,
            "average_confidence": avg_confidence
        }


if __name__ == "__main__":
    # Test the timeline
    timeline = EmotionalTimeline()

    # Add some test entries
    import random
    states = ['calm', 'engaged', 'elevated', 'intense', 'overwhelmed']
    social_cues = ['appropriate', 'interrupting', 'dominating']

    print("Adding test timeline entries...")
    for i in range(20):
        state = random.choice(states)
        cue = random.choice(social_cues)
        conf = random.uniform(0.3, 0.9)
        alert = conf > 0.7 and state in ['intense', 'overwhelmed']

        timeline.add_entry(state, cue, conf, f"Test entry {i}", alert)
        time.sleep(0.1)  # Small delay

    # Display timeline
    timeline.display_timeline()

    print("\nSession Summary:")
    summary = timeline.get_session_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")