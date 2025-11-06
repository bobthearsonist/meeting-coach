"""
Unit tests for the dashboard components
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.ui.dashboard import LiveDashboard
from src.ui.timeline import EmotionalTimeline


class TestLiveDashboard:
    """Test cases for LiveDashboard"""

    @pytest.fixture
    def dashboard(self):
        """Create dashboard instance for testing."""
        return LiveDashboard()

    @pytest.mark.unit
    def test_dashboard_initialization(self, dashboard):
        """Test dashboard initializes with correct default state."""
        assert hasattr(dashboard, "current_state")
        assert hasattr(dashboard, "alert_active")

    @pytest.mark.unit
    def test_terminal_width_detection(self, dashboard):
        """Test terminal width detection."""
        # Test the private method
        width = dashboard._get_terminal_width(default=80)
        assert isinstance(width, int)
        assert width >= 60  # Minimum width
        assert width <= 140  # Maximum width

    @pytest.mark.unit
    def test_state_color_mapping(self, dashboard):
        """Test emotional state color mapping."""
        test_states = ["calm", "engaged", "elevated", "intense", "unknown"]

        for state in test_states:
            color = dashboard._get_state_color(state)
            assert isinstance(color, str)

    @pytest.mark.unit
    def test_update_dashboard_data_storage(self, dashboard, dashboard_scenarios):
        """Test that dashboard stores update data correctly."""
        scenario = dashboard_scenarios[0]

        dashboard.update_current_status(
            emotional_state=scenario["state"],
            social_cue=scenario["cue"],
            confidence=scenario["confidence"],
            text=scenario["text"],
            coaching=scenario["coaching"],
            alert=scenario["alert"],
            wpm=scenario["wpm"],
        )

        # Check that data is stored in the correct attributes
        assert dashboard.current_state["emotional_state"] == scenario["state"]
        assert dashboard.current_social_cue == scenario["cue"]
        assert dashboard.current_confidence == scenario["confidence"]
        assert dashboard.current_text == scenario["text"]
        assert dashboard.current_coaching == scenario["coaching"]
        assert dashboard.alert_active == scenario["alert"]
        assert dashboard.current_wpm == scenario["wpm"]

    @pytest.mark.unit
    def test_text_wrapping_functionality(self, dashboard):
        """Test text wrapping utility function."""
        long_text = "This is a very long piece of text that should be wrapped properly when it exceeds the specified width limit"

        # Test basic wrapping
        wrapped = dashboard._wrap_text(long_text, 50)
        assert isinstance(wrapped, list)
        assert len(wrapped) > 1  # Should wrap into multiple lines

        # Test that no line exceeds the width
        for line in wrapped:
            assert len(line) <= 50

        # Test with indentation
        wrapped_with_indent = dashboard._wrap_text(long_text, 50, "    ")
        assert wrapped_with_indent[0] == wrapped[0]  # First line unchanged
        if len(wrapped_with_indent) > 1:
            assert wrapped_with_indent[1].startswith(
                "    "
            )  # Subsequent lines indented

    @pytest.mark.unit
    def test_terminal_width_adaptation(self, dashboard):
        """Test that dashboard adapts to different terminal widths."""
        # Test various terminal widths
        test_widths = [60, 80, 100, 120, 140]

        for width in test_widths:
            with patch("shutil.get_terminal_size") as mock_size:
                mock_size.return_value = Mock(columns=width)
                detected_width = dashboard._get_terminal_width()

                # Should respect min/max bounds
                assert 60 <= detected_width <= 140
                assert detected_width == min(max(width, 60), 140)

    @pytest.mark.unit
    def test_activity_formatting_alignment(self, dashboard):
        """Test that activity entries maintain proper column alignment."""
        from src.ui.timeline import EmotionalTimeline

        timeline = EmotionalTimeline()

        # Add entries with different state lengths to test alignment
        test_cases = [
            ("calm", "Short state text"),
            (
                "overwhelmed",
                "This is a much longer state text that should test wrapping",
            ),
            ("engaged", "Medium length text"),
            ("intense", "Another text entry"),
            ("elevated", "Final test entry"),
        ]

        for state, text in test_cases:
            timeline.add_entry(state, "appropriate", 0.8, text, False)

        # Test that rendering doesn't crash and maintains format
        try:
            # Capture output by redirecting stdout
            import io
            from contextlib import redirect_stdout

            captured_output = io.StringIO()
            with redirect_stdout(captured_output):
                dashboard._render_recent_activity(timeline, 80)

            output = captured_output.getvalue()
            lines = output.split("\n")

            # Find activity lines (skip headers)
            activity_lines = [line for line in lines if "|" in line and ":" in line]

            # Verify column alignment by checking pipe positions
            if activity_lines:
                first_line = activity_lines[0]
                pipe_positions = [i for i, char in enumerate(first_line) if char == "|"]

                # Check that all lines have pipes in the same positions
                for line in activity_lines[1:]:
                    line_pipes = [i for i, char in enumerate(line) if char == "|"]
                    # First two pipes should align (timestamp and state columns)
                    if len(line_pipes) >= 2 and len(pipe_positions) >= 2:
                        assert (
                            line_pipes[0] == pipe_positions[0]
                        ), f"First pipe misaligned in: {line}"
                        assert (
                            line_pipes[1] == pipe_positions[1]
                        ), f"Second pipe misaligned in: {line}"

        except Exception as e:
            pytest.fail(f"Activity formatting failed: {e}")


class TestEmotionalTimeline:
    """Test cases for EmotionalTimeline"""

    @pytest.fixture
    def timeline(self):
        """Create timeline instance for testing."""
        return EmotionalTimeline()

    @pytest.mark.unit
    def test_timeline_initialization(self, timeline):
        """Test timeline initializes correctly."""
        assert hasattr(timeline, "entries")
        assert len(timeline.entries) == 0
        assert hasattr(timeline, "window_minutes")
        assert hasattr(timeline, "max_entries")

    @pytest.mark.unit
    def test_add_entry(self, timeline):
        """Test adding entries to timeline."""
        timeline.add_entry("calm", "appropriate", 0.8, "Test event")

        assert len(timeline.entries) == 1
        entry = timeline.entries[0]
        assert entry.emotional_state == "calm"
        assert entry.social_cue == "appropriate"
        assert entry.confidence == 0.8
        assert entry.text == "Test event"
        assert isinstance(entry.timestamp, float)

    @pytest.mark.unit
    def test_add_multiple_events(self, timeline):
        """Test adding multiple entries maintains order."""
        events = [
            ("calm", "appropriate", 0.8, "First"),
            ("engaged", "appropriate", 0.9, "Second"),
            ("elevated", "interrupting", 0.7, "Third"),
        ]

        for state, cue, conf, desc in events:
            timeline.add_entry(state, cue, conf, desc)

        assert len(timeline.entries) == 3

        # Check order is maintained (chronological)
        assert timeline.entries[0].text == "First"
        assert timeline.entries[1].text == "Second"
        assert timeline.entries[2].text == "Third"

    @pytest.mark.unit
    def test_get_recent_events(self, timeline):
        """Test getting recent entries."""
        # Add entries
        for i in range(5):
            timeline.add_entry("calm", "appropriate", 0.8, f"Event {i}")

        recent = timeline.get_recent_entries(10)  # 10 minutes
        assert len(recent) <= 5

        # Should return TimelineEntry objects
        if recent:
            assert hasattr(recent[0], "emotional_state")
            assert hasattr(recent[0], "timestamp")

    @pytest.mark.unit
    def test_get_recent_events_less_than_limit(self, timeline):
        """Test getting recent entries when fewer than limit exist."""
        timeline.add_entry("calm", "appropriate", 0.8, "Only event")

        recent = timeline.get_recent_entries(10)
        assert len(recent) == 1
        assert recent[0].text == "Only event"

    @pytest.mark.unit
    def test_timeline_event_structure(self, timeline):
        """Test that entries have the correct structure."""
        timeline.add_entry("engaged", "appropriate", 0.9, "Test event", alert=True)

        entry = timeline.entries[0]
        assert hasattr(entry, "timestamp")
        assert hasattr(entry, "emotional_state")
        assert hasattr(entry, "social_cue")
        assert hasattr(entry, "confidence")
        assert hasattr(entry, "text")
        assert hasattr(entry, "alert")

        # Check values
        assert entry.emotional_state == "engaged"
        assert entry.social_cue == "appropriate"
        assert entry.confidence == 0.9
        assert entry.text == "Test event"
        assert entry.alert == True

    @pytest.mark.unit
    def test_get_dominant_state(self, timeline):
        """Test getting dominant emotional state."""
        # Add entries with different states
        timeline.add_entry("calm", "appropriate", 0.8, "Event 1")
        timeline.add_entry("calm", "appropriate", 0.9, "Event 2")
        timeline.add_entry("elevated", "interrupting", 0.7, "Event 3")

        dominant_state, confidence = timeline.get_dominant_state()
        assert dominant_state == "calm"  # Should be most frequent
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
