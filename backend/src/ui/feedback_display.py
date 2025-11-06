"""
Console-based feedback display for testing and headless environments
"""

from typing import Dict


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
    display.update_pace(
        185, {"icon": "🐇", "level": "too_fast", "message": "Speaking too fast!"}
    )
    display.update_tone("supportive", 0.85, "🤝")
    display.update_filler_words({"um": 3, "like": 5})
    display.add_feedback(
        {
            "suggestion": "Great job being supportive! Try to reduce filler words.",
            "alert": False,
        }
    )

    print("\n\nSimulating problematic tone...")
    display.update_tone("dismissive", 0.78, "🙄")
    display.add_feedback(
        {
            "suggestion": "Your tone seems dismissive. Try to be more open.",
            "alert": True,
        }
    )
