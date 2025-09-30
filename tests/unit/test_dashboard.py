"""
Unit tests for the dashboard components
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from dashboard import LiveDashboard
from timeline import EmotionalTimeline

class TestLiveDashboard:
    """Test cases for LiveDashboard"""

    @pytest.fixture
    def dashboard(self):
        """Create dashboard instance for testing."""
        return LiveDashboard()

    @pytest.mark.unit
    def test_dashboard_initialization(self, dashboard):
        """Test dashboard initializes with correct default state."""
        assert hasattr(dashboard, 'current_state')
        assert hasattr(dashboard, 'alert_active')

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
        test_states = ['calm', 'engaged', 'elevated', 'intense', 'unknown']

        for state in test_states:
            color = dashboard._get_state_color(state)
            assert isinstance(color, str)

    @pytest.mark.unit
    def test_update_dashboard_data_storage(self, dashboard, dashboard_scenarios):
        """Test that dashboard stores update data correctly."""
        scenario = dashboard_scenarios[0]

        dashboard.update_current_status(
            emotional_state=scenario['state'],
            social_cue=scenario['cue'],
            confidence=scenario['confidence'],
            text=scenario['text'],
            coaching=scenario['coaching'],
            alert=scenario['alert'],
            wpm=scenario['wpm']
        )

        # Check that data is stored in the correct attributes
        assert dashboard.current_state['emotional_state'] == scenario['state']
        assert dashboard.current_social_cue == scenario['cue']
        assert dashboard.current_confidence == scenario['confidence']
        assert dashboard.current_text == scenario['text']
        assert dashboard.current_coaching == scenario['coaching']
        assert dashboard.alert_active == scenario['alert']
        assert dashboard.current_wpm == scenario['wpm']

class TestEmotionalTimeline:
    """Test cases for EmotionalTimeline"""

    @pytest.fixture
    def timeline(self):
        """Create timeline instance for testing."""
        return EmotionalTimeline()

    @pytest.mark.unit
    def test_timeline_initialization(self, timeline):
        """Test timeline initializes correctly."""
        assert hasattr(timeline, 'entries')
        assert len(timeline.entries) == 0
        assert hasattr(timeline, 'window_minutes')
        assert hasattr(timeline, 'max_entries')

    @pytest.mark.unit
    def test_add_entry(self, timeline):
        """Test adding entries to timeline."""
        timeline.add_entry('calm', 'appropriate', 0.8, 'Test event')

        assert len(timeline.entries) == 1
        entry = timeline.entries[0]
        assert entry.emotional_state == 'calm'
        assert entry.social_cue == 'appropriate'
        assert entry.confidence == 0.8
        assert entry.text == 'Test event'
        assert isinstance(entry.timestamp, float)

    @pytest.mark.unit
    def test_add_multiple_events(self, timeline):
        """Test adding multiple entries maintains order."""
        events = [
            ('calm', 'appropriate', 0.8, 'First'),
            ('engaged', 'appropriate', 0.9, 'Second'),
            ('elevated', 'interrupting', 0.7, 'Third')
        ]

        for state, cue, conf, desc in events:
            timeline.add_entry(state, cue, conf, desc)

        assert len(timeline.entries) == 3

        # Check order is maintained (chronological)
        assert timeline.entries[0].text == 'First'
        assert timeline.entries[1].text == 'Second'
        assert timeline.entries[2].text == 'Third'

    @pytest.mark.unit
    def test_get_recent_events(self, timeline):
        """Test getting recent entries."""
        # Add entries
        for i in range(5):
            timeline.add_entry('calm', 'appropriate', 0.8, f'Event {i}')

        recent = timeline.get_recent_entries(10)  # 10 minutes
        assert len(recent) <= 5

        # Should return TimelineEntry objects
        if recent:
            assert hasattr(recent[0], 'emotional_state')
            assert hasattr(recent[0], 'timestamp')

    @pytest.mark.unit
    def test_get_recent_events_less_than_limit(self, timeline):
        """Test getting recent entries when fewer than limit exist."""
        timeline.add_entry('calm', 'appropriate', 0.8, 'Only event')

        recent = timeline.get_recent_entries(10)
        assert len(recent) == 1
        assert recent[0].text == 'Only event'

    @pytest.mark.unit
    def test_timeline_event_structure(self, timeline):
        """Test that entries have the correct structure."""
        timeline.add_entry('engaged', 'appropriate', 0.9, 'Test event', alert=True)

        entry = timeline.entries[0]
        assert hasattr(entry, 'timestamp')
        assert hasattr(entry, 'emotional_state')
        assert hasattr(entry, 'social_cue')
        assert hasattr(entry, 'confidence')
        assert hasattr(entry, 'text')
        assert hasattr(entry, 'alert')

        # Check values
        assert entry.emotional_state == 'engaged'
        assert entry.social_cue == 'appropriate'
        assert entry.confidence == 0.9
        assert entry.text == 'Test event'
        assert entry.alert == True

    @pytest.mark.unit
    def test_get_dominant_state(self, timeline):
        """Test getting dominant emotional state."""
        # Add entries with different states
        timeline.add_entry('calm', 'appropriate', 0.8, 'Event 1')
        timeline.add_entry('calm', 'appropriate', 0.9, 'Event 2')
        timeline.add_entry('elevated', 'interrupting', 0.7, 'Event 3')

        dominant_state, confidence = timeline.get_dominant_state()
        assert dominant_state == 'calm'  # Should be most frequent
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
