"""
Teams Meeting Coach - Main Application (RealtimeSTT Version)
Provides real-time feedback on speaking pace, tone, and communication style
"""
import sys
import time
import threading
import argparse
from RealtimeSTT import AudioToTextRecorder
from analyzer import CommunicationAnalyzer
from feedback_display import FeedbackDisplay, SimpleFeedbackDisplay
from timeline import EmotionalTimeline
from colors import Colors, colorize_emotional_state, colorize_social_cue, colorize_alert
from dashboard import LiveDashboard
import config


class MeetingCoach:
    def __init__(self, use_menu_bar: bool = True, device_index: int = None):
        """
        Initialize the Meeting Coach system using RealtimeSTT.

        Args:
            use_menu_bar: Use menu bar app (True) or console output (False)
            device_index: Specific device index to use (for RealtimeSTT)
        """
        print("Initializing Teams Meeting Coach with RealtimeSTT...")

        # Initialize core components
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

        # Initialize RealtimeSTT (replaces AudioCapture + Transcriber + threading)
        print("🎤 Initializing RealtimeSTT recorder...")
        try:
            self.recorder = AudioToTextRecorder(
                model=config.WHISPER_MODEL,
                language="en",

                # Optimized VAD settings for continuous speech detection
                post_speech_silence_duration=0.3,  # Shorter silence before stopping
                min_length_of_recording=0.2,       # Minimum recording length
                min_gap_between_recordings=0.1,    # Smaller gap between recordings
                pre_recording_buffer_duration=0.3, # Buffer before speech starts

                # VAD sensitivity settings
                silero_sensitivity=0.6,             # Moderate sensitivity
                webrtc_sensitivity=2,               # Balanced WebRTC sensitivity

                # Disable features that might interfere
                enable_realtime_transcription=False,
                use_microphone=True,
                spinner=False,

                # Enable debug mode for troubleshooting
                debug_mode=True,

                # Add callbacks for monitoring
                on_recording_start=self._on_recording_start,
                on_recording_stop=self._on_recording_stop,
            )
            print("✅ RealtimeSTT recorder initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing RealtimeSTT: {e}")
            raise

        self.is_running = False
        self.is_listening = False
        self.last_wpm = 0
        self.animation_thread = None
        self.animation_stop_event = threading.Event()
        
        # Track speech timing for accurate WPM calculation
        self.speech_start_time = None
        self.speech_end_time = None

        print(f"✅ RealtimeSTT initialized with model: {config.WHISPER_MODEL}")

    def _on_recording_start(self):
        """Callback when RealtimeSTT starts recording"""
        print("🎤 Recording started...")
        self.is_listening = True
        self.speech_start_time = time.time()

    def _on_recording_stop(self):
        """Callback when RealtimeSTT stops recording"""
        print("🎤 Recording stopped...")
        self.is_listening = False
        self.speech_end_time = time.time()

    def _animation_worker(self):
        """Background thread to update listening animation"""
        while not self.animation_stop_event.wait(1.0):  # Update every 1 second (less aggressive)
            if self.is_running and self.is_listening:
                # Only advance animation if we're actively in listening state
                self.dashboard.set_listening_state(True)  # This advances animation
                # Update display less frequently to reduce flicker
                try:
                    self.dashboard.update_live_display(self.timeline)
                except Exception as e:
                    # Ignore display errors in background thread
                    pass

    def process_speech(self, text: str):
        """
        Process complete speech utterances from RealtimeSTT.
        This replaces the complex buffering and chunking logic.

        Args:
            text: Complete speech utterance detected by RealtimeSTT
        """
        if not text or len(text.strip()) < 3:
            # Even for short text, update dashboard to show activity
            self.dashboard.set_listening_state(False)
            self.dashboard.update_live_display(self.timeline)
            return

        word_count = len(text.split())

        # Calculate speaking pace using ACTUAL timing from RealtimeSTT callbacks
        if self.speech_start_time and self.speech_end_time:
            actual_duration = self.speech_end_time - self.speech_start_time
            # Use a minimum duration to avoid division by very small numbers
            actual_duration = max(actual_duration, 0.1)
            wpm = (word_count / actual_duration) * 60 if actual_duration > 0 else 0
            
            # Apply reasonable bounds to filter out obvious errors
            wpm = min(max(wpm, 30), 500)  # Between 30-500 WPM (wider range for real data)
        else:
            # Fallback to estimation if timing data not available
            estimated_seconds = max(1.0, word_count * 0.4)  # ~0.4 seconds per word (150 WPM)
            wpm = (word_count / estimated_seconds) * 60 if estimated_seconds > 0 else 0
            wpm = min(max(wpm, 50), 300)  # Between 50-300 WPM
        
        self.last_wpm = wpm

        print(f"🎙️ Detected speech: \"{text[:60]}{'...' if len(text) > 60 else ''}\" ({word_count} words, ~{wpm:.1f} WPM)")
        
        # Debug timing information
        if self.speech_start_time and self.speech_end_time:
            duration = self.speech_end_time - self.speech_start_time
            print(f"⏱️ Actual speech duration: {duration:.2f}s (real timing)")
        else:
            print("⏱️ Using estimated timing (no real duration available)")

        # Update pace feedback using transcriber's proper method
        pace_feedback = self._get_speaking_pace_feedback_dict(wpm)
        self.display.update_pace(wpm, pace_feedback)

        # Count filler words
        filler_counts = self._count_filler_words(text)
        if filler_counts:
            self.display.update_filler_words(filler_counts)

        # Only analyze if we have enough content
        if word_count >= config.MIN_WORDS_FOR_ANALYSIS:
            print(f"📝 Analyzing: {text[:50]}{'...' if len(text) > 50 else ''} ({word_count} words)")

            # Perform full LLM analysis
            tone_analysis = self.analyzer.analyze_tone(text)

            # Extract analysis fields
            emotional_state = tone_analysis.get('emotional_state', 'neutral')
            social_cues = tone_analysis.get('social_cues', 'appropriate')
            speech_pattern = tone_analysis.get('speech_pattern', 'normal')
            confidence = tone_analysis.get('confidence', 0.0)
            coaching_feedback = tone_analysis.get('coaching_feedback', tone_analysis.get('suggestions', ''))

            # Get appropriate emojis
            emotion_emoji = self.analyzer.get_emotional_state_emoji(emotional_state)
            social_emoji = self.analyzer.get_social_cue_emoji(social_cues)

            self.display.update_tone(emotional_state, confidence, emotion_emoji)

            # Enhanced alerting for autism/ADHD coaching
            emotional_alert = self.analyzer.should_alert(emotional_state, confidence)
            social_alert = self.analyzer.should_social_cue_alert(social_cues, confidence)

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

            # Add to timeline with full text
            self.timeline.add_entry(
                emotional_state=emotional_state,
                social_cue=social_cues,
                confidence=confidence,
                text=text,
                alert=emotional_alert or social_alert
            )

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
        else:
            # For short utterances, still update dashboard with basic info
            # AND add to timeline so it shows up in recent activity
            self.dashboard.update_current_status(
                emotional_state='neutral',
                social_cue='appropriate',
                confidence=0.0,
                text=text,
                coaching='',
                alert=False,
                wpm=wpm,
                filler_counts=filler_counts
            )

            # Add short utterances to timeline too (without LLM analysis)
            self.timeline.add_entry(
                emotional_state='neutral',
                social_cue='appropriate',
                confidence=0.0,
                text=text,
                alert=False
            )

        # Always clear listening state and update live dashboard display after processing
        self.dashboard.set_listening_state(False)
        self.dashboard.update_live_display(self.timeline)

    def _get_speaking_pace_feedback(self, wpm: float) -> str:
        """Get speaking pace feedback (replaces transcriber method)"""
        if wpm >= config.PACE_TOO_FAST:
            return "Too fast - slow down for clarity"
        elif wpm <= config.PACE_TOO_SLOW:
            return "Too slow - increase pace slightly"
        elif config.PACE_IDEAL_MIN <= wpm <= config.PACE_IDEAL_MAX:
            return "Perfect pace!"
        else:
            return "Good pace"

    def _get_speaking_pace_feedback_dict(self, wpm: float) -> dict:
        """Get speaking pace feedback as dictionary (consistent with transcriber method)"""
        if wpm > config.PACE_TOO_FAST:
            return {
                'level': 'too_fast',
                'category': 'fast',
                'message': f'Speaking too fast ({wpm:.1f} WPM). Try to slow down.',
                'icon': '🐇'
            }
        elif wpm < config.PACE_TOO_SLOW:
            return {
                'level': 'too_slow',
                'category': 'slow',
                'message': f'Speaking slowly ({wpm:.1f} WPM). Consider picking up the pace.',
                'icon': '🐢'
            }
        elif config.PACE_IDEAL_MIN <= wpm <= config.PACE_IDEAL_MAX:
            return {
                'level': 'ideal',
                'category': 'good',
                'message': f'Great pace! ({wpm:.1f} WPM)',
                'icon': '✅'
            }
        else:
            return {
                'level': 'normal',
                'category': 'good',
                'message': f'Pace: {wpm:.1f} WPM',
                'icon': '🎯'
            }

    def _count_filler_words(self, text: str) -> dict:
        """Count filler words (replaces transcriber method)"""
        text_lower = text.lower()
        filler_counts = {}

        for filler in config.FILLER_WORDS:
            count = text_lower.count(filler)
            if count > 0:
                filler_counts[filler] = count

        return filler_counts

    def run(self):
        """Start the meeting coach using RealtimeSTT."""
        # Collect initialization information to display
        initialization_info = {
            'audio_device': 'RealtimeSTT Auto-Selected',
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
            print("🚀 Starting RealtimeSTT audio processing...")
            print("🎤 Speak naturally - RealtimeSTT will detect speech boundaries automatically")
            print("🛑 Press Ctrl+C to stop")

            # Start animation thread for dynamic listening indicator
            self.animation_thread = threading.Thread(target=self._animation_worker, daemon=True)
            self.animation_thread.start()

            # Show initial dashboard state
            self.dashboard.update_live_display(self.timeline)

            # Use the correct RealtimeSTT pattern: continuous callback in loop
            while self.is_running:
                try:
                    # Set listening state before waiting for speech
                    self.dashboard.set_listening_state(True)
                    self.dashboard.update_live_display(self.timeline)

                    # Wait for speech - this blocks until complete speech utterance is detected
                    # Use the callback pattern
                    self.recorder.text(self.process_speech)

                    # Brief pause to prevent overwhelming the system
                    time.sleep(0.1)

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"⚠️ RealtimeSTT error: {e}")
                    time.sleep(0.5)  # Longer pause on error before retrying

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping Meeting Coach...")

        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources and show session summary."""
        print("🧹 Starting cleanup...")

        # Signal to stop the recording loop
        self.is_running = False

        # Stop animation thread
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_stop_event.set()
            self.animation_thread.join(timeout=1.0)

        # Clear listening state
        self.dashboard.set_listening_state(False)

        # RealtimeSTT cleanup - shutdown the recorder
        try:
            self.recorder.shutdown()
            print("✅ RealtimeSTT shut down")
        except Exception as e:
            print(f"⚠️ Error shutting down RealtimeSTT: {e}")

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


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Teams Meeting Coach - Real-time Communication Analysis")
    parser.add_argument(
        "--console",
        action="store_true",
        help="Use console output instead of menu bar"
    )
    parser.add_argument(
        "--device",
        type=int,
        help="Audio input device index to use"
    )

    args = parser.parse_args()

    # Create and run the meeting coach
    coach = MeetingCoach(
        use_menu_bar=not args.console,
        device_index=args.device
    )

    coach.run()


if __name__ == "__main__":
    main()
