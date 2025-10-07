"""
Menu bar app for displaying live feedback
"""
import rumps
from typing import Dict, Optional
from collections import deque
from src import config


class FeedbackDisplay(rumps.App):
    def __init__(self):
        """Initialize menu bar app."""
        super(FeedbackDisplay, self).__init__(
            "Meeting Coach",
            icon=None,
            quit_button=None
        )
        
        # Store recent feedback
        self.feedback_history = deque(maxlen=config.FEEDBACK_HISTORY_SIZE)
        self.current_pace = "—"
        self.current_tone = "—"
        self.current_wpm = 0
        self.filler_count = {}
        self.is_recording = False
        
        # Build initial menu
        self._update_menu()
    
    def _update_menu(self):
        """Update the menu bar items."""
        self.menu.clear()
        
        # Status indicator
        status_icon = "🔴" if self.is_recording else "⚪️"
        self.menu.add(rumps.MenuItem(f"{status_icon} Status: {'Recording' if self.is_recording else 'Idle'}", 
                                     callback=None))
        self.menu.add(rumps.separator)
        
        # Current metrics
        self.menu.add(rumps.MenuItem(f"📊 Pace: {self.current_pace}", callback=None))
        self.menu.add(rumps.MenuItem(f"💬 Tone: {self.current_tone}", callback=None))
        
        if self.current_wpm > 0:
            self.menu.add(rumps.MenuItem(f"⏱️  {self.current_wpm:.0f} words/min", callback=None))
        
        # Filler words
        if self.filler_count:
            self.menu.add(rumps.separator)
            self.menu.add(rumps.MenuItem("Filler Words:", callback=None))
            for word, count in sorted(self.filler_count.items(), key=lambda x: x[1], reverse=True):
                self.menu.add(rumps.MenuItem(f"  '{word}': {count}x", callback=None))
        
        # Recent feedback
        if self.feedback_history:
            self.menu.add(rumps.separator)
            self.menu.add(rumps.MenuItem("Recent Feedback:", callback=None))
            for feedback in list(self.feedback_history)[-3:]:  # Show last 3
                suggestion = feedback.get('suggestion', '')
                if suggestion:
                    truncated = suggestion[:50] + "..." if len(suggestion) > 50 else suggestion
                    self.menu.add(rumps.MenuItem(f"  {truncated}", callback=None))
        
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Quit", callback=self.quit_app))
    
    def update_status(self, is_recording: bool):
        """Update recording status."""
        self.is_recording = is_recording
        self._update_menu()
    
    def update_pace(self, wpm: float, feedback: Dict[str, str]):
        """
        Update speaking pace display.
        
        Args:
            wpm: words per minute
            feedback: pace feedback dictionary with icon and level
        """
        self.current_wpm = wpm
        self.current_pace = f"{feedback['icon']} {wpm:.0f} WPM ({feedback['level']})"
        self._update_menu()
        
        # Show notification for concerning pace
        if feedback['level'] in ['too_fast', 'too_slow']:
            self._show_notification("Speaking Pace", feedback['message'])
    
    def update_tone(self, tone: str, confidence: float, emoji: str):
        """
        Update tone display.
        
        Args:
            tone: detected tone
            confidence: confidence level
            emoji: tone emoji
        """
        self.current_tone = f"{emoji} {tone.title()} ({confidence:.0%})"
        self._update_menu()
    
    def update_filler_words(self, filler_counts: Dict[str, int]):
        """
        Update filler word counts.
        
        Args:
            filler_counts: dictionary of filler word counts
        """
        # Accumulate counts
        for word, count in filler_counts.items():
            self.filler_count[word] = self.filler_count.get(word, 0) + count
        self._update_menu()
    
    def add_feedback(self, feedback: Dict[str, any]):
        """
        Add feedback to history.
        
        Args:
            feedback: feedback dictionary with suggestion and other metadata
        """
        self.feedback_history.append(feedback)
        self._update_menu()
        
        # Show notification for important feedback
        if feedback.get('alert', False):
            suggestion = feedback.get('suggestion', 'Consider adjusting your communication style')
            self._show_notification("Communication Feedback", suggestion)
    
    def reset_metrics(self):
        """Reset all metrics (for new meeting)."""
        self.feedback_history.clear()
        self.current_pace = "—"
        self.current_tone = "—"
        self.current_wpm = 0
        self.filler_count = {}
        self._update_menu()
    
    def _show_notification(self, title: str, message: str):
        """
        Show macOS notification.
        
        Args:
            title: notification title
            message: notification message
        """
        rumps.notification(
            title=title,
            subtitle="",
            message=message,
            sound=False
        )
    
    def quit_app(self, _):
        """Quit the application."""
        rumps.quit_application()


class SimpleFeedbackDisplay:
    """
    Simple console-based feedback display for testing without menu bar app.
    """
    def __init__(self):
        self.is_recording = False
        self.current_wpm = 0.0
        self.current_tone = ""
        self.filler_counts = {}
    
    def update_status(self, is_recording: bool):
        # Avoid extra prints in console mode; dashboard shows status
        self.is_recording = is_recording
    
    def update_pace(self, wpm: float, feedback: Dict[str, str]):
        # Dashboard reflects pace; keep state without printing
        self.current_wpm = wpm
    
    def update_tone(self, tone: str, confidence: float, emoji: str):
        # Dashboard reflects tone; avoid printing
        self.current_tone = tone
    
    def update_filler_words(self, filler_counts: Dict[str, int]):
        # Dashboard reflects filler words; retain counts without printing
        if filler_counts:
            for k, v in filler_counts.items():
                self.filler_counts[k] = self.filler_counts.get(k, 0) + v
    
    def add_feedback(self, feedback: Dict[str, any]):
        # Dashboard renders feedback; do not print to avoid scroll
        pass
    
    def reset_metrics(self):
        # No-op for console to avoid extra prints
        self.current_wpm = 0.0
        self.current_tone = ""
        self.filler_counts = {}


if __name__ == "__main__":
    print("Testing Feedback Display\n")
    
    # Use simple display for testing
    display = SimpleFeedbackDisplay()
    
    display.update_status(True)
    display.update_pace(185, {'icon': '🐇', 'level': 'too_fast', 'message': 'Speaking too fast!'})
    display.update_tone('supportive', 0.85, '🤝')
    display.update_filler_words({'um': 3, 'like': 5})
    display.add_feedback({
        'suggestion': 'Great job being supportive! Try to reduce filler words.',
        'alert': False
    })
    
    print("\n\nSimulating problematic tone...")
    display.update_tone('dismissive', 0.78, '🙄')
    display.add_feedback({
        'suggestion': 'Your tone seems dismissive. Try to be more open.',
        'alert': True
    })
