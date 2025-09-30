"""
Teams Meeting Coach - Main Application
Provides real-time feedback on speaking pace, tone, and communication style
"""
import sys
import time
import argparse
import numpy as np
from audio_capture import AudioCapture
from transcriber import Transcriber
from analyzer import CommunicationAnalyzer
from feedback_display import FeedbackDisplay, SimpleFeedbackDisplay
from timeline import EmotionalTimeline
from colors import Colors, colorize_emotional_state, colorize_social_cue, colorize_alert
from dashboard import LiveDashboard
import config


class MeetingCoach:
    def __init__(self, use_menu_bar: bool = True, device_index: int = None):
        """
        Initialize the Meeting Coach system.

        Args:
            use_menu_bar: Use menu bar app (True) or console output (False)
            device_index: Specific device index to use, overrides config
        """
        print("Initializing Teams Meeting Coach...")

        # Initialize components
        if config.USE_MICROPHONE_INPUT:
            selected_device = device_index if device_index is not None else config.MICROPHONE_DEVICE_INDEX
            self.audio_capture = AudioCapture(selected_device, use_microphone=True)
        else:
            self.audio_capture = AudioCapture(config.BLACKHOLE_DEVICE_INDEX, use_microphone=False)
        self.transcriber = Transcriber()
        self.analyzer = CommunicationAnalyzer()
        self.timeline = EmotionalTimeline(window_minutes=15, max_entries=200)
        self.dashboard = LiveDashboard()

        # Initialize display
        if use_menu_bar:
            try:
                self.display = FeedbackDisplay()
            except Exception as e:
                print(f"Could not initialize menu bar app: {e}")
                print("Falling back to console display")
                self.display = SimpleFeedbackDisplay()
        else:
            self.display = SimpleFeedbackDisplay()
        
        self.is_running = False
    
    def process_audio_chunk(self, audio_data):
        """
        Process a single audio chunk through the pipeline.
        
        Args:
            audio_data: numpy array of audio samples
        """
        # Transcribe
        transcription = self.transcriber.transcribe(audio_data)
        text = transcription['text']
        
        # Skip if no speech detected
        if not text or transcription['word_count'] < 3:
            return  # Dashboard will show activity status
        
        # Analyze speaking pace
        wpm = self.transcriber.calculate_wpm(
            transcription['word_count'],
            transcription['duration']
        )
        pace_feedback = self.transcriber.get_speaking_pace_feedback(wpm)
        self.display.update_pace(wpm, pace_feedback)
        
        # Count filler words
        filler_counts = self.transcriber.count_filler_words(text)
        if filler_counts:
            self.display.update_filler_words(filler_counts)
        
        # Analyze communication patterns (only if enough content)
        if transcription['word_count'] >= config.MIN_WORDS_FOR_ANALYSIS:
            tone_analysis = self.analyzer.analyze_tone(text)

            # Extract new analysis fields
            emotional_state = tone_analysis.get('emotional_state', 'neutral')
            social_cues = tone_analysis.get('social_cues', 'appropriate')
            speech_pattern = tone_analysis.get('speech_pattern', 'normal')
            confidence = tone_analysis.get('confidence', 0.0)
            coaching_feedback = tone_analysis.get('coaching_feedback', tone_analysis.get('suggestions', ''))

            # Get appropriate emojis
            emotion_emoji = self.analyzer.get_tone_emoji(emotional_state)
            social_emoji = self.analyzer.get_social_cue_emoji(social_cues)

            self.display.update_tone(emotional_state, confidence, emotion_emoji)

            # Enhanced alerting for autism/ADHD coaching
            emotional_alert = self.analyzer.should_alert(emotional_state, confidence)
            social_alert = self.analyzer.should_social_cue_alert(social_cues, confidence)

            # Add to timeline
            self.timeline.add_entry(
                emotional_state=emotional_state,
                social_cue=social_cues,
                confidence=confidence,
                text=text[:50],  # First 50 chars
                alert=emotional_alert or social_alert
            )

            # Update dashboard with current status
            self.dashboard.update_current_status(
                emotional_state=emotional_state,
                social_cue=social_cues,
                confidence=confidence,
                text=text,
                coaching=coaching_feedback,
                alert=emotional_alert or social_alert,
                wpm=wpm,
                filler_counts=filler_counts
            )

            # Update live dashboard display
            self.dashboard.update_live_display(self.timeline)

            # Create comprehensive feedback object
            feedback = {
                'text': text,
                'tone': emotional_state,
                'emotional_state': emotional_state,
                'social_cues': social_cues,
                'speech_pattern': speech_pattern,
                'confidence': confidence,
                'suggestion': coaching_feedback,
                'alert': emotional_alert or social_alert,
                'key_indicators': tone_analysis.get('key_indicators', [])
            }
            self.display.add_feedback(feedback)
    
    def run(self):
        """Start the meeting coach."""
        # Collect initialization information to display
        initialization_info = {
            'audio_device': self.audio_capture.get_device_name(self.audio_capture.device_index),
            'whisper_model': config.WHISPER_MODEL,
            'ollama_model': self.analyzer.model
        }
        
        # Initialize the live dashboard with initialization info
        self.dashboard.initialize_display(initialization_info)

        # Brief pause to show initialization
        time.sleep(2)
        
        self.display.update_status(True)
        self.is_running = True
        
        try:
            # Start audio capture stream
            for audio_chunk in self.audio_capture.capture_stream(config.CHUNK_DURATION):
                if not self.is_running:
                    break
                
                self.process_audio_chunk(audio_chunk)
        
        except KeyboardInterrupt:
            print("\n\nStopping Meeting Coach...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources and show session summary."""
        self.is_running = False
        self.display.update_status(False)

        # Restore terminal display before printing summary
        try:
            self.dashboard.restore_display()
        except Exception:
            # Fallback
            self.dashboard.clear_screen()

        print("="*70)
        print("📊 FINAL SESSION SUMMARY")
        print("="*70)

        # Show final timeline
        self.timeline.display_timeline(minutes=15, width=70)

        # Show session summary
        summary = self.timeline.get_session_summary()
        duration_min = summary.get('session_duration_minutes', 0)

        print(f"\n🕐 Session Duration: {duration_min:.1f} minutes")
        print(f"📝 Total Analyses: {summary.get('total_entries', 0)}")

        if summary.get('dominant_state'):
            dominant = summary['dominant_state']
            dominant_colored = colorize_emotional_state(dominant)
            print(f"🎯 Dominant State: {dominant_colored}")

        alert_count = summary.get('alert_count', 0)
        if alert_count > 0:
            alert_text = colorize_alert(f"{alert_count} coaching alerts", True)
            print(f"🚨 Alerts: {alert_text}")

        state_dist = summary.get('state_distribution', {})
        if state_dist:
            print(f"📈 State Distribution:")
            for state, count in sorted(state_dist.items(), key=lambda x: x[1], reverse=True):
                state_colored = colorize_emotional_state(state)
                percentage = (count / summary['total_entries']) * 100 if summary['total_entries'] > 0 else 0
                print(f"    {state_colored}: {count} times ({percentage:.1f}%)")

        print("\n" + "="*70)
        print("🎉 Great work on your emotional awareness during this session! 🧠")
        print("💡 Review the patterns above to understand your communication style")
        print("="*70)


def list_audio_devices():
    """List all available audio input devices."""
    print("Available Audio Input Devices:")
    print("=" * 50)

    # Create temporary capture to list devices
    temp_capture = AudioCapture(use_microphone=True)
    devices = []

    for i in range(temp_capture.audio.get_device_count()):
        device_info = temp_capture.audio.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            devices.append((i, device_info))

    # Sort devices by their actual index for cleaner display
    devices.sort(key=lambda x: x[0])

    # Display devices using their actual index as the number
    for device_index, device_info in devices:
        channels = device_info['maxInputChannels']
        sample_rate = int(device_info['defaultSampleRate'])
        print(f"{device_index:2d}. {device_info['name']} - {channels}ch, {sample_rate}Hz")

    del temp_capture

    if not devices:
        print("No input devices found!")
        return None

    print("\nTo use a specific device, run:")
    print("./run_with_venv.sh --device INDEX")
    print("\nFor example, to use the Yeti Stereo Microphone:")
    print("./run_with_venv.sh --device 5")
    return devices


def select_audio_device():
    """Interactive device selection."""
    devices = list_audio_devices()

    if not devices:
        return None

    # Create a mapping of device indices for easy lookup
    device_map = {device_index: device_info for device_index, device_info in devices}
    valid_indices = [str(device_index) for device_index, _ in devices]

    while True:
        try:
            choice = input(f"\nSelect device ({', '.join(valid_indices)}) or 'q' to quit: ").strip().lower()

            if choice == 'q':
                return None

            if choice.isdigit():
                device_index = int(choice)
                if device_index in device_map:
                    device_info = device_map[device_index]
                    print(f"Selected: {device_info['name']} (Index: {device_index})")
                    return device_index

            print(f"Please enter a valid device index ({', '.join(valid_indices)}) or 'q' to quit")
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled.")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="Teams Meeting Coach - Real-time meeting feedback"
    )
    parser.add_argument(
        '--console',
        action='store_true',
        help='Use console output instead of menu bar app'
    )
    parser.add_argument(
        '--test-audio',
        action='store_true',
        help='Test audio capture and list devices'
    )
    parser.add_argument(
        '--test-transcription',
        action='store_true',
        help='Test transcription with existing test_capture.wav'
    )
    parser.add_argument(
        '--select-device',
        action='store_true',
        help='List available audio input devices'
    )
    parser.add_argument(
        '--device',
        type=int,
        help='Specify audio device index to use'
    )
    
    args = parser.parse_args()
    
    # Test mode
    if args.test_audio:
        print("Testing audio capture...\n")
        if config.USE_MICROPHONE_INPUT:
            capture = AudioCapture(use_microphone=True)
            print("Testing MICROPHONE input (your speech will be analyzed)")
            print("Speak into your microphone during the test...")
        else:
            capture = AudioCapture(use_microphone=False)
            print("Testing BlackHole output (Teams audio will be analyzed)")

        capture.list_devices()

        print("\nCapturing 5 seconds of audio...")
        capture.start_capture()
        audio = capture.read_chunk(5.0)
        capture.stop_capture()

        print(f"Captured audio shape: {audio.shape}")
        print(f"Audio level (RMS): {np.sqrt(np.mean(audio**2)):.4f}")
        capture.save_chunk_to_wav(audio, "test_capture.wav")
        return
    
    if args.test_transcription:
        print("Testing transcription...\n")
        from transcriber import Transcriber
        import wave
        
        transcriber = Transcriber()
        
        try:
            with wave.open("test_capture.wav", 'rb') as wf:
                audio_bytes = wf.readframes(wf.getnframes())
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                
                result = transcriber.transcribe(audio_array)
                print(f"Transcription: {result['text']}")
                print(f"Word count: {result['word_count']}")
                
                wpm = transcriber.calculate_wpm(result['word_count'], result['duration'])
                print(f"Speaking pace: {wpm:.0f} WPM")
        except FileNotFoundError:
            print("test_capture.wav not found. Run with --test-audio first.")
        return

    # Device selection mode
    if args.select_device:
        list_audio_devices()
        return

    # Handle device specification
    selected_device_index = None
    if args.device is not None:
        selected_device_index = args.device
        print(f"Using specified device index: {selected_device_index}")
    elif config.USE_MICROPHONE_INPUT and config.MICROPHONE_DEVICE_INDEX is None:
        # Auto-prompt for device selection
        print("No microphone device configured. Please select one:\n")
        selected_device_index = select_audio_device()
        if selected_device_index is None:
            print("No device selected. Exiting.")
            return
        print(f"\nStarting Meeting Coach with device {selected_device_index}...\n")

    # Run meeting coach
    use_menu_bar = not args.console
    coach = MeetingCoach(use_menu_bar=use_menu_bar, device_index=selected_device_index)
    
    if use_menu_bar and isinstance(coach.display, FeedbackDisplay):
        # Run as menu bar app
        coach.display.run()
    else:
        # Run in console mode
        coach.run()


if __name__ == "__main__":
    main()
