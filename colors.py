"""
Color utilities for console output
"""
import sys
from typing import Dict

class Colors:
    """ANSI color codes for terminal output"""

    # Reset
    RESET = '\033[0m'

    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'

    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'

    @classmethod
    def is_supported(cls) -> bool:
        """Check if colors are supported in current terminal"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text if supported"""
        if not cls.is_supported():
            return text
        return f"{color}{text}{cls.RESET}"

def get_emotional_state_color(emotional_state: str) -> str:
    """Get color for emotional state"""
    color_map = {
        'calm': Colors.GREEN,
        'neutral': Colors.WHITE,
        'engaged': Colors.BRIGHT_YELLOW,
        'elevated': Colors.YELLOW,
        'intense': Colors.BRIGHT_RED,
        'rapid': Colors.BRIGHT_MAGENTA,
        'overwhelmed': Colors.RED,
        'distracted': Colors.DIM,
        'unknown': Colors.WHITE
    }
    return color_map.get(emotional_state.lower(), Colors.WHITE)

def get_social_cue_color(social_cue: str) -> str:
    """Get color for social cue"""
    color_map = {
        'appropriate': Colors.GREEN,
        'interrupting': Colors.BRIGHT_RED,
        'dominating': Colors.YELLOW,
        'too_quiet': Colors.DIM,
        'off_topic': Colors.MAGENTA,
        'repetitive': Colors.CYAN,
        'monotone': Colors.BLUE,
        'unknown': Colors.WHITE
    }
    return color_map.get(social_cue.lower(), Colors.WHITE)

def get_alert_color(is_alert: bool) -> str:
    """Get color for alerts"""
    return Colors.BRIGHT_RED if is_alert else Colors.GREEN

def colorize_emotional_state(emotional_state: str) -> str:
    """Return colorized emotional state text"""
    color = get_emotional_state_color(emotional_state)
    return Colors.colorize(emotional_state, color)

def colorize_social_cue(social_cue: str) -> str:
    """Return colorized social cue text"""
    color = get_social_cue_color(social_cue)
    return Colors.colorize(social_cue, color)

def colorize_alert(text: str, is_alert: bool) -> str:
    """Return colorized alert text"""
    color = get_alert_color(is_alert)
    return Colors.colorize(text, color)

if __name__ == "__main__":
    # Test colors
    print("Testing color support...")
    print(f"Colors supported: {Colors.is_supported()}")

    print("\nEmotional States:")
    states = ['calm', 'elevated', 'intense', 'overwhelmed']
    for state in states:
        colored = colorize_emotional_state(state)
        print(f"  {colored}")

    print("\nSocial Cues:")
    cues = ['appropriate', 'interrupting', 'dominating', 'too_quiet']
    for cue in cues:
        colored = colorize_social_cue(cue)
        print(f"  {colored}")

    print("\nAlerts:")
    print(f"  {colorize_alert('ALERT', True)}")
    print(f"  {colorize_alert('OK', False)}")