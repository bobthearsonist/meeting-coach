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
    def test_format_emotional_state(self, dashboard):
        """Test emotional state formatting."""
        test_cases = [
            ('calm', '😌', '😌 Calm'),
            ('engaged', '😊', '😊 Engaged'),
            ('elevated', '😤', '😤 Elevated'),
            ('intense', '🔥', '🔥 Intense'),
            ('unknown', '❓', '❓ Unknown')
        ]
        
        for state, expected_emoji, expected_formatted in test_cases:
            result = dashboard.format_emotional_state(state)
            assert expected_emoji in result
            assert state.title() in result or state == 'unknown' and 'Unknown' in result
    
    @pytest.mark.unit
    def test_format_social_cue(self, dashboard):
        """Test social cue formatting."""
        test_cases = [
            ('appropriate', '✅', '✅ Appropriate'),
            ('interrupting', '⚠️', '⚠️ Interrupting'),
            ('dominating', '🚫', '🚫 Dominating'),
            ('withdrawn', '😶', '😶 Withdrawn'),
            ('unknown', '❓', '❓ Unknown')
        ]
        
        for cue, expected_emoji, expected_formatted in test_cases:
            result = dashboard.format_social_cue(cue)
            assert expected_emoji in result
            assert cue.title() in result or cue == 'unknown' and 'Unknown' in result
    
    @pytest.mark.unit 
    def test_update_dashboard_data_storage(self, dashboard, dashboard_scenarios):
        """Test that dashboard stores update data correctly."""
        scenario = dashboard_scenarios[0]
        
        dashboard.update(
            emotional_state=scenario['state'],
            social_cue=scenario['cue'], 
            confidence=scenario['confidence'],
            transcript=scenario['text'],
            coaching_tip=scenario['coaching'],
            alert=scenario['alert'],
            wpm=scenario['wpm']
        )
        
        # Check that data is stored
        assert dashboard.current_state['emotional_state'] == scenario['state']
        assert dashboard.current_state['social_cue'] == scenario['cue']
        assert dashboard.current_state['confidence'] == scenario['confidence']
        assert dashboard.current_state['transcript'] == scenario['text']
        assert dashboard.current_state['coaching_tip'] == scenario['coaching']
        assert dashboard.alert_active == scenario['alert']
        assert dashboard.current_state['wpm'] == scenario['wpm']

class TestEmotionalTimeline:
    """Test cases for EmotionalTimeline"""
    
    @pytest.fixture
    def timeline(self):
        """Create timeline instance for testing."""
        return EmotionalTimeline()
    
    @pytest.mark.unit
    def test_timeline_initialization(self, timeline):
        """Test timeline initializes correctly."""
        assert hasattr(timeline, 'events')
        assert isinstance(timeline.events, list)
        assert len(timeline.events) == 0
    
    @pytest.mark.unit
    def test_add_event(self, timeline):
        """Test adding events to timeline."""
        timeline.add_event('calm', 0.8, 'Test event')
        
        assert len(timeline.events) == 1
        event = timeline.events[0]
        assert event['state'] == 'calm'
        assert event['confidence'] == 0.8
        assert event['description'] == 'Test event'
        assert 'timestamp' in event
    
    @pytest.mark.unit
    def test_add_multiple_events(self, timeline):
        """Test adding multiple events maintains order."""
        events = [
            ('calm', 0.8, 'First'),
            ('engaged', 0.9, 'Second'), 
            ('elevated', 0.7, 'Third')
        ]
        
        for state, conf, desc in events:
            timeline.add_event(state, conf, desc)
        
        assert len(timeline.events) == 3
        
        # Check order is maintained (newest first)
        assert timeline.events[0]['description'] == 'Third'
        assert timeline.events[1]['description'] == 'Second'
        assert timeline.events[2]['description'] == 'First'
    
    @pytest.mark.unit
    def test_get_recent_events(self, timeline):
        """Test getting recent events."""
        # Add more events than the limit
        for i in range(15):
            timeline.add_event('calm', 0.8, f'Event {i}')
        
        recent = timeline.get_recent_events(5)
        assert len(recent) == 5
        
        # Should be most recent events
        assert recent[0]['description'] == 'Event 14'
        assert recent[4]['description'] == 'Event 10'
    
    @pytest.mark.unit
    def test_get_recent_events_less_than_limit(self, timeline):
        """Test getting recent events when fewer than limit exist."""
        timeline.add_event('calm', 0.8, 'Only event')
        
        recent = timeline.get_recent_events(5)
        assert len(recent) == 1
        assert recent[0]['description'] == 'Only event'
    
    @pytest.mark.unit
    def test_timeline_event_structure(self, timeline):
        """Test that events have the correct structure."""
        timeline.add_event('engaged', 0.9, 'Test event')
        
        event = timeline.events[0]
        required_keys = ['state', 'confidence', 'description', 'timestamp']
        
        for key in required_keys:
            assert key in event, f"Missing required key: {key}"
        
        assert isinstance(event['state'], str)
        assert isinstance(event['confidence'], (int, float))
        assert isinstance(event['description'], str)
        # timestamp should be a number (Unix timestamp)
        assert isinstance(event['timestamp'], (int, float))
    
    @pytest.mark.unit
    def test_clear_timeline(self, timeline):
        """Test clearing the timeline."""
        # Add some events
        for i in range(5):
            timeline.add_event('calm', 0.8, f'Event {i}')
        
        assert len(timeline.events) == 5
        
        timeline.clear()
        assert len(timeline.events) == 0