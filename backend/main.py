"""
Teams Meeting Coach - Main Application (WebSocket Version)
The backend always runs as a WebSocket server broadcasting updates.
The console dashboard is now a WebSocket client that displays the updates.

Usage:
    python main.py              # Starts WebSocket server + integrated engine
    python console_client.py    # Connect console dashboard (separate terminal)
"""

import argparse
import logging
import os
import sys
import threading
import time
import warnings

# Suppress ctranslate2 float16 warnings
os.environ["CT2_VERBOSE"] = "0"
logging.getLogger("ctranslate2").setLevel(logging.ERROR)

# Suppress RealtimeSTT EOFError warnings during shutdown
# These occur when multiprocessing connections are closed during cleanup
logging.getLogger("root").setLevel(logging.CRITICAL)

warnings.filterwarnings("ignore", message=".*float16.*")
warnings.filterwarnings("ignore", message=".*compute type.*")

from RealtimeSTT import AudioToTextRecorder
from src import config
from src.core.analyzer import CommunicationAnalyzer
from src.server.ws_server import MeetingCoachWebSocketServer
from src.ui.colors import colorize_alert, colorize_emotional_state, colorize_social_cue
from src.ui.timeline import EmotionalTimeline


class MeetingCoach:
    def __init__(
        self, ws_server: MeetingCoachWebSocketServer, device_index: int = None
    ):
        """
        Initialize the Meeting Coach system with WebSocket broadcasting.

        Args:
            ws_server: WebSocket server instance for broadcasting updates
            device_index: Specific device index to use (for RealtimeSTT)
        """
        # Import here to avoid loading dependencies for API-only mode
        from RealtimeSTT import AudioToTextRecorder
        from src.core.analyzer import CommunicationAnalyzer
        from src.ui.timeline import EmotionalTimeline
        
        print("Initializing Teams Meeting Coach WebSocket Engine...")

        # WebSocket server reference
        self.ws_server = ws_server
        self.session_start_time = time.time()

        # Initialize core components
        self.analyzer = CommunicationAnalyzer()
        self.timeline = EmotionalTimeline(window_minutes=15, max_entries=200)

        # Initialize RealtimeSTT
        print("🎤 Initializing RealtimeSTT recorder...")
        try:
            self.recorder = AudioToTextRecorder(
                model=config.WHISPER_MODEL,
                language="en",
                # Optimized VAD settings for continuous speech detection
                post_speech_silence_duration=0.3,  # Shorter silence before stopping
                min_length_of_recording=0.2,  # Minimum recording length
                min_gap_between_recordings=0.1,  # Smaller gap between recordings
                pre_recording_buffer_duration=0.3,  # Buffer before speech starts
                # VAD sensitivity settings
                silero_sensitivity=0.6,  # Moderate sensitivity
                webrtc_sensitivity=2,  # Balanced WebRTC sensitivity
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

        print(f"✅ Meeting Coach initialized with model: {config.WHISPER_MODEL}")

    def _on_recording_start(self):
        """Callback when RealtimeSTT starts recording"""
        print("🎤 Recording started...")
        self.is_listening = True

        # Broadcast listening status
        self.broadcast_update({"type": "recording_status", "is_listening": True})

    def _on_recording_stop(self):
        """Callback when RealtimeSTT stops recording"""
        print("🎤 Recording stopped...")
        self.is_listening = False

        # Broadcast listening status
        self.broadcast_update({"type": "recording_status", "is_listening": False})

    def broadcast_update(self, data: dict):
        """Broadcast update to all connected WebSocket clients"""
        data["timestamp"] = time.time()
        self.ws_server.broadcast_sync(data)

    def process_speech(self, text: str):
        """
        Process complete speech utterances from RealtimeSTT.
        Broadcasts all updates via WebSocket to connected clients.

        Args:
            text: Complete speech utterance detected by RealtimeSTT
        """
        if not text or len(text.strip()) < 3:
            return

        word_count = len(text.split())

        # Calculate speaking pace
        estimated_seconds = max(
            1.0, word_count * 0.4
        )  # ~0.4 seconds per word (150 WPM)
        wpm = (word_count / estimated_seconds) * 60 if estimated_seconds > 0 else 0
        wpm = min(max(wpm, 50), 300)  # Cap between 50-300 WPM
        self.last_wpm = wpm

        print(
            f"🎙️ Detected speech: \"{text[:60]}{'...' if len(text) > 60 else ''}\" ({word_count} words, ~{wpm:.0f} WPM)"
        )

        # Count filler words
        filler_counts = self._count_filler_words(text)

        # Broadcast transcription immediately
        self.broadcast_update(
            {
                "type": "transcription",
                "text": text,
                "wpm": wpm,
                "word_count": word_count,
                "filler_counts": filler_counts,
            }
        )

        # Check speaking pace for alerts
        pace_feedback = self._get_speaking_pace_feedback(wpm)
        if "Too" in pace_feedback or "slow" in pace_feedback.lower():
            self.broadcast_update(
                {
                    "type": "alert",
                    "message": pace_feedback,
                    "severity": "warning",
                    "category": "pace",
                }
            )

        # Only analyze if we have enough content
        if word_count >= config.MIN_WORDS_FOR_ANALYSIS:
            print(
                f"📝 Analyzing: {text[:50]}{'...' if len(text) > 50 else ''} ({word_count} words)"
            )

            # Perform full LLM analysis
            tone_analysis = self.analyzer.analyze_tone(text)

            # Extract analysis fields
            emotional_state = tone_analysis.get("emotional_state", "neutral")
            social_cues = tone_analysis.get("social_cues", "appropriate")
            speech_pattern = tone_analysis.get("speech_pattern", "normal")
            confidence = tone_analysis.get("confidence", 0.0)
            coaching_feedback = tone_analysis.get(
                "coaching_feedback", tone_analysis.get("suggestions", "")
            )

            # Enhanced alerting for autism/ADHD coaching
            emotional_alert = self.analyzer.should_alert(emotional_state, confidence)
            social_alert = self.analyzer.should_social_cue_alert(
                social_cues, confidence
            )

            # Add to timeline
            self.timeline.add_entry(
                emotional_state=emotional_state,
                social_cue=social_cues,
                confidence=confidence,
                text=text,
                alert=emotional_alert or social_alert,
            )

            # Broadcast emotional state update
            self.broadcast_update(
                {
                    "type": "emotion_update",
                    "emotional_state": emotional_state,
                    "confidence": confidence,
                }
            )

            # Broadcast full meeting update
            self.broadcast_update(
                {
                    "type": "meeting_update",
                    "emotional_state": emotional_state,
                    "social_cue": social_cues,
                    "confidence": confidence,
                    "wpm": wpm,
                    "text": text,
                    "coaching": coaching_feedback,
                    "alert": emotional_alert or social_alert,
                    "filler_counts": filler_counts,
                    "speech_pattern": speech_pattern,
                }
            )

            # Broadcast alerts if needed
            if emotional_alert:
                self.broadcast_update(
                    {
                        "type": "alert",
                        "message": f"Emotional state: {emotional_state.upper()} - {coaching_feedback}",
                        "severity": "warning",
                        "category": "emotional",
                        "emotional_state": emotional_state,
                    }
                )

            if social_alert:
                self.broadcast_update(
                    {
                        "type": "alert",
                        "message": f"Social cue alert: {social_cues}",
                        "severity": "warning",
                        "category": "social",
                        "social_cue": social_cues,
                    }
                )

        else:
            # For short utterances, broadcast basic update
            self.timeline.add_entry(
                emotional_state="neutral",
                social_cue="appropriate",
                confidence=0.0,
                text=text,
                alert=False,
            )

            self.broadcast_update(
                {
                    "type": "meeting_update",
                    "emotional_state": "neutral",
                    "social_cue": "appropriate",
                    "confidence": 0.0,
                    "wpm": wpm,
                    "text": text,
                    "coaching": "",
                    "alert": False,
                    "filler_counts": filler_counts,
                }
            )

        # Broadcast timeline summary
        self._broadcast_timeline_summary()

    def _broadcast_timeline_summary(self):
        """Broadcast current timeline summary"""
        summary = self.timeline.get_session_summary()
        recent_entries = self.timeline.get_recent_entries(10)

        # Convert timeline entries to serializable format
        timeline_data = []
        for entry in recent_entries:
            timeline_data.append(
                {
                    "emotional_state": entry.emotional_state,
                    "social_cue": entry.social_cue,
                    "confidence": entry.confidence,
                    "text": entry.text,
                    "alert": entry.alert,
                    "timestamp": entry.timestamp,
                }
            )

        self.broadcast_update(
            {
                "type": "timeline_update",
                "summary": summary,
                "recent_entries": timeline_data,
            }
        )

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
        """Start the meeting coach with WebSocket broadcasting."""
        print("🚀 Starting Meeting Coach WebSocket Engine...")
        print("🎤 Speak naturally - RealtimeSTT will detect speech automatically")
        print("📡 Broadcasting updates to all connected clients")
        print("💡 Open console_client.py in another terminal to see the dashboard")
        print("🛑 Press Ctrl+C to stop")

        # Broadcast session start
        self.broadcast_update(
            {
                "type": "session_status",
                "status": "started",
                "message": "Meeting coach session started",
                "config": {
                    "whisper_model": config.WHISPER_MODEL,
                    "ollama_model": self.analyzer.model,
                },
            }
        )

        self.is_running = True
        self.session_start_time = time.time()

        try:
            # Use the continuous RealtimeSTT pattern
            while self.is_running:
                try:
                    # Wait for speech - blocks until complete speech utterance is detected
                    self.recorder.text(self.process_speech)

                    # Brief pause to prevent overwhelming the system
                    time.sleep(0.1)

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"⚠️ RealtimeSTT error: {e}")
                    self.broadcast_update(
                        {"type": "error", "message": f"Processing error: {str(e)}"}
                    )
                    time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping Meeting Coach...")

        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources and broadcast session summary."""
        print("🧹 Starting cleanup...")

        self.is_running = False

        # RealtimeSTT cleanup
        try:
            self.recorder.shutdown()
            print("✅ RealtimeSTT shut down")
        except Exception as e:
            print(f"⚠️ Error shutting down RealtimeSTT: {e}")

        # Broadcast final session summary
        summary = self.timeline.get_session_summary()
        session_duration = time.time() - self.session_start_time

        self.broadcast_update(
            {
                "type": "session_status",
                "status": "stopped",
                "message": "Meeting coach session ended",
                "summary": summary,
                "duration_seconds": session_duration,
            }
        )

        print("=" * 70)
        print("� SESSION COMPLETE")
        print("=" * 70)
        print(f"🕐 Duration: {session_duration/60:.1f} minutes")
        print(f"📝 Total Analyses: {summary.get('total_entries', 0)}")
        print(f"🚨 Alerts: {summary.get('alert_count', 0)}")
        if summary.get("dominant_state"):
            dominant = summary["dominant_state"]
            dominant_colored = colorize_emotional_state(dominant)
            print(f"� Dominant State: {dominant_colored}")
        print("=" * 70)


def main():
    """Main entry point - starts WebSocket server with MeetingCoach engine"""
    parser = argparse.ArgumentParser(
        description="Teams Meeting Coach - WebSocket Server"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help=f"WebSocket server host (default: {config.WEBSOCKET_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=f"WebSocket server port (default: {config.WEBSOCKET_PORT})",
    )
    parser.add_argument("--device", type=int, help="Audio input device index to use")

    args = parser.parse_args()

    # Create WebSocket server (will use config defaults if args are None)
    ws_server = MeetingCoachWebSocketServer(host=args.host, port=args.port)

    print("🧠 Teams Meeting Coach - WebSocket Server")
    print("=" * 70)
    print(f"📡 Starting WebSocket server on ws://{ws_server.host}:{ws_server.port}")
    print(
        f"💡 Connect clients with: python -m src.server.console_client --url ws://{ws_server.host}:{ws_server.port}"
    )
    print("=" * 70)

    # Create Meeting Coach engine
    coach = MeetingCoach(ws_server=ws_server, device_index=args.device)

    args = parser.parse_args()
    
    if args.api_only:
        # Run only the REST API server
        print("Starting REST API server only...")
        from src.server.api_server import app
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=args.api_port)
    else:
        # Import WebSocket dependencies only when needed
        from src.server.ws_server import MeetingCoachWebSocketServer
        
        # Run WebSocket server (existing behavior)
        # Create WebSocket server (will use config defaults if args are None)
        ws_server = MeetingCoachWebSocketServer(host=args.host, port=args.port)

        print("🧠 Teams Meeting Coach - WebSocket Server")
        print("=" * 70)
        print(f"📡 Starting WebSocket server on ws://{ws_server.host}:{ws_server.port}")
        print(f"💡 Connect clients with: python -m src.server.console_client --url ws://{ws_server.host}:{ws_server.port}")
        print("=" * 70)

        # Create Meeting Coach engine
        coach = MeetingCoach(
            ws_server=ws_server,
            device_index=args.device
        )

        # Run WebSocket server in background thread
        server_thread = threading.Thread(target=ws_server.run, daemon=True)
        server_thread.start()

        # Give server time to start
        time.sleep(2)

        # Run the meeting coach engine (blocking)
        try:
            coach.run()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
